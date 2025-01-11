import sys
import signal

from usap_e2sm.server.server import Server
from usap_e2sm.logger.logger import Log


logger = Log().get_logger()


class App():
    def __init__(self):
        self.grpc_server = Server()
        self.logger = Log().get_logger()

    def signal_handler(self, sig, frame):
        """Handle graceful shutdown on SIGINT or SIGTERM."""
        self.logger.info(
            "Signal received: %s. Shutting down server gracefully.", sig)
        sys.exit(0)

    def start(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            self.grpc_server.Start()
        except Exception as e:
            self.logger.error(
                "Error while running the gRPC server: {}", str(e))
            sys.exit(1)


def run():
    logger.info("Starting usap-e2ap application...")

    app = App()

    app.start()
