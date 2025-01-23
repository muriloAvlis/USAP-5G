from usap_smc.logger.logger import Log
import socket
import os
import signal
import sys


from loguru import logger


def get_ip_by_hostname(hostname) -> str:
    try:
        ip_addr = socket.gethostbyname(hostname)
        return ip_addr
    except socket.gaierror as e:
        logger.error(f"Error to resolve hostname {hostname}: {e}")
        signal.raise_signal(signal.SIGINT)
        return None
