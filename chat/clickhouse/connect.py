import clickhouse_connect
from clickhouse_connect.driver.httpclient import Client
from dataclasses import dataclass,asdict
from typing import List,Dict,Optional


@dataclass
class TableColumn:
    name: str
    ch_type: str


@dataclass
class TableSchema:
    name: str
    columns: List[TableColumn]


@dataclass
class DatabaseSchema:
    tables: Dict[str, TableSchema]

class CLICKHOUSE:
    def __init__(self):
        self.client:Optional[Client] = None

    def connect(self,host:str,port:int,username:str,password:str)->Client: 
        try:
            self.client = clickhouse_connect.get_client(host=host,
                                                        port=port,
                                                        username=username,
                                                        password=password
                                                        )
            return self.client
        except Exception as e:
            raise e
    
    def extract_clickhouse_schema(self):
        if not self.client:
            raise ValueError("Connect to a clickhouse server first.")
        rows = self.client.query(
                            """
                            SELECT database, name
                            FROM system.tables
                            WHERE database = 'JARVIS_DB'
                                AND (
                                    name ILIKE 'zoho%_d' 
                                    OR name ILIKE 'DEVOPS%'
                                    )
                            ORDER BY name
                            """
                            ).result_rows


        tables: Dict[str, TableSchema] = {}
        for (db, name) in rows:
            cols = self.client.query(
            f"""
            SELECT name, type
            FROM system.columns
            WHERE database = 'JARVIS_DB' AND table = '{name}'
            ORDER BY position
            """
            ).result_rows
            tables[name] = TableSchema(name=name, columns=[TableColumn(name=c[0], ch_type=c[1]) for c in cols])


        return asdict(DatabaseSchema(tables=tables))
