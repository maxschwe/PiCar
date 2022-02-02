import logging
import os


server = Blueprint()


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
