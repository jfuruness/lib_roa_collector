import csv
from datetime import datetime, timedelta
from multiprocessing import cpu_count
import os
import re

from lib_utils.base_classes import Base
from lib_utils.file_funcs import download_file
from lib_utils.helper_funcs import get_hrefs, run_cmds

from .tables import ROAsTable

class ROACollector(Base):
    """Downloads ROAs from ripe"""

    url = "https://ftp.ripe.net/rpki/"

    def run(self):
        """Gets URLs, downloads files, and concatenates them"""

        # Get URLs and paths
        urls = self._get_urls()
        paths = self._get_paths(urls)
        # Download all files with multiprocessing
        self.download_mp(download_file, [urls, paths])
        # Extract data to the tsv_path
        self._extract_data()

    def _get_urls(self):
        """Gets URLs to all the ROA CSVs"""

        # Get URLs of Tals
        urls = [self.url + x for x in get_hrefs(self.url) if ".tal" in x]
        # https://ftp.ripe.net/rpki/afrinic.tal/2021/08/16/roas.csv
        return [self.dl_time.strftime(f"{x}/%Y/%m/%d/roas.csv") for x in urls]

    def _get_paths(self, urls):
        """Gets all paths from the URLs for downloading"""

        paths = []
        for url in urls:
            # Get name of tal
            tal = re.findall("rpki/(.+).tal/", url)[0]
            # Get download path
            paths.append(self.dir_ / f"{tal}.csv")
        return paths

    def _extract_data(self):
        """Extracts data and adds it to the TSV path"""

        rows = []
        # Done this way because many links are broken, so paths are empty
        for fname in os.listdir(self.dir_):
            if ".csv" not in fname:
                continue
            tal = fname.replace(".csv", "")
            path = self.dir_ / fname
            with path.open(mode="r") as f:
                for row in csv.DictReader(f):
                    # Don't start and end 1 early for URI - this cuts off data
                    new_row = {"uri": row["URI"],
                               # Get rid of AS in front of ASN
                               "asn": row["ASN"][2:],
                               # Replaace bad key names
                               "prefix": row["IP Prefix"],
                               "max_length": row["Max Length"],
                               "not_before": row["Not Before"],
                               "not_after": row["Not After"],
                               "tal": tal}
                    rows.append(new_row)
        # Write to file
        with self.tsv_path.open(mode="w") as f:
            writer = csv.DictWriter(f, new_row.keys(), delimiter="\t")
            writer.writeheader()
            writer.writerows(rows)
