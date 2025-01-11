import argparse
import signal
import threading
import sys

from usap.config.config import Config
from usap.usap_xapp.usap_xapp import UsapXapp


class App(object):
    def __init__(self, configPath):
        self.config = Config('usap-xapp', configPath)  # Get config class
        self.logger = self.config.get_logger()  # Get Logger
        self.usap_xapp = UsapXapp()  # Get xApp Class

    def signal_handler(self, signum, frame):
        self.logger.warning(f"""Received signal: {
                            signum} ({signal.Signals(signum).name})""")

        # List all active threads
        threads = threading.enumerate()
        self.logger.debug(f"""Active threads at signal time: {
            [t.name for t in threads]}""")

        self.stop()

    def start(self):
        # Thread to run usap_xapp
        self.usap_xapp_thread = threading.Thread(target=self.usap_xapp.start)
        self.usap_xapp_thread.start()

    def stop(self):
        self.logger.warning(f"Stopping USAP application!")
        self.usap_xapp.stop()

        # Wait until the thread terminates
        if self.usap_xapp_thread is not None:
            self.usap_xapp_thread.join()

        # sys.exit(0)


def run():
    # Get xapp arguments
    parser = argparse.ArgumentParser(description="usap-xapp args")

    parser.add_argument('--config', type=str, dest='config',
                        default='/usr/src/usap-xapp/config/config-file.json', help='xApp config file path')

    args = parser.parse_args()
    configPath = args.config

    app = App(configPath)

    # add signal handler
    signal.signal(signal.SIGQUIT, app.signal_handler)
    signal.signal(signal.SIGTERM, app.signal_handler)
    signal.signal(signal.SIGINT, app.signal_handler)

    # Start operations
    app.start()
