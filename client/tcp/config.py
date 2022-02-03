import os
import logging


class Config:
    # ==================================================================
    # SERVER configuration
    # ==================================================================
    SERVER = "127.0.0.1"  # SERVER = "192.168.178.75"
    PORT = 4000, 10

    DELAY_RECONNECTING = 3
    TIMEOUT_RECONNECTING = 10
    DELAY_RETRY_CONNECTING = 0.5

    ENCODING = "utf-8"
    MSG_LENGTH = 1024

    # ==================================================================
    # Sync configuration
    # ==================================================================
    PATH_PC = "C:/Users/Max/Desktop/Daten/Python/PiCar/pi"
    PATH_DATA = "data"
    PATH_PI = "C:/Users/Max/Desktop/Test"  # /home/pi/PiCar
