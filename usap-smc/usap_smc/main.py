import sys
import signal
import asyncio

from loguru import logger
from usap_smc.logger.logger import Log
from usap_smc.client.client import Client


class App(object):
    def __init__(self):
        # Add signal handler
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        self.client = Client()

    def signal_handler(self, sig, frame):
        """Handle graceful shutdown on SIGINT or SIGTERM."""
        logger.info(
            "Signal received: %s. Shutting down application gracefully.", sig)

        if hasattr(self, 'client'):
            self.client.stop()
        sys.exit(0)

    def Start(self):
        # Start client
        asyncio.run(self.client.run())


def run():
    Log().configure()

    logger.info("Iniciando módulo USAP-SMC...")

    # Call App class to start processes
    app = App()
    app.Start()
