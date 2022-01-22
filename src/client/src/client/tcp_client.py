import socket
import logging
import time
import math
import traceback

from .. import config, ACTION, RETURN


class TcpClient:
    def __init__(self):
        self.connected = False

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for port in config.PORT:
            try:
                self.socket.connect((config.SERVER, port))
                self.connected = True
                break
            except:
                pass
        if not self.connected:
            logging.error("Failed to connect to server")
            return False
        self.log(f"Connected to {config.SERVER}:{port}", type="server")
        self.log(type="div")
        self.ping()
        return True

    def send(self, action=ACTION.PING, msg="", ret_type=RETURN.ACK):
        # calculate msg length
        msg_length = len(msg)

        # encode header
        if type(action) != int:
            action = action.value
        action_encoded = action.to_bytes(1, byteorder="big")
        msg_length_encoded = msg_length.to_bytes(6, byteorder="big")
        if type(ret_type) != int:
            ret_type = ret_type.value
        ret_type_encoded = ret_type.to_bytes(1, byteorder="big")

        header = action_encoded + msg_length_encoded + ret_type_encoded

        # send header
        sent = self.socket.send(header)
        if sent == 0:
            raise RuntimeError("Socket connection broken")

        # send msg if exists
        if msg_length > 0:
            if type(msg) != bytes:
                msg_encoded = msg.encode(encoding=config.ENCODING)
            else:
                msg_encoded = msg
            for i in range(math.ceil(msg_length/config.MSG_LENGTH)):
                msg_part = msg_encoded[i *
                                       config.MSG_LENGTH:(i+1)*config.MSG_LENGTH]
                sent = self.socket.send(msg_part)
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
        self.log(
            f"{ACTION.decode(action)} - {msg[:15]}{'...' if msg_length > 15 else ''} ({msg_length} Bytes)", type="sent")

    def exec(self, action=ACTION.PING, msg="", ret_type=RETURN.ACK):
        self.send(action=action, msg=msg, ret_type=ret_type)
        if ret_type != RETURN.ACK:
            return self.receive()
        if self.received_ack():
            return True
        logging.error(f"Did not receive {ACTION.ACK}")
        return False

    def receive(self):
        action, msg_length, ret_type = self.recv_header()
        if msg_length > 0:
            msg = self.recv_msg(msg_length)
        else:
            msg = ""
        self.log(
            f"{action} - {msg[:15]}{'...' if msg_length > 15 else ''} ({msg_length} Bytes)", type="recv")
        if ret_type == RETURN.ACK:
            self.send_ack()
        self.log(type="div")
        return msg

    def recv_header(self):
        header = self.socket.recv(8)
        if header == b'':
            raise RuntimeError("Socket connection broken")
        # decode header
        action = ACTION.decode(header[0])
        msg_length = int.from_bytes(header[1:7], byteorder='big')
        ret_type = RETURN.decode(header[7])
        return action, msg_length, ret_type

    def recv_msg(self, msg_length):
        recv_text = ""
        while msg_length > 0:
            recv_length = min(msg_length, config.MSG_LENGTH)
            recv_text += self.socket.recv(recv_length).decode(config.ENCODING)
            msg_length -= recv_length
        return recv_text

    def received_ack(self):
        action, _, _ = self.recv_header()
        if action == ACTION.ACK:
            self.log(ACTION.ACK, type="recv")
            self.log(type="div")
            return True
        return False

    def ping(self):
        start = time.time()
        ack = self.exec(action=ACTION.PING, ret_type=RETURN.ACK)
        if not ack:
            raise RuntimeError(
                "Socket connection broken or server wrong configured")
        ping_time = time.time() - start
        self.log(f"Ping: {ping_time:2f}s")
        self.log(type="div")
        return ping_time

    def put(self, filepath, new_filepath):
        with open(filepath, "rb") as f:
            file_txt = f.read()

        msg = f"{new_filepath}|".encode(config.ENCODING) + file_txt
        success = self.exec(action=ACTION.PUT, msg=msg)
        if not success:
            logging.error(f"Error when syncing: {filepath} to {new_filepath}")

    def disconnect(self):
        ack = self.exec(action=ACTION.DISCONNECT, ret_type=RETURN.ACK)
        if not ack:
            raise RuntimeError("Error when disconnecting")
        self.connected = False
        self.socket.close()
        self.log("You have disconnected successfully!", type="server")

    def exec_restart(self):
        ack = self.exec(action=ACTION.RESTART, ret_type=RETURN.ACK)
        if not ack:
            raise RuntimeError("Error when restarting")
        self.connected = False
        self.socket.close()
        self.log("You have disconnected successfully!", type="server")
        time.sleep(config.DELAY_RECONNECTING)
        start_time = time.time()
        while (time.time() - start_time) < config.TIMEOUT_RECONNECTING:
            if self.connect():
                break
            time.sleep(config.DELAY_RETRY_CONNECTING)
        if not self.connected:
            logging.error("Failed to reconnect after restarting server")

    def send_ack(self):
        self.send(ACTION.ACK, ret_type=RETURN.NONE)

    def log(self, msg="", type="txt"):
        if type == "txt":
            logging.info(f">>> {msg}")
        elif type == "recv":
            logging.info(f"~ Recv: {msg}")
        elif type == "sent":
            logging.info(f"Sent: {msg}")
        elif type == "server":
            logging.info(f"[{msg}]")
        elif type == "div":
            logging.info(60*"-")
        else:
            logging.error("Wrong type log")
