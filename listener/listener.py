from dataclasses import dataclass
from datetime import datetime
import logging
import os
import json
from typing import Any, Dict

import socket
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


@dataclass
class Message:
    type: str
    collection: str
    message: Dict[str, Any]


class UDPListener:
    def __init__(self, udp_host, udp_port, mongo_config):
        self.udp_host = udp_host
        self.udp_port = udp_port
        self.db_client = MongoClient(mongo_config.get("url"))
        self.db = self.db_client[mongo_config.get("db")]

        # Создаем UDP сокет для приёма
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_host, self.udp_port))
        logging.info(f"UDP Listener запущен на {self.udp_host}:{self.udp_port}")

    def listen(self):
        while True:
            try:
                data, addr = self.sock.recvfrom(65535)  # Максимальный размер датаграммы
                message = json.loads(data.decode("utf-8"))
                logging.info(f"Получено сообщение от {addr}: {message}")
                self.process_message(message)

            except Exception as e:
                logging.error(f"Ошибка при обработке датаграммы: {e}")

    def process_message(self, message):
        try:
            message = Message(**message)
        except Exception as e:
            logging.error(f"Bad message: {message}; Exception: {e}")
            return
        collection = self.db[message.collection]
        collection.insert_one(message.message)

if __name__ == "__main__":
    UDP_HOST = "0.0.0.0"
    UDP_PORT = 9999

    CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
    CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")
    MONGO_URI = os.getenv("DB_URL")
    MONGO_DATABASE = os.getenv("MONGO_DB", "logs_db")

    MONGO_CONFIG = {
        "url": MONGO_URI,
        "db": MONGO_DATABASE,
    }

    listener = UDPListener(UDP_HOST, UDP_PORT, MONGO_CONFIG)
    listener.listen()
