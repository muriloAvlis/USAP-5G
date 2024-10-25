import asyncio
import argparse
import logging
import signal

from .logger import logger
from .kpimon import kpimon

log = logging.getLogger(__name__)


def signal_handler(signal, loop):
    log.info(f"""Received an exit signal {
             signal.name}, stopping pending event loops""")
    loop.stop()  # Stop the loop


async def main(args) -> None:
    client = kpimon.Client(args.server_address, args.server_port)

    await client.get_kpm_indication()


def run() -> None:
    # Process args (or use envs??)
    parse = argparse.ArgumentParser(description="USAP-Classifier arguments")
    parse.add_argument("--server-address", dest="server_address", type=str,
                       help="gRPC server address to connect classifier", default="10.126.1.142")
    parse.add_argument("--server-port", dest="server_port",
                       type=int, help="gRPC server port", default=5051)

    args = parse.parse_args()

    # Init app logger
    logger.configLogger()

    # Get app event loop
    loop = asyncio.get_event_loop()

    # Register app interrupt handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, signal_handler, sig, loop)

    # Start app
    try:
        loop.run_until_complete(main(args))
    finally:
        log.info("Finishing application...")
        loop.close()
