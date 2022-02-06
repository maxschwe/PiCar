import os
import logging

from tcp import TcpClient, ACTIONS
from config import Config


def setup_logging():
    if Config.LOG_FILE:
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        logging.basicConfig(format=Config.LOG_FORMAT,
                            filemode=Config.LOG_FILE_MODE, filename=Config.LOG_TCP, level=Config.LOG_LEVEL)
    else:
        logging.basicConfig(format=Config.LOG_FORMAT, level=Config.LOG_LEVEL)


setup_logging()

client = TcpClient()
client.connect()

client.load_status()

"""action, params = client.exec(
        ACTIONS.ECHO, ["Hallo ich bin der Max", {"wie geht es dir": 20}], log=True)"""


client.disconnect()
