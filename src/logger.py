import logging


class Logger:
    def __init__(self):
        self.core = logging.basicConfig(filename='', level=logging.INFO)

