import asyncio
from datetime import datetime, timedelta, timezone
import logging

from db_interfaces.base import StorageInterface

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("info")

class MongoStorage(StorageInterface):

    def __init__(self, db, is_async: bool):
        self.db = db
        self.is_async = is_async

    async def insert(self, collection, data):
        data["created_dt"] = datetime.fromisoformat(data.get("created_dt"))
        if self.is_async:
            await self.db[collection].insert_one(data)
        else:
            await asyncio.to_thread(self._insert_sync, collection, data)

    def _insert_sync(self, collection, data):
        self.db[collection].insert_one(data)
        
    async def clean_logs(self, retention_days: int):
        """Удаляет документы старше retention_days по created_dt."""
        threshold_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        if self.is_async:
            result = await self.db["logs"].delete_many(
                {"created_dt": {"$lt": threshold_date}}
            )
        else:
            result = await asyncio.to_thread(
                self._clean_logs_sync,
                threshold_date,
            )
        logger.info(
            f"[{datetime.now()}] Logs older than {retention_days} days deleted. "
            f"Deleted count: {result.deleted_count}"
        )
        
    def _clean_logs_sync(self, threshold_date):
        return self.db["logs"].delete_many(
            {"created_dt": {"$lt": threshold_date}}
        )
