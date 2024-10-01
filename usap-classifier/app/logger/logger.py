import logging
import datetime
from colorama import Fore, Style, init

# init colorama
init(autoreset=True)


class CustomFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: "[%(asctime)s]" + Fore.CYAN + "[%(levelname)s]" + Style.RESET_ALL + "[%(filename)s:%(lineno)d] %(message)s",
        logging.INFO: "[%(asctime)s]" + Fore.GREEN + "[%(levelname)s]" + Style.RESET_ALL + "[%(filename)s:%(lineno)d] %(message)s",
        logging.WARNING: "[%(asctime)s]" + Fore.YELLOW + "[%(levelname)s]" + Style.RESET_ALL + "[%(filename)s:%(lineno)d] %(message)s",
        logging.ERROR: "[%(asctime)s]" + Fore.RED + "[%(levelname)s]" + Style.RESET_ALL + "[%(filename)s:%(lineno)d] %(message)s",
        logging.CRITICAL: "[%(asctime)s]" + Fore.MAGENTA + "[%(levelname)s]" +
        Style.RESET_ALL + "[%(filename)s:%(lineno)d] %(message)s"
    }

    date_format = "%Y-%m-%dT%H:%M:%S"

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=self.date_format)
        return formatter.format(record)


def configLogger():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove handlers if they exist
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Stream handler (console output)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(CustomFormatter())
    root_logger.addHandler(stream_handler)

    logging.debug("Logger initialized successfully.")
