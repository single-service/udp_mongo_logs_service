import asyncio
from dataclasses import dataclass
import logging
import os
import json
from typing import Any, Dict
import socket

from db_interfaces.base import StorageInterface
from db_interfaces.clickhousedb import ClickHouseStorage
from db_interfaces.postgesqldb import PostgresStorage
from db_interfaces.storage_fabric import create_storage

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
