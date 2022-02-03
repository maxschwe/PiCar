import logging
import os
from threading import Thread
import traceback

from tcp import TcpServer
from config import Config


def setup_logging():
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    if Config.LOG_FILE:
        logging.basicConfig(format=Config.LOG_FORMAT,
                            filemode=Config.LOG_FILE_MODE, filename=Config.LOG_TCP, level=Config.LOG_LEVEL)
    else:
        logging.basicConfig(format=Config.LOG_FORMAT, level=Config.LOG_LEVEL)


setup_logging()

try:
    from robot import Robot
    robot = Robot.instance()
    Thread(target=robot.run, daemon=True).start()
    robot_error = None
except:
    robot_error = traceback.format_exc()
server = TcpServer()
server.robot_error = robot_error
server.run()
