import os
import logging


class Config:
    # ==================================================================
    # SERVER configuration
    # ==================================================================
    SERVER = "192.168.178.75"  # SERVER = "127.0.0.1"
    PORT = 4000, 10

    DELAY_RECONNECTING = 3
    TIMEOUT_RECONNECTING = 10
    DELAY_RETRY_CONNECTING = 0.5

    ENCODING = "utf-8"
    MSG_LENGTH = 1024

    # ==================================================================
    # Sync configuration
    # ==================================================================
    USE_PC = True
    PATH_PC = "/home/max/Schreibtisch/Python/PiCar/pi"
    PATH_LAPTOP = "C:/Users/Max/Desktop/Daten/Python/PiCar/pi"

    PATH_DATA = "data"
    PATH_PI = "/home/pi/PiCar"  # "C:/Users/Max/Desktop/Test"
