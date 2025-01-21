import sys
import signal

from usap_smc.logger.logger import Log

logger = Log().get_logger()


class App(object):
    def __init__(self):
        pass

    def signal_handler(self, sig, frame):
        """Handle graceful shutdown on SIGINT or SIGTERM."""
        logger.info(
            "Signal received: %s. Shutting down server gracefully.", sig)
        sys.exit(0)

    def Start(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # TODO


def run():
    logger.info("Starting usap-e2ap application...")

    # Call App class to start processes
    app = App()
    app.Start()
