import os
import logging


class Config:
    SERVER = ""
    PORT = 4004
    ADDR = (SERVER, PORT)

    LOG_DIR = "logging"
    LOG_TCP = os.path.join(LOG_DIR, "tcp.log")
    LOG_LEVEL = logging.INFO
    LOG_FILE_MODE = "w"
    LOG_FILE = False
    LOG_FORMAT = '%(asctime)s: %(message)s'
    LOG_HEADER = False

    ENCODING = "utf-8"
    MSG_LENGTH = 1024
