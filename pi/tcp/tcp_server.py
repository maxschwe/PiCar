import socket
import logging
import os
import sys
import traceback
import time

from .config import Config
from .actions import ACTIONS
from .tcp_handler import TcpHandler
from routes import blueprints


class TcpServer:
    def __init__(self):
        self.action_map = {
            "server-global": {ACTIONS.RESTART: self.restart, ACTIONS.LOAD_STATUS: self.load_status},
            "files": {blueprint.file_map: blueprint.get_action_map() for blueprint in blueprints}
        }
        print(self.action_map)
        self.robot_error = None
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def run(self):
        self.running = False
        for port in range(Config.PORT[0], Config.PORT[0] + Config.PORT[1]):
            try:
                self.server.bind((Config.SERVER, port))
                self.server.listen()
                self.running = True
                self.port = port
                break
            except:
                logging.warning(f"[Failed to start server on port {port}]")

        if not self.running:
            raise RuntimeError("Server could not get started!")
        logging.info(f"[Server is listening on port {self.port}]")

        self.handlers = []
        while self.running:
            conn, addr = self.server.accept()
            # Start handler for client
            logging.info(f"[Client {addr} connected]")
            handler = TcpHandler(conn, addr, self.action_map, daemon=True)
            handler.start()
            self.handlers.append(handler)
        self.stop_server()

    def stop_server(self):
        self.server.close()
        self.server.detach()

    def restart(self, socket):
        socket.disconnect()
        self.stop_server()
        from robot.robot import Robot
        r = Robot.instance().camera.vs.stop()
        time.sleep(2)
        logging.info("[Server is shutting down and will be restarted]")
        print(5 * "...\n")

        # restart script
        os.execv(sys.executable, ['python3'] + sys.argv)

    def set_robot_error(self, error):
        self.robot_error = error

    def load_status(self, socket):
        data = {blueprint.file_map: blueprint.error for blueprint in blueprints}
        data["robot"] = self.robot_error
        socket.send(ACTIONS.LOAD_STATUS, params=data)
