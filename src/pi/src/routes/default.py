import logging

from .blueprint import Blueprint
from .. import ACTION

server = Blueprint()


@server.on(ACTION.HI)
def hi(arg, ret_type):
    logging.info("Hello World")


@server.on(ACTION.ECHO)
def echo(msg, socket):
    socket.send(action=ACTION.ACK, msg=msg)
