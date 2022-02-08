import logging
from threading import Thread
import math
import json
import traceback
import time
import os
import socket

from .config import Config
from .actions import ACTIONS


# JSON, int, float, decode and more_to_recv are generated and dont need to be specified
FLAGS = ["", "bool", "float", "int", "json", "decode", "ack", "more_to_recv"]
DEFAULT_FLAG_VALUES = [False, False, False, False, False, True, False, False]
ACTIONS_NO_LOG = [ACTIONS.LIVESTREAM]


class TcpHandler(Thread):
    def __init__(self, socket, addr, action_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = socket
        self.addr = addr
        self.action_map = action_map
        self.action_map["server-handler"] = {
            ACTIONS.DISCONNECT: self.disconnect,
            ACTIONS.PING: self.ping_response,
            ACTIONS.PUT: self.put,
            ACTIONS.ECHO: self.echo,
            ACTIONS.HI: self.hi,
        }
        self.connected = True

    def run(self):
        try:
            while self.connected:
                self.sent_response = False
                # accept request
                action, params, flags = self.receive(log=True)

                # handle request
                self.handle_action(action, params, flags)
        except:
            self.log(f"Client {self.addr} disconnected!", type="server")

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
        if log and action not in ACTIONS_NO_LOG:
            self.log(f"{action}: {params}", type="recv")
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
        elif flags["int"]:
            recv_text = int(recv_text)
        elif flags["float"]:
            recv_text = float(recv_text)
        elif flags["bool"]:
            recv_text = bool(int(recv_text))
        return recv_text

    def received_ack(self):
        action, _, _ = self.receive()
        return action == ACTIONS.ACK

    def send(self, action, params="", log=True, **flags):
        if type(params) != list:
            params = [params]
        params_count = len(params)
        for i, msg in enumerate(params):
            flags["more_to_recv"] = params_count - 1 != i
            flags["json"] = type(msg) == dict
            flags["decode"] = type(msg) != bytes
            flags["int"] = type(msg) == int
            flags["float"] = type(msg) == float
            flags["bool"] = type(msg) == bool

            # convert msg to string and convert to bytes
            if type(msg) != bytes:
                if flags["json"]:
                    msg = json.dumps(msg)
                elif flags["bool"]:
                    msg = int(msg)
                msg = str(msg)
                msg = msg.encode(encoding=Config.ENCODING)
            # calculate msg length
            msg_length = len(msg)

            # send header
            sent_flags = self.send_header(action, msg_length, **flags)

            # send msg
            if msg_length > 0:
                self.send_msg(msg, msg_length, sent_flags)
        if log and action not in ACTIONS_NO_LOG:
            self.log(f"{action}: {params}", type="sent")
        self.sent_response = True
        # wait for ack if expected
        if sent_flags["ack"]:
            return self.received_ack()
        else:
            return True

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

    def _find_action_map(self, action):
        if action in self.action_map["server-global"]:
            return self.action_map["server-global"][action], "server-global"
        elif action in self.action_map["server-handler"]:
            return self.action_map["server-handler"][action], "server-handler"
        else:
            for file, maps in self.action_map["files"].items():
                if action in maps:
                    return maps[action], file
        return None, None

    def handle_action(self, action, params, flags):
        func, search_path = self._find_action_map(action)
        if func is None:
            error = f"{action} is not mapped"
            logging.error(error)
            self.send(ACTIONS.ERROR, error)
            return
        if action in self.action_map:
            func = self.action_map[action]
        var_names = func.__code__.co_varnames[:]
        kwargs = {}
        if "params" in var_names:
            kwargs["params"] = params
        if "flags" in var_names:
            kwargs["flags"] = flags
        if "socket" in var_names:
            kwargs["socket"] = self
        try:
            func(**kwargs)
        except:
            error = traceback.format_exc()
            error_txt = f"{search_path}/{action}: {error}"
            logging.error(error_txt)
            self.send(ACTIONS.ERROR, error_txt)
            return

        # send ack if expected and if not already other response
        if flags["ack"] and not self.sent_response:
            self.send_ack()

    def log(self, msg="", type="txt"):
        if type == "txt":
            logging.info(f">>> {msg}")
        elif type == "recv":
            logging.info(f"Rx: {msg}")
        elif type == "sent":
            logging.info(f"Tx: {msg}")
        elif type == "div":
            logging.info(50*"-")
        elif type == "server":
            logging.info(f"[{msg}]")
        else:
            logging.error("Wrong type log")

    def ping_response(self):
        start_time = time.time()
        self.send(ACTIONS.PING, ack=True)
        self.log(
            f"Ping of {self.addr}: {time.time() - start_time:6f}s", type="server")

    def echo(self, params):
        self.send(action=ACTIONS.ECHO, params=params)

    def hi(self):
        self.log("Hello World")

    def put(self, params):
        file_path = params[0]
        path_dir = "/".join(file_path.split("/")[:-1])
        os.makedirs(path_dir, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(params[1])
        logging.info(f"Created file: {file_path}")

    def disconnect(self, send_ack=True):
        # send ack and disconnect
        if self.connected:
            if send_ack:
                self.send_ack()
            self.socket.close()
            self.connected = False

            self.log(f"Client {self.addr} disconnected!", type="server")
