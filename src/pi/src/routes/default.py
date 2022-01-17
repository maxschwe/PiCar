import logging

from .blueprint import Blueprint
from .. import ACTION
from .. import RETURN

server = Blueprint()


@server.on(ACTION.HI)
def hi(arg, ret_type):
    logging.info("Hello World")


@server.on(ACTION.ECHO)
def echo(msg, socket):
    socket.send(action=ACTION.ECHO, ret_type=RETURN.ACK, msg=msg)
