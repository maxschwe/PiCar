import os
import logging


class Config:

    # ==================================================================
    # SERVER configuration
    # ==================================================================
    SERVER = ""
    PORT_SYNC = 4000
    PORT_API = 4001

    ENCODING = "utf-8"
    MSG_LENGTH = 1024

    # ==================================================================
    # LOG configuration
    # ==================================================================
    LOG_DIR = "logging"
    LOG_SYNC = os.path.join(LOG_DIR, "sync_server.log")
    LOG_API = os.path.join(LOG_DIR, "api_server.log")

    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s: %(message)s'
    LOG_HEADER = False
    LOG_FILE = False
    LOG_FILE_MODE = "w"
