import socket
import logging
import time
import math

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
        self.send(ACTION.HI)
        self.send(ACTION.ECHO, msg="hallo")
        self.disconnect()
        while self.connected:
            pass

    def send(self, action, ret_type=RETURN.ACK, msg=""):
        # calculate msg length
        msg_length = len(msg)

        # encode header
        action_encoded = action.value.to_bytes(1, byteorder="big")
        msg_length_encoded = msg_length.to_bytes(6, byteorder="big")
        ret_type_encoded = ret_type.value.to_bytes(1, byteorder="big")

        header = action_encoded + msg_length_encoded + ret_type_encoded

        # send header
        sent = self.socket.send(header)
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        logging.info(
            f"Sent {action}, {msg[:10]}...({msg_length} Bytes), {ret_type} to server")

        # send msg if exists
        if msg_length > 0:
            msg_encoded = msg.encode(encoding=config.ENCODING)
            for i in range(math.ceil(msg_length/config.MSG_LENGTH)):
                msg_part = msg_encoded[i *
                                       config.MSG_LENGTH:(i+1)*config.MSG_LENGTH]
                sent = self.socket.send(msg_part)
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
            logging.info(f"Sent message ({msg_length} Bytes)")
        if ret_type == RETURN.ACK:
            return self.received_ack()

    def recv_header(self):
        header = self.socket.recv(8)
        if header == b'':
            raise RuntimeError("Socket connection broken")
        # decode header
        action = ACTION.decode(header[0])
        msg_length = int.from_bytes(header[1:7], byteorder='big')
        ret_type = RETURN.decode(header[7])
        logging.info(
            f"Received header: {action}, {msg_length}, {ret_type}")
        return action, msg_length, ret_type

    def recv_msg(self, msg_length):
        while msg_length > 0:
            recv_length = max(msg_length, config.MSG_LENGTH)
            recv_text = ""
            recv_text += self.socket.recv(recv_length).decode(config.ENCODING)
            msg_length -= config.MSG_LENGTH
        logging.info(f"Received: {recv_text}")

    def received_ack(self):
        action, _, _ = self.recv_header()
        return action == ACTION.ACK

    def ping(self):
        start = time.time()
        ack = self.send(action=ACTION.PING, ret_type=RETURN.ACK)
        if not ack:
            raise RuntimeError(
                "Socket connection broken or server wrong configured")
        ping_time = time.time() - start
        logging.info(f"Ping: {ping_time:2f}s")
        return ping_time

    def disconnect(self):
        ack = self.send(action=ACTION.DISCONNECT, ret_type=RETURN.ACK)
        if not ack:
            raise RuntimeError("Error when disconnecting")
        self.connected = False
        self.socket.close()
        logging.info("You have disconnected successfully!")
