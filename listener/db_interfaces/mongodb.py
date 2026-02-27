import asyncio

from db_interfaces.base import StorageInterface

class MongoStorage(StorageInterface):

    def __init__(self, db, is_async: bool):
        self.db = db
        self.is_async = is_async

    async def insert(self, collection, data):
        if self.is_async:
            await self.db[collection].insert_one(data)
        else:
            await asyncio.to_thread(self._insert_sync, collection, data)

    def _insert_sync(self, collection, data):
        self.db[collection].insert_one(data)
