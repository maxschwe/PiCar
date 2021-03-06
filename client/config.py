import os
import logging


class Config:
    # ==================================================================
    # LOG configuration
    # ==================================================================
    LOG_DIR = "log"
    LOG_TCP = os.path.join(LOG_DIR, "client.log")

    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s: %(message)s'
    LOG_HEADER = False
    LOG_FILE = False
    LOG_FILE_MODE = "w"
