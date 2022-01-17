from .configuration import Config, ACTION, RETURN

if True:
    config = Config()

from .server import TcpServer
from .routes import blueprints


def get_server():
    server = TcpServer()
    for blueprint in blueprints:
        server.register_blueprint(blueprint)
    return server
