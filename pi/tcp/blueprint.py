import logging


class Blueprint:
    def __init__(self, file_map):
        self.action_map = {}
        self.file_map = file_map
        self.error = None

    def on(self, action):
        def handle_action(func):
            if action in self.action_map:
                logging.warning(
                    f"Overriding previously added function map for {action} in {self.file_map}")
            self.action_map[action] = func
            return func

        return handle_action

    def set_error(self, error):
        self.error = error

    def get_action_map(self):
        return self.action_map
