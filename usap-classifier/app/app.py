import asyncio
from .logger import logger

from .client import grpc_client

reportingPeriod = 1000
granularityPeriod = 1000


async def main() -> None:
    await grpc_client.collectIndStyle4Metrics()
    # grpc_client.getE2Nodes()


def run() -> None:
    # Init app logger
    logger.configLogger()

    asyncio.run(main())
