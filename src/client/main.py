import logging
import os
import time
from tkinter import *

from src import TcpClient, sync_dir, config, ACTION, RETURN


def setup_logging():
    os.makedirs(config.LOG_DIR, exist_ok=True)
    if config.LOG_FILE:
        logging.basicConfig(format=config.LOG_FORMAT,
                            filemode=config.LOG_FILE_MODE, filename=config.LOG_TCP, level=config.LOG_LEVEL)
    else:
        logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL)


setup_logging()

client = TcpClient()
client.connect()
client.exec(ACTION.HI)

sync_dir(client, all=False)
client.exec_restart()
client.disconnect()
