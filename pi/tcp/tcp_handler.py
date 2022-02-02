import logging
from threading import Thread
import math
import json

from .config import Config
from .actions import ACTIONS

FLAGS = ["", "", "", "", "json", "decode", "ack", "more_to_recv"]
DEFAULT_FLAG_VALUES = [False, False, False, False, False, True, False, False]


class TcpHandler(Thread):
    def __init__(self, socket, addr, action_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = socket
        self.addr = addr
        self.action_map = action_map
        self.connected = True

    def run(self):
        while self.connected:
            self.sent_response = False
            # accept request
            action, params, flags = self.receive()

            # handle request
            self.handle_action(action, params, flags)

    def receive(self):
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

        return action, params, flags

    def recv_header(self):
        header = self.socket.recv(8)
        if header == b'':
            raise RuntimeError("Socket connection broken")
        # decode header
        action = ACTIONS.decode(header[:2])
        msg_length = int.from_bytes(header[1:7], byteorder='big')
        val_flags = int.from_bytes(header[7], byteorder="big")
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

    def received_ack(self):
        action, _, _ = self.recv_header()
        if action == ACTIONS.ACK:
            return True
        return False

    def send(self, action, params="", **flags):
        if type(params) == str:
            params = [params]
        params_count = len(params)
        for i, msg in enumerate(params):
            # calculate msg length
            msg_length = len(msg)
            flags["more_to_recv"] = params_count - 1 != i
            flags["json"] = type(msg) == dict

            # send header
            sent_flags = self.send_header(action, msg_length, **flags)

            # send msg
            if msg_length > 0:
                self.send_msg(msg, msg_length, sent_flags)
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
        return flags

    def send_msg(self, msg, msg_length, flags):
        if type(msg) != bytes:
            if flags["json"]:
                msg = json.dumps(msg)
            msg = msg.encode(encoding=Config.ENCODING)
        for i in range(math.ceil(msg_length/Config.MSG_LENGTH)):
            msg_part = msg[i * Config.MSG_LENGTH:
                           (i+1)*Config.MSG_LENGTH]
            sent = self.socket.send(msg_part)
            if sent == 0:
                raise RuntimeError("Socket connection broken")

    def send_ack(self):
        self.send(ACTIONS.ACK)

    def handle_action(self, action, params, flags):
        if action == ACTIONS.DISCONNECT:
            self.disconnect()
            return
        elif action == ACTIONS.RESTART:
            self.disconnect()
            self.action_map[action][0]()
            return
        elif action == ACTIONS.PING:
            self.send(ACTIONS.PING, ack=True)
        elif action in self.action_map:
            func = self.action_map[action][0]
            var_names = func.__code__.co_varnames[:]
            kwargs = {}
            if "params" in var_names:
                if len(params) < 2:
                    params = params[0]
                kwargs["params"] = params
            if "flags" in var_names:
                kwargs["flags"] = flags
            if "socket" in var_names:
                kwargs["socket"] = self

            func(**kwargs)
        else:
            error = f"{action} is not mapped"
            logging.error()
            self.send(ACTIONS.ERROR, error)

        # send ack if expected and if not already other response
        if flags["ack"] and not self.sent_response:
            self.send_ack()

    def log(self, msg="", type="txt"):
        if type == "txt":
            logging.info(f">>> {msg}")
        elif type == "recv":
            logging.info(f"- Recv: {msg}")
        elif type == "sent":
            logging.info(f"Sent: {msg}")
        elif type == "div":
            logging.info(60*"-")
        elif type == "server":
            logging.info(f"[{msg}]")
        else:
            logging.error("Wrong type log")

    def disconnect(self):
        # send ack and disconnect
        self.send_ack()
        self.connected = False
        self.socket.close()
        self.log(f"Client {self.addr} disconnected!", type="server")
