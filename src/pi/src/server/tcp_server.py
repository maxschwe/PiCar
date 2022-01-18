import socket
import logging

from .tcp_handler import TcpHandler
from .. import config


class TcpServer:
    def __init__(self):
        self.running = True
        self.action_map = {}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def register_blueprint(self, blueprint):
        self.action_map.update(blueprint.get_action_map())
        logging.info(f"[Updated action map: {self.action_map}]")

    def run(self):
        self.socket.bind(config.ADDR)
        self.socket.listen()
        logging.info(f"[Server is listening on port {config.PORT}]")
        self.handlers = []
        while self.running:
            conn, addr = self.socket.accept()
            # Start handler for client
            handler = TcpHandler(conn, addr, self.action_map)
            handler.start()
            self.handlers.append(handler)
