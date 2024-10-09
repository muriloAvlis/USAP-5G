import asyncio
import argparse

from .logger import logger
from .client import grpc_client


async def main(args) -> None:
    client = grpc_client.Client(args.server_address, args.server_port)

    await client.get_kpm_indication()


def run() -> None:
    # process args
    parse = argparse.ArgumentParser(description="USAP-Classifier arguments")
    parse.add_argument("--server-address", dest="server_address", type=str,
                       help="gRPC server address to connect classifier", default="127.0.0.1")
    parse.add_argument("--server-port", dest="server_port",
                       type=int, help="gRPC server port", default=5051)

    args = parse.parse_args()

    # Init app logger
    logger.configLogger()

    asyncio.run(main(args))
