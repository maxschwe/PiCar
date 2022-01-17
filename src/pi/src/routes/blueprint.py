import logging


class Blueprint:
    def __init__(self):
        self.action_map = {}

    def on(self, action):
        def handle_action(func):
            if action in self.action_map:
                logging.warning(
                    f"Overriding previously added function map for {action}")
            self.action_map[action] = func

            def wrap_func(*args, **kwargs):
                return func(*args, **kwargs)
            return wrap_func

        return handle_action

    def get_action_map(self):
        return self.action_map
