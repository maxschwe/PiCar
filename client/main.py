import logging
import os
import time

from src import TcpClient, sync_dir, config, ACTION, RETURN
from src import Window


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
synced_count = sync_dir(client, all=False)
if synced_count > 0:
    client.exec_restart()
win = Window(client)

time_between = 1 / config.FPS
while win.active:
    start = time.time()
    win.update_livestream()
    win.update()
    time.sleep(max(0, (time_between - (time.time() - start))))

client.disconnect()
