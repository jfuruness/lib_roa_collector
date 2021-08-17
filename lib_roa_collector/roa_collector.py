import csv
from datetime import datetime, timedelta
from multiprocessing import cpu_count
import os
import re

from lib_utils.file_funcs import makedirs, download_file
from lib_utils.helper_funcs import get_hrefs, run_cmds, mp_call

from .tables import ROAsTable

class ROACollector:
    """Downloads ROAs from ripe"""

    url = "https://ftp.ripe.net/rpki/"

    def __init__(self, base_roa_path="/ssd/roas"):
        """Initializes ROA path"""

        self.base_roa_path = base_roa_path
        makedirs(base_roa_path, remake=True)
        self.tsv_path = os.path.join(base_roa_path, "roas.tsv")

    def run(self, dl_time=datetime.utcnow() - timedelta(days=2),
            dl_cpus=cpu_count() * 4,
            database=True):
        """Gets URLs, downloads files, and concatenates them"""

        # Get URLs and paths
        urls = self._get_urls(dl_time)
        paths = self._get_paths(urls)
        # Download all files with multiprocessing
        mp_call(download_file, [urls, paths], "Downloading", cpus=dl_cpus)
        # Extract data to the tsv_path
        self._extract_data()
        # Insert info into the db
        if database:
            with ROAsTable(clear=True) as db:
                db.bulk_insert_tsv(self.tsv_path)

    def _get_urls(self, dl_time):
        """Gets URLs to all the ROA CSVs"""

        # Get URLs of Tals
        tal_urls = [self.url + x for x in get_hrefs(self.url) if ".tal" in x]
        # https://ftp.ripe.net/rpki/afrinic.tal/2021/08/16/roas.csv
        return [dl_time.strftime(f"{x}/%Y/%m/%d/roas.csv") for x in tal_urls]
 
    def _get_paths(self, urls):
        """Gets all paths from the URLs for downloading"""

        paths = []
        for url in urls:
            # Get name of tal
            tal = re.findall("rpki/(.+).tal/", url)[0]
            # Get download path
            paths.append(os.path.join(self.base_roa_path, f"{tal}.csv"))
        return paths

    def _extract_data(self):
        """Extracts data and adds it to the TSV path"""

        rows = []
        # Done this way because many links are broken, so paths are empty
        for fname in os.listdir(self.base_roa_path):
            path = os.path.join(self.base_roa_path, fname)
            with open(path, "r") as f:
                for row in csv.DictReader(f):
                    # Get rid of quotes
                    new_row = {"uri": row["URI"][1:-1],
                               # Get rid of AS in front of ASN
                               "asn": row["ASN"][2:],
                               # Replaace bad key names
                               "prefix": row["IP Prefix"],
                               "max_length": row["Max Length"],
                               "not_before": row["Not Before"],
                               "not_after": row["Not After"]}
                    rows.append(new_row)
        # Write to file
        with open(self.tsv_path, "w") as f:
            csv.DictWriter(f, new_row.keys(), delimiter="\t").writerows(rows)
