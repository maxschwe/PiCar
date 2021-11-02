import os
import logging


class Config:
    src_folder = "/home/max/Schreibtisch/Python/PiCar/src/pi"
    dest_folder = "/home/pi/PiCar"

    path_execute = "/home/pi/PiCar/src/api/run_api.py"

    # * = subdirs allowed, ** = name must be part of path
    excluded_dirs = ["docs", "*__pycache__"]
    excluded_files = []

    filename_last_sync = ".last_sync"

    logging_file = False
    logging_level = logging.INFO

    filepath_last_sync = os.path.join(src_folder, filename_last_sync)

    # sync all independent from modified time
    sync_all = True

    host = "192.168.178.75"
    username = "pi"
    password = "3110"
