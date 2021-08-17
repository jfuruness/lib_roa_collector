from lib_database import GenericTable


class ROAsTable(GenericTable):
    """ROAs Table"""

    name = "roas"
    id_col = None

    def create_table(self):
        """Creates ROAs Table"""

        sql = f"""CREATE UNLOGGED TABLE IF NOT EXISTS {self.name} (
              uri TEXT,
              asn BIGINT,
              prefix CIDR,
              max_length INTEGER,
              not_before TIMESTAMP,
              not_after TIMESTAMP
              );"""
        self.execute(sql)
