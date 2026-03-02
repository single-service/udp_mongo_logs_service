import asyncio
from datetime import datetime
import logging

from db_interfaces.base import StorageInterface

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("info")


class PostgresStorage(StorageInterface):

    def __init__(self, conn, is_async: bool):
        self.conn = conn
        self.is_async = is_async
        
    async def init_table(self):
        """Создание таблицы с нужными колонками и индексом на created_dt"""
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS logs (
            uuid TEXT,
            created_dt TIMESTAMP(3),
            pathname TEXT,
            funcName TEXT,
            lineno INTEGER,
            message TEXT,
            exc_text TEXT,
            created DOUBLE PRECISION,
            filename TEXT,
            levelname TEXT,
            levelno TEXT,
            module TEXT,
            msecs DOUBLE PRECISION,
            msg TEXT,
            name TEXT,
            process TEXT,
            processName TEXT,
            relativeCreated TEXT,
            stack_info TEXT,
            thread TEXT,
            threadName TEXT,
            server_name TEXT
        );
        """

        create_index_sql = f"""
        CREATE INDEX IF NOT EXISTS idx_logs_created_dt
        ON logs (created_dt);
        """

        if self.is_async:
            await self.conn.execute(create_table_sql)
            await self.conn.execute(create_index_sql)
        else:
            await asyncio.to_thread(self.__init_table_sync, create_table_sql, create_index_sql)
            
            
    def __init_table_sync(self, create_table_sql, create_index_sql):
        cur = self.conn.cursor()
        try:
            cur.execute(create_table_sql)
            cur.execute(create_index_sql)
            self.conn.commit()
        finally:
            cur.close()

    async def insert(self, collection, data):
        if self.is_async:
            await self.conn.execute(
                f"""
                INSERT INTO {collection} (
                    uuid, created_dt, pathname, funcName, lineno, message,
                    exc_text, created, filename, levelname, levelno, module,
                    msecs, msg, name, process, processName, relativeCreated,
                    stack_info, thread, threadName, server_name
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
                    $13, $14, $15, $16, $17, $18, $19, $20, $21, $22
                )
                """,
                *[
                    data.get("uuid"),
                    datetime.fromisoformat(data.get("created_dt")),
                    data.get("pathname"),
                    data.get("funcName"),
                    data.get("lineno"),
                    data.get("message"),
                    data.get("exc_text"),
                    data.get("created"),
                    data.get("filename"),
                    data.get("levelname"),
                    data.get("levelno"),
                    data.get("module"),
                    data.get("msecs"),
                    data.get("msg"),
                    data.get("name"),
                    data.get("process"),
                    data.get("processName"),
                    data.get("relativeCreated"),
                    data.get("stack_info"),
                    data.get("thread"),
                    data.get("threadName"),
                    data.get("server_name"),
                ],
            )
        else:
            await asyncio.to_thread(
                self._insert_sync,
                collection,
                data
            )

    def _insert_sync(self, collection, data):
        cur = self.conn.cursor()
        try:
            cur.execute(
                f"""
                INSERT INTO {collection} (
                    uuid, created_dt, pathname, funcName, lineno, message,
                    exc_text, created, filename, levelname, levelno, module,
                    msecs, msg, name, process, processName, relativeCreated,
                    stack_info, thread, threadName, server_name
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                [
                    data.get("uuid"),
                    data.get("created_dt"),
                    data.get("pathname"),
                    data.get("funcName"),
                    data.get("lineno"),
                    data.get("message"),
                    data.get("exc_text"),
                    data.get("created"),
                    data.get("filename"),
                    data.get("levelname"),
                    data.get("levelno"),
                    data.get("module"),
                    data.get("msecs"),
                    data.get("msg"),
                    data.get("name"),
                    data.get("process"),
                    data.get("processName"),
                    data.get("relativeCreated"),
                    data.get("stack_info"),
                    data.get("thread"),
                    data.get("threadName"),
                    data.get("server_name"),
                ],
            )
            self.conn.commit()
        finally:
            cur.close()
            
    async def clean_logs(self, retention_days: int):
        """Удаляет логи старше retention_days по created_dt."""
        
        delete_sql = f"""
            DELETE FROM logs
            WHERE created_dt < NOW() - INTERVAL '{retention_days} days';
        """

        if self.is_async:
            await self.conn.execute(delete_sql)
        else:
            await asyncio.to_thread(self._clean_logs_sync, delete_sql)

        logger.info(
            f"[{datetime.now()}] Logs older than {retention_days} days deleted."
        )
        
    def _clean_logs_sync(self, delete_sql):
        cur = self.conn.cursor()
        try:
            cur.execute(delete_sql)
            self.conn.commit()
        finally:
            cur.close()
