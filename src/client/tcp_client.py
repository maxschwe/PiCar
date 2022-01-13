import socket
import logging
import time

from config import Config
from const import *


config = Config()


class TcpClient:
    def __init__(self):
        self.connected = True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.socket.connect(config.ADDR)
        logging.info(f"Connected to {config.SERVER}:{config.PORT}")
        self.ping()
        self.disconnect()
        while self.connected:
            pass

    def send(self, action, ret_type=RETURN.ACK, msg=""):
        msg_length = 0 if msg is None else len(msg)

        action_encoded = action.value.to_bytes(1, byteorder="big")
        msg_length_encoded = msg_length.to_bytes(6, byteorder="big")
        ret_type_encoded = ret_type.value.to_bytes(1, byteorder="big")

        header = action_encoded + msg_length_encoded + ret_type_encoded
        sent = self.socket.send(header)
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        logging.info(
            f"Sent {action}, {msg[:10]}...({msg_length} Bytes), {ret_type} to server")

        if msg_length > 0:
            msg_encoded = msg.encode(encoding=config.ENCODING)
            print(msg_encoded)

    def recv_header(self):
        header = self.socket.recv(8)
        if header == b'':
            raise RuntimeError("Socket connection broken")
        action = ACTIONS.decode(header[0])
        msg_length = int.from_bytes(header[1:7], byteorder='big')
        ret_type = RETURN.decode(header[7])
        logging.info(
            f"Received header: {action}, {msg_length}, {ret_type}")
        return action, msg_length, ret_type

    def received_ack(self):
        action, _, _ = self.recv_header()
        return action == ACTIONS.ACK

    def ping(self):
        start = time.time()
        self.send(action=ACTIONS.PING, ret_type=RETURN.ACK)
        if not self.received_ack():
            raise RuntimeError(
                "Socket connection broken or server wrong configured")
        ping_time = time.time() - start
        logging.info(f"Ping: {ping_time:2f}s")
        return ping_time

    def disconnect(self):
        self.send(action=ACTIONS.DISCONNECT, ret_type=RETURN.ACK)
        if not self.received_ack():
            raise RuntimeError("Error when disconnecting")
        self.connected = False
        self.socket.close()
        logging.info("You have disconnected successfully!")
