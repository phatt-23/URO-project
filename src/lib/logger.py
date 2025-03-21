import logging
import os
from datetime import datetime

from lib.types import Singleton

class Logger(Singleton):
    def __init__(self):
        LOG_DIR = "logs"
        os.makedirs(LOG_DIR, exist_ok=True)

        # generate a log filename based on the current date
        self.log_filepath = os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")

        # create a logger
        self.logger = logging.getLogger("AppLogger")
        self.logger.setLevel(logging.DEBUG)  # Change to INFO or WARNING for less verbosity

        # console handler (prints logs to terminal)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Only show important logs in console

        # file handler (logs all levels to a file)
        file_handler = logging.FileHandler(self.log_filepath, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)

        # log format
        formatter = logging.Formatter(
            "[%(levelname)s][%(asctime)s] - %(message)s", 
            # datefmt="%Y-%m-%d %H:%M:%S"
            datefmt="%H:%M:%S"
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # add handlers to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def log(self, level, *args, sep=" ", end="\n"):
        """Flexible logging similar to print()"""
        msg = sep.join(str(arg) for arg in args) + end.strip()
        self.logger.log(level, msg)

    def debug(self, *args, sep=" ", end="\n"):
        self.log(logging.DEBUG, *args, sep=sep, end=end)

    def info(self, *args, sep=" ", end="\n"):
        self.log(logging.INFO, *args, sep=sep, end=end)

    def warning(self, *args, sep=" ", end="\n"):
        self.log(logging.WARNING, *args, sep=sep, end=end)

    def error(self, *args, sep=" ", end="\n"):
        self.log(logging.ERROR, *args, sep=sep, end=end)

    def exception(self, *args, sep=" ", end="\n"):
        self.log(logging.ERROR, *args, sep=sep, end=end)
        self.logger.exception(sep.join(str(arg) for arg in args))

    def get_logger(self):
        return self.logger

log = Logger()


