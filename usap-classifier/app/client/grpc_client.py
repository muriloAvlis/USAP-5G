import asyncio
import logging
import grpc
from ..pb import xapp_pb2
from ..pb import xapp_pb2_grpc

logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, server_addr: str, server_port: int):
        self.server_addr = server_addr
        self.server_port = server_port

    async def get_kpm_indication(self):
        async with grpc.aio.insecure_channel(f"{self.server_addr}:{self.server_port}") as ch:
            # gRPC service stub
            stub = xapp_pb2_grpc.E2SM_KPM_ServiceStub(ch)

            logger.info(f'''Connecting to gRPC server {self.server_addr}:{
                        self.server_port} to get KPM indication stream''')

            try:
                # Prepare request
                request = xapp_pb2.KPMIndicationRequest(
                    svc_name="usap-classifier")

                # Make requisition
                response_stream = stub.GetIndicationStream(request)

                async for res in response_stream:
                    logger.info(f"Receiving KPM indication: {res}")
            except grpc.aio.AioRpcError as e:
                logger.error(f"Error to call gRPC service: {e.details()}")
