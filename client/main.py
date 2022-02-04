import logging
import os
import time

from tcp import TcpClient, sync_dir
from gui import Window
from config import Config


def setup_logging():
    if Config.LOG_FILE:
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        logging.basicConfig(format=Config.LOG_FORMAT,
                            filemode=Config.LOG_FILE_MODE, filename=Config.LOG_TCP, level=Config.LOG_LEVEL)
    else:
        logging.basicConfig(format=Config.LOG_FORMAT, level=Config.LOG_LEVEL)


x = os.getcwd()
print(x)
setup_logging()

client = TcpClient()
client.connect()
client.load_status()
synced_count = sync_dir(client, all=False)
if synced_count > 0:
    client.exec_restart()
win = Window(client, width=3000, height=1500)
win.mainloop()


client.disconnect()
