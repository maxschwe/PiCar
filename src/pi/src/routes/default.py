import logging
import os
import cv2

from .blueprint import Blueprint
from .. import ACTION, RETURN, config

from ..server.camera import Camera

server = Blueprint()
camera = Camera()


@server.on(ACTION.HI)
def hi(arg, ret_type):
    logging.info("Hello World")


@server.on(ACTION.ECHO)
def echo(msg, socket):
    socket.send(action=ACTION.ECHO, ret_type=RETURN.ACK, msg=msg)


@server.on(ACTION.PUT, no_decoding=True)
def put(msg):
    delimeter = msg.find("|".encode(config.ENCODING))
    path = msg[:delimeter].decode(config.ENCODING)
    file_txt = msg[delimeter+1:]
    path_dir = "/".join(path.split("/")[:-1])
    os.makedirs(path_dir, exist_ok=True)
    logging.info(f"Created file: {path}")
    with open(path, "wb") as f:
        f.write(file_txt)


@server.on(ACTION.LIVESTREAM)
def livestream(socket):
    frame = camera._get_frame()
    socket.send(action=ACTION.LIVESTREAM, msg=frame)
