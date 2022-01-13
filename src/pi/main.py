import logging
import os

from tcp_server import TcpServer
from config import Config

config = Config()


def setup_logging():
    os.makedirs(config.LOG_DIR, exist_ok=True)
    if config.LOG_FILE:
        logging.basicConfig(format=config.LOG_FORMAT,
                            filemode=config.LOG_FILE_MODE, filename=config.LOG_TCP, level=config.LOG_LEVEL)
    else:
        logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL)


setup_logging()
server = TcpServer()
server.run()
