import logging


class MockLogger(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)
        self.messages = []

    def get_messages(self, level):
        return [
            message_text
            for message_level, message_text in self.messages
            if message_level == level
        ]

    def emit(self, record):
        self.messages.append((record.levelname, record.getMessage().rstrip()))

    def __enter__(self):
        logging.root.addHandler(self)
        self.old_level = logging.root.level
        logging.root.setLevel(logging.DEBUG)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logging.root.removeHandler(self)
        logging.root.setLevel(self.old_level)
