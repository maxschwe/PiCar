import socket
import logging
import time
import math
import traceback
import json

from .config import Config
from .actions import ACTIONS


# JSON, decode and more_to_recv are generated and dont need to be specified
FLAGS = ["", "", "", "", "json", "decode", "ack", "more_to_recv"]
DEFAULT_FLAG_VALUES = [False, False, False, False, False, True, True, False]


class TcpClient:
    def __init__(self):
        pass

    def connect(self):
        self.connected = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.socket.settimeout(5)
        for port in range(Config.PORT[0], Config.PORT[0] + Config.PORT[1]):
            try:
                self.socket.connect((Config.SERVER, port))
                self.connected = True
                break
            except:
                traceback.print_exc()
        if not self.connected:
            self.log("Failed to connect to server", type="server")
            return False
        self.log(f"Connected to {Config.SERVER}:{port}", type="server")
        self.log(type="div")
        self.ping()
        return True

    def exec(self, action, params="", log=False, **kwargs):
        sent_flags = self.send(action=action, params=params, log=log, **kwargs)

        # when expects response
        if sent_flags["ack"]:
            action, params, flags = self.receive(log=log)

            # send back ack if expected
            if flags["ack"]:
                self.send(ACTIONS.ACK, ack=False, log=log)
            if action == ACTIONS.ACK:
                return True
            return action, params

    def receive(self, log=False):
        more_to_recv = True
        params = []
        while more_to_recv:
            action, msg_length, flags = self.recv_header()
            # recv msg if available
            if msg_length > 0:
                msg = self.recv_msg(msg_length, flags)
            else:
                msg = ''
            params.append(msg)
            more_to_recv = flags["more_to_recv"]
        if len(params) == 1:
            params = params[0]
        if log:
            self.log(f"{action}: {params}", type="recv")
        if action == ACTIONS.ERROR:
            self.log(f"{params}", type="error")
        return action, params, flags

    def recv_header(self):
        header = self.socket.recv(8)
        if header == b'':
            raise RuntimeError("Socket connection broken")
        # decode header
        action = ACTIONS.decode(int.from_bytes(header[:2], byteorder='big'))
        msg_length = int.from_bytes(header[2:7], byteorder='big')
        val_flags = header[7]
        # convert val flags to single bits and then map to flag names
        flags = {flag_name: val == "1" for val, flag_name in zip(
            "{0:08b}".format(val_flags), FLAGS)}
        return action, msg_length, flags

    def recv_msg(self, msg_length, flags):
        recv_text = b""
        while msg_length > 0:
            recv_length = min(msg_length, Config.MSG_LENGTH)
            new_txt = self.socket.recv(recv_length)
            recv_text += new_txt
            msg_length -= len(new_txt)
        # decode msg if flag is set
        if flags["decode"] or flags["json"]:
            recv_text = recv_text.decode(Config.ENCODING)
        if flags["json"]:
            recv_text = json.loads(recv_text)
        return recv_text

    def send(self, action, params="", log=False, **flags):
        if type(params) != list:
            params = [params]
        params_count = len(params)
        for i, msg in enumerate(params):
            flags["more_to_recv"] = params_count - 1 != i
            flags["json"] = type(msg) == dict
            flags["decode"] = type(msg) != bytes

            # convert msg to byte and evtl. encode
            if type(msg) != bytes:
                msg = str(msg)
                if flags["json"]:
                    msg = json.dumps(msg)
                msg = msg.encode(encoding=Config.ENCODING)
            # calculate msg length
            msg_length = len(msg)
            # send header
            sent_flags = self.send_header(action, msg_length, **flags)

            # send msg
            if msg_length > 0:
                self.send_msg(msg, msg_length, sent_flags)
        if log:
            self.log(f"{action}: {params}", type="sent")

        self.sent_response = True
        return sent_flags

    def send_header(self, action, msg_length, **kwargs):
        action_encoded = action.value.to_bytes(2, byteorder="big")
        msg_length_encoded = msg_length.to_bytes(5, byteorder="big")

        # convert possible kwargs to flag byte
        flags = DEFAULT_FLAG_VALUES[:]
        for name, value in kwargs.items():
            if name in FLAGS:
                index = FLAGS.index(name)
                flags[index] = value
        flags_val = 0
        for flag in flags:
            flags_val <<= 1
            flags_val += int(flag)
        flags_encoded = flags_val.to_bytes(1, byteorder="big")

        header = action_encoded + msg_length_encoded + flags_encoded

        # send header
        sent = self.socket.send(header)
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        return dict(zip(FLAGS, flags))

    def send_msg(self, msg, msg_length, flags):
        for i in range(math.ceil(msg_length/Config.MSG_LENGTH)):
            msg_part = msg[i * Config.MSG_LENGTH:
                           (i+1)*Config.MSG_LENGTH]
            sent = self.socket.send(msg_part)
            if sent == 0:
                raise RuntimeError("Socket connection broken")

    def send_ack(self):
        self.send(ACTIONS.ACK)

    def load_status(self):
        self.log(type="div")
        action, params = self.exec(ACTIONS.LOAD_STATUS)
        print("Status files: ")
        for file, error in params.items():
            if error is not None:
                print(f">>> {file}: \n{error}")
        self.log(type="div")

    def ping(self):
        start = time.time()
        success = self.exec(action=ACTIONS.PING, log=True)
        if not success:
            raise RuntimeError(
                "Socket connection broken or server wrong configured")
        ping_time = time.time() - start
        self.log(f"Ping: {ping_time:2f}s")
        self.log(type="div")
        return ping_time

    def put(self, filepath, new_filepath):
        with open(filepath, "rb") as f:
            file_txt = f.read()
        success = self.exec(action=ACTIONS.PUT, params=[
                            new_filepath, file_txt], log=False)
        if success:
            logging.info(f"Synced {filepath} to {new_filepath}")
        else:
            logging.error(f"Error when syncing: {filepath} to {new_filepath}")

    def disconnect(self, action=ACTIONS.DISCONNECT):
        ack = self.exec(action=action)
        if not ack:
            raise RuntimeError("Error when disconnecting")
        self.connected = False
        self.socket.close()
        self.log(type="div")
        self.log("You have disconnected successfully!", type="server")

    def exec_restart(self):
        self.disconnect(action=ACTIONS.RESTART)
        time.sleep(Config.DELAY_RECONNECTING)
        start_time = time.time()
        while (time.time() - start_time) < Config.TIMEOUT_RECONNECTING:
            if self.connect():
                break
            time.sleep(Config.DELAY_RETRY_CONNECTING)
        if not self.connected:
            logging.error("Failed to reconnect after restarting server")

    def log(self, msg="", type="txt"):
        # TODO: LOG with listener for GUI
        if type == "txt":
            logging.info(f">>> {msg}")
        elif type == "recv":
            logging.info(f"Rx: {msg}")
        elif type == "sent":
            logging.info(f"Tx: {msg}")
        elif type == "server":
            logging.info(f"[{msg}]")
        elif type == "div":
            logging.info(60*"-")
        elif type == "error":
            logging.error("!!!{msg}!!!")
        else:
            logging.error("Wrong type log")
