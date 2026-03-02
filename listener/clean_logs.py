import asyncio
import logging
import os

from dotenv import load_dotenv

from db_interfaces.storage_fabric import create_storage

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("info")

load_dotenv()

async def main():
    LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", 30))
    DB_URL = os.getenv("DB_URL")
    storage = await create_storage(DB_URL)
    await storage.clean_logs(LOG_RETENTION_DAYS)
        

if __name__ == "__main__":
    asyncio.run(main())
