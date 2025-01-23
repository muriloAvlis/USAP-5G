import sys
import signal
import asyncio

from usap_smc.logger.logger import Log
from usap_smc.client.client import Client

logger = Log().get_logger()


class App(object):
    def __init__(self):
        self.client = Client()

    def signal_handler(self, sig, frame):
        """Handle graceful shutdown on SIGINT or SIGTERM."""
        logger.info(
            "Signal received: %s. Shutting down server gracefully.", sig)
        self.client.stop()
        sys.exit(0)

    def Start(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Start client
        asyncio.run(self.client.run())


def run():
    logger.info("Starting usap-smc application...")

    # Call App class to start processes
    app = App()
    app.Start()
