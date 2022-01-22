import os
import logging


class Config:
    SERVER = "192.168.178.75"
    PORT = [4000, 4001, 4002]

    LOG_DIR = "logging"
    LOG_TCP = os.path.join(LOG_DIR, "tcp.log")
    LOG_LEVEL = logging.INFO
    LOG_FILE_MODE = "w"
    LOG_FILE = False
    LOG_FORMAT = '%(asctime)s: %(message)s'
    LOG_HEADER = False

    ENCODING = "utf-8"
    MSG_LENGTH = 1024

    PATH_PC = "C:/Users/Max/Desktop/Daten/Python/PiCar/src/pi"
    PATH_PI = "/home/pi/PiCar"

    PATH_DATA = "data"
    DELAY_RECONNECTING = 3
    TIMEOUT_RECONNECTING = 10
    DELAY_RETRY_CONNECTING = 0.5

    FPS = 30
