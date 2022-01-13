import socket
from threading import Thread
import logging
import time

from config import Config
from const import *


config = Config()


class TcpServer:
    def __init__(self):
        self.running = True

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.socket.bind(config.ADDR)
        self.socket.listen()
        logging.info(f"Server is listening on port {config.PORT}")
        self.handlers = []
        while self.running:
            conn, addr = self.socket.accept()
            # Start handler for client
            handler = TcpHandler(conn, addr)
            handler.start()
            self.handlers.append(handler)


class TcpHandler(Thread):
    def __init__(self, socket, addr, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = socket
        self.addr = addr
        self.connected = True

    def run(self):
        while self.connected:
            action, msg_length, ret_type = self.recv_header()
            # recv msg if available
            if msg_length > 0:
                msg = self.recv_msg()
            else:
                msg = ''
            self.handle_action(action, msg, ret_type)

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

    def recv_msg(self):
        pass

    def handle_action(self, action, msg, ret_type):
        if action == ACTIONS.DISCONNECT:
            if ret_type == RETURN.ACK:
                self.send_ack()
            self.connected = False
            self.socket.close()
            logging.info(f"Client {self.addr} disconnected!")
            return

        # send ack if expected
        if ret_type == RETURN.ACK:
            self.send_ack()

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
            f"Sent {action}, {msg[:10]}...({msg_length} Bytes), {ret_type} to {self.addr}")

        if msg_length > 0:
            msg_encoded = msg.encode(encoding=config.ENCODING)
            print(msg_encoded)

    def send_ack(self):
        self.send(ACTIONS.ACK, ret_type=RETURN.NONE)

    def received_ack(self):
        action, _, _ = self.recv_header()
        return action == ACTIONS.ACK

    def ping(self):
        start = time.time()
        self.send(action=ACTIONS.PING, ret_type=RETURN.ACK)
        success = self.received_ack()
        if not success:
            raise RuntimeError(
                "Socket connection broken or server wrong configured")
        ping_time = time.time() - start
        logging.info(f"Ping: {ping_time:2f}s")
        return ping_time
