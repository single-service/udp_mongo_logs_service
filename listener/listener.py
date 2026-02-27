import asyncio
from dataclasses import dataclass
import logging
import os
import json
from typing import Any, Dict
from urllib.parse import urlparse

import socket
from clickhouse_driver import Client
import psycopg2
import asyncpg
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from db_interfaces.base import StorageInterface
from db_interfaces.clickhousedb import ClickHouseStorage
from db_interfaces.mongodb import MongoStorage
from db_interfaces.postgesqldb import PostgresStorage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class Message:
    type: str
    collection: str
    message: Dict[str, Any]


class UDPListener:
    def __init__(self, udp_host: str, udp_port: int, storage: StorageInterface):
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.storage = storage

        # Создаем UDP сокет для приёма
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_host, self.udp_port))
        logging.info(f"UDP Listener запущен на {self.udp_host}:{self.udp_port}")

    async def listen(self):
        while True:
            try:
                data, addr = await asyncio.to_thread(
                    self.sock.recvfrom, 65535
                )  # Максимальный размер датаграммы
                message = json.loads(data.decode("utf-8"))
                logging.info(f"Получено сообщение от {addr}: {message}")
                await self.process_message(message)

            except Exception as e:
                logging.error(f"Ошибка при обработке датаграммы: {e}")

    async def process_message(self, message):
        try:
            message = Message(**message)
        except Exception as e:
            logging.error(f"Bad message: {message}; Exception: {e}")
            return
        try:
            await self.storage.insert(
                message.collection,
                message.message,
            )
        except Exception as e:
                logging.error(f"Ошибка: {e}")
        
        
def parse_db_url(db_url: str) -> dict:
    parsed = urlparse(db_url)
    db_type = parsed.scheme 
    user = parsed.username
    password = parsed.password
    host = parsed.hostname
    port = parsed.port
    database = parsed.path.lstrip("/")
    return {
        "db_type": db_type,
        "user": user,
        "password": password,
        "host": host,
        "port": port,
        "database": database,
    }
       
        
def create_mongo_client(db_url: str, cfg: dict, is_async=False):
    if is_async:
        client = AsyncIOMotorClient(db_url)
        db = client[cfg.get("database")]
        return MongoStorage(db, is_async=True)
    else:
        client = MongoClient(db_url)
        db = client[cfg.get("database")]
        return MongoStorage(db, is_async=False)
        
        
async def create_postgres_client(cfg: dict, is_async=False):
    if is_async:
        conn = await asyncpg.connect(
            user=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            database=cfg["database"],
        )
        return PostgresStorage(conn, is_async=True)
    else:
        conn = psycopg2.connect(
            user=cfg["user"],
            password=cfg["password"],
            host=cfg["host"],
            port=cfg["port"],
            dbname=cfg["database"],
        )
        return PostgresStorage(conn, is_async=False)
   
            
def create_clickhouse_client(cfg: dict):
    client = Client(
        host=cfg["host"],
        port=cfg["port"] or 9000,
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
    )
    return ClickHouseStorage(client, cfg["database"])
   
        
async def create_storage(db_url: str) -> StorageInterface:
    IS_ASYNC = int(os.getenv("IS_ASYNC", "0"))
    cfg = parse_db_url(db_url)
    if cfg["db_type"] == "mongodb":
        return create_mongo_client(db_url, cfg, IS_ASYNC)
    elif cfg["db_type"] in ("postgresql", "postgres"):
        return await create_postgres_client(cfg, IS_ASYNC)
    elif cfg["db_type"] == "clickhouse":
        return create_clickhouse_client(cfg)
    else:
        raise ValueError(f"Unsupported DB type: {cfg['db_type']}")
    
    
async def main():
    UDP_HOST = "0.0.0.0"
    UDP_PORT = 9999

    DB_URL = os.getenv("DB_URL")
    storage = await create_storage(DB_URL)
    if isinstance(storage, (ClickHouseStorage, PostgresStorage)):
        await storage.init_table()
    listener = UDPListener(UDP_HOST, UDP_PORT, storage)
    await listener.listen()
        

if __name__ == "__main__":
    asyncio.run(main())
