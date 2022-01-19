import socket
import logging
import os
import sys

from .tcp_handler import TcpHandler
from .. import config, ACTION


class TcpServer:
    def __init__(self):
        self.running = False
        self.action_map = {ACTION.RESTART: [self.restart, {}]}

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def register_blueprint(self, blueprint):
        self.action_map.update(blueprint.get_action_map())
        # logging.info(f"[Updated action map: {self.action_map}]")

    def run(self):
        for port in config.PORT:
            try:
                self.socket.bind((config.SERVER, port))
                self.running = True
                break
            except:
                pass
        if not self.running:
            logging.error("Could not start server")
            return
        self.socket.listen()
        logging.info(f"[Server is listening on port {port}]")
        self.handlers = []
        while self.running:
            conn, addr = self.socket.accept()
            # Start handler for client
            handler = TcpHandler(conn, addr, self.action_map)
            handler.start()
            self.handlers.append(handler)

    def restart(self):
        self.socket.close()
        self.socket.detach()
        logging.info("[Server is shutting down and will be restarted]")
        print(5 * (100*"_" + "\n"))
        os.execv(sys.executable, ['python'] + sys.argv)
