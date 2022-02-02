import logging
import os
from threading import Thread

from src import get_server, config
from src.robot import Robot


def setup_logging():
    os.makedirs(config.LOG_DIR, exist_ok=True)
    if config.LOG_FILE:
        logging.basicConfig(format=config.LOG_FORMAT,
                            filemode=config.LOG_FILE_MODE, filename=config.LOG_TCP, level=config.LOG_LEVEL)
    else:
        logging.basicConfig(format=config.LOG_FORMAT, level=config.LOG_LEVEL)


setup_logging()
server = get_server()

robot = Robot.instance()
Thread(target=robot.run, daemon=True).start()

server.run()
