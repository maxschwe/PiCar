import socket
import logging
import time
import math
import traceback
import json
import os
from threading import Thread

from .config import Config
from .actions import ACTIONS


# JSON, int, float, decode and more_to_recv are generated and dont need to be specified
FLAGS = ["", "bool", "float", "int", "json", "decode", "ack", "more_to_recv"]
DEFAULT_FLAG_VALUES = [False, False, False, False, False, True, True, False]


class TcpClient:
    def __init__(self):
        self.connected = False
        self.log_bindings = []

    def connect(self):
        self.connected = connected = False
        for port in range(Config.PORT[0], Config.PORT[0] + Config.PORT[1]):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(2)
                self.socket.connect((Config.SERVER, port))
                connected = True
                break
            except OSError as e:
                error = e
            except:
                error = traceback.format_exc()
        if not connected:
            self.log(f"Failed to connect to server: {error}", type="error")
            return False
        self.log(f"Connected to {Config.SERVER}:{port}", type="server")
        self.log(type="div")
        self.connected = True
        return True

    def _check_connection(func):
        def wrapper(self, *args, **kwargs):
            if self.connected:
                try:
                    return func(self, *args, **kwargs)
                except socket.timeout:
                    self.connected = False
                    self.log("Trying to reconnect...", type="server")
                    self.try_connect().start()
            else:
                self.log("Client is not connected!", type="error")
        return wrapper

    def exec_no_timeout_handling(self, action, params="", log=False, **kwargs):

        if log:
            self.log(type="div")
        sent_flags = self.send(
            action=action, params=params, log=log, **kwargs)

        # when expects response
        if sent_flags["ack"]:
            action, params, flags = self.receive(log=log)

            # send back ack if expected
            if flags["ack"]:
                self.send(ACTIONS.ACK, log=log, ack=False)
            if action == ACTIONS.ACK:
                return True

            return action, params

    @_check_connection
    def exec(self, action, params="", log=False, **kwargs):
        return self.exec_no_timeout_handling(action=action, params=params, log=log, **kwargs)

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
        if action == ACTIONS.ERROR:
            self.log(f"{params}", type="error")
        elif log:
            self.log(f"{action}: {params}", type="recv")
        return action, params, flags

    def recv_header(self):
        header = self.socket.recv(8)
        if header == b'':
            raise socket.timeout
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
            if new_txt == b'':
                raise socket.timeout
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

    def send(self, action, params="", log=False, **flags):
        if type(params) != list:
            params = [params]
        params_count = len(params)
        for i, msg in enumerate(params):
            flags["more_to_recv"] = params_count - 1 != i
            flags["json"] = type(msg) == dict
            flags["int"] = type(msg) == int
            flags["float"] = type(msg) == float
            flags["bool"] = type(msg) == bool
            flags["decode"] = type(msg) != bytes

            # convert msg to byte and evtl. encode
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
            raise socket.timeout
        return dict(zip(FLAGS, flags))

    def send_msg(self, msg, msg_length, flags):
        for i in range(math.ceil(msg_length/Config.MSG_LENGTH)):
            msg_part = msg[i * Config.MSG_LENGTH:
                           (i+1)*Config.MSG_LENGTH]
            sent = self.socket.send(msg_part)
            if sent == 0:
                raise socket.timeout

    def send_ack(self):
        self.send(ACTIONS.ACK)

    def load_status(self):
        action, params = self.exec_no_timeout_handling(ACTIONS.LOAD_STATUS)
        print("Status files: ")
        for file, error in params.items():
            if error is not None:
                print(f">>> {file}: \n{error}")

    def ping(self):
        start = time.time()
        success = self.exec_no_timeout_handling(action=ACTIONS.PING, log=True)
        if not success:
            raise RuntimeError(
                "Socket connection broken or server wrong configured")
        ping_time = time.time() - start
        self.log(f"Ping: {ping_time:2f}s")
        return ping_time

    def put(self, filepath, new_filepath):
        with open(filepath, "rb") as f:
            file_txt = f.read()
        success = self.exec_no_timeout_handling(action=ACTIONS.PUT, params=[
            new_filepath, file_txt], log=False)
        if success:
            logging.info(f"Synced {filepath} to {new_filepath}")
        else:
            logging.error(f"Error when syncing: {filepath} to {new_filepath}")

    def sync_dir(self, all=False):
        last_sync_path = os.path.join(Config.PATH_DATA, ".last_sync")
        if os.path.exists(last_sync_path):
            with open(last_sync_path) as f:
                last_sync = float(f.read())
        else:
            last_sync = 0
        synced_count = 0
        path_src = Config.PATH_PC if Config.USE_PC else Config.PATH_LAPTOP
        for root, dirs, files in os.walk(path_src):
            for file in files:
                filepath = os.path.join(root, file)
                last_modified = os.path.getmtime(filepath)
                new_filepath = filepath.replace(path_src, Config.PATH_PI)
                new_filepath = new_filepath.replace("\\", "/")
                if last_modified > last_sync or all:
                    self.put(filepath, new_filepath)
                    synced_count += 1

        os.makedirs(Config.PATH_DATA, exist_ok=True)
        with open(last_sync_path, "w") as f:
            f.write(str(time.time()))

        return synced_count

    @_check_connection
    def disconnect(self, action=ACTIONS.DISCONNECT):
        ack = self.exec_no_timeout_handling(action=action)
        if type(ack) != bool:
            pass
            # raise RuntimeError("Error when disconnecting")
        self.socket.close()
        self.connected = False
        self.log(type="div")
        self.log("You have disconnected successfully!", type="server")

    def exec_restart(self):
        self.disconnect(action=ACTIONS.RESTART)
        time.sleep(Config.DELAY_RECONNECTING)
        self.try_connect().start()

    def try_connect(self):
        def func():
            start_time = time.time()
            while (time.time() - start_time) < Config.TIMEOUT_RECONNECTING:
                if self.connect():
                    break
                time.sleep(Config.DELAY_RETRY_CONNECTING)
            if not self.connected:
                logging.error(
                    f"[Failed to reconnect within {Config.TIMEOUT_RECONNECTING}s]")
            return self.connected

        return Thread(target=func, daemon=True)

    def log(self, msg="", type="txt"):
        type_binding = "txt"
        if type == "txt":
            txt = f">>> {msg}"
        elif type == "recv":
            txt = f"Rx: {msg}"
        elif type == "sent":
            txt = f"Tx: {msg}"
        elif type == "server":
            txt = f"[{msg}]"
        elif type == "div":
            txt = 60*"-"
        elif type == "error":
            txt = f"!!!{msg}!!!"
            type_binding = "error"
        else:
            txt = "Wrong log type"
            type_binding = "error"
        if type == "error":
            logging.error(txt)
        else:
            logging.info(txt)
        for log_binding in self.log_bindings:
            log_binding(msg=txt, type=type)

    def bind_log(self, func):
        self.log_bindings.append(func)
