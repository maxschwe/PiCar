import socket
import logging
import os
import sys
import traceback

from .config import Config
from .actions import ACTIONS
from .tcp_handler import TcpHandler


class TcpServer:
    def __init__(self, port):
        self.port = port
        self.action_map = {ACTIONS.RESTART: [self.restart, {}]}

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def register_blueprint(self, blueprint):
        self.action_map.update(blueprint.get_action_map())

    def run(self):
        try:
            self.server.bind((Config.SERVER, self.port))
            self.server.listen()
        except:
            logging.error(f"[Server could not be started on port {self.port}]")
            logging.error(traceback.format_exc())
            raise RuntimeError

        self.running = True
        logging.info(f"[Server is listening on port {self.port}]")

        self.handlers = []
        while self.running:
            conn, addr = self.server.accept()
            # Start handler for client
            handler = TcpHandler(conn, addr, self.action_map, daemon=True)
            handler.start()
            self.handlers.append(handler)
        self.stop_server()

    def stop_server(self):
        self.server.close()
        self.server.detach()

    def restart(self):
        self.stop_server()
        logging.info("[Server is shutting down and will be restarted]")
        print(5 * "...\n")

        # restart script
        os.execv(sys.executable, ['python3'] + sys.argv)
