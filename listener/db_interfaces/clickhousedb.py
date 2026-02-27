import asyncio

from listener.db_interfaces.base import StorageInterface

class ClickHouseStorage(StorageInterface):

    def __init__(self, client, db_name: str):
        self.client = client
        self.db_name = db_name
        self.table_name = f"{self.db_name}.logs"
        
    def init_table(self):
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {self.table_name}
        (
            uuid String,
            created_dt DateTime64(3),
            pathname Nullable(String),
            funcName Nullable(String),
            lineno Nullable(Int32),
            message Nullable(String),
            exc_text Nullable(String),
            created Nullable(Float64),
            filename Nullable(String),
            levelname Nullable(String),
            levelno Nullable(String),
            module Nullable(String),
            msecs Nullable(Float64),
            msg Nullable(String),
            name Nullable(String),
            process Nullable(String),
            processName Nullable(String),
            relativeCreated Nullable(String),
            stack_info Nullable(String),
            thread Nullable(String),
            threadName Nullable(String),
            server_name Nullable(String)
        )
        ENGINE = MergeTree()
        PARTITION BY toDate(created_dt)
        ORDER BY (created_dt)
        SETTINGS min_bytes_for_wide_part = 0;
        """
        asyncio.to_thread(self.__init_table_sync, create_table_sql)
        
    def __init_table_sync(self, create_table_sql):
        self.client.execute(create_table_sql)

    async def insert(self, collection, data):
        await asyncio.to_thread(self._insert_sync, collection, data)

    def _insert_sync(self, collection, data):
        columns = list(data.keys())
        values = [list(data.values())]

        self.client.execute(
            f"INSERT INTO {collection} ({', '.join(columns)}) VALUES",
            values,
        )
