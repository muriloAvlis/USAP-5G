import sys
import signal

from usap_e2sm.server.server import Server
from loguru import logger
from usap_e2sm.logger.logger import Log


class App():
    def __init__(self):
        self.grpc_server = Server()

    def signal_handler(self, sig, frame):
        """Handle graceful shutdown on SIGINT or SIGTERM."""
        logger.info(
            "Signal received: %s. Shutting down server gracefully.", sig)
        sys.exit(0)

    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            self.grpc_server.Start()
        except Exception as e:
            logger.error(
                "Error while running the gRPC server: {}", str(e))
            sys.exit(1)


def run():
    Log().configure()

    logger.info("Starting usap-e2ap application...")

    app = App()

    app.start()
