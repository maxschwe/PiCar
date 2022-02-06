import logging
import os
import time
from threading import Thread

from tcp import TcpClient
from gui import Window
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
win = Window(client, width=3000, height=1500)
client.try_connect().start()

win.mainloop()


client.disconnect()
