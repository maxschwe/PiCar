import logging
from threading import Thread
import math

from .. import config, ACTION, RETURN

# hello


class TcpHandler(Thread):
    def __init__(self, socket, addr, action_map, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.socket = socket
        self.addr = addr
        self.action_map = action_map
        self.connected = True

    def run(self):
        while self.connected:
            # accept request
            action, msg, ret_type = self.receive()

            # handle request
            self.handle_action(action, msg, ret_type)

            # self.log(type="div")

    def send(self, action, msg="", ret_type=RETURN.NONE, log=False):
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
        if config.LOG_HEADER:
            logging.info(
                f"Sent {action}, {msg_length} Bytes, {ret_type} to {self.addr}")

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
        if log:
            self.log(
                f"{action} - {msg[:15]}{'...' if msg_length > 15 else ''} ({msg_length} Bytes)", type="sent")

        # wait for ack if expected
        if ret_type == RETURN.ACK:
            return self.received_ack()
        else:
            return True

    def receive(self, log=False):
        action, msg_length, ret_type = self.recv_header()
        # recv msg if available
        if msg_length > 0:
            msg = self.recv_msg(msg_length, action)
        else:
            msg = ''
        if log:
            self.log(
                f"{action} - {msg[:15]}{'...' if msg_length > 15 else ''} ({msg_length} Bytes)", type="recv")
        return action, msg, ret_type

    def recv_header(self):
        header = self.socket.recv(8)
        if header == b'':
            raise RuntimeError("Socket connection broken")
        # decode header
        action = ACTION.decode(header[0])
        msg_length = int.from_bytes(header[1:7], byteorder='big')
        ret_type = RETURN.decode(header[7])
        return action, msg_length, ret_type

    def recv_msg(self, msg_length, action):
        kwargs = self.action_map[action][1]
        no_decoding = "no_decoding" in kwargs and kwargs["no_decoding"]
        recv_text = b""
        while msg_length > 0:
            recv_length = min(msg_length, config.MSG_LENGTH)
            new_txt = self.socket.recv(recv_length)
            recv_text += new_txt
            msg_length -= len(new_txt)
        if not no_decoding:
            recv_text = recv_text.decode(config.ENCODING)
        return recv_text

    def handle_action(self, action, msg, ret_type):
        if action == ACTION.DISCONNECT:
            self.disconnect(ret_type)
            return
        elif action == ACTION.RESTART:
            self.disconnect(ret_type)
            self.action_map[action][0]()

        elif action == ACTION.PING:
            pass
        elif action in self.action_map:
            func = self.action_map[action][0]
            var_names = func.__code__.co_varnames
            args = []
            kwargs = {}
            if "msg" in var_names:
                kwargs["msg"] = msg
            if "ret_type" in var_names:
                kwargs["ret_type"] = ret_type
            if "socket" in var_names:
                kwargs["socket"] = self
            # 1 unknown args -> take msg
            if len(var_names) == 2 and len(kwargs) < 1:
                args.append(msg)
            elif len(var_names) == 3 and len(kwargs) < 2:
                # 2 unknown args -> take msg, ret_type
                if not kwargs:
                    args.append(msg, ret_type)
                elif "msg" in kwargs:
                    args.append(ret_type)
                else:
                    args.append(msg)
            elif len(var_names) == 4 and len(kwargs) < 3:
                logging.error(
                    "Definition of Mapping function should have these kwargs: ['msg', 'ret_type', 'socket']. (Incorrect kwargs only supported for 1-2 parameters)")
            func(*args, **kwargs)
        else:
            logging.error(f"{action} is not mapped")

        # send ack if expected
        if ret_type == RETURN.ACK:
            self.send_ack()

    def received_ack(self):
        action, _, _ = self.recv_header()
        if action == ACTION.ACK:
            self.log(ACTION.ACK, type="recv")
            return True
        return False

    def send_ack(self):
        self.send(ACTION.ACK, ret_type=RETURN.NONE)

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

    def disconnect(self, ret_type):
        # send ack and disconnect
        if ret_type == RETURN.ACK:
            self.send_ack()
        self.connected = False
        self.socket.close()
        self.log(f"Client {self.addr} disconnected!", type="server")
