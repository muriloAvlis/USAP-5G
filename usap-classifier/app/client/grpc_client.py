import asyncio
import logging
import grpc
from ..pb import xapp_pb2
from ..pb import xapp_pb2_grpc

logger = logging.getLogger(__name__)


def getE2Nodes():
    try:
        # gRPC channel
        channel = grpc.insecure_channel('localhost:5051')

        # gRPC stub to access services
        stub = xapp_pb2_grpc.E2NodesInfoServiceStub(channel)

        # request
        request = xapp_pb2.EmptyRequest()

        # response
        response = stub.getE2Nodes(request)

        # Show results
        print(f"Number of E2 nodes: {response.len}")
        for node in response.e2Node:
            print(f"Node ID Type: {node.id.type}")
            print(f"Node MCC: {node.id.plmn.mcc}, MNC: {
                node.id.plmn.mnc}, MNC Digit Length: {node.id.plmn.mnc_digit_len}")
            print(f"Node GNB ID: {node.id.nb_id.nb_id}")
            print(f"CU/DU ID: {node.id.cu_du_id}")
            print(f"Len CCA: {node.len_cca}")
            print("-" * 30)
    except grpc.RpcError as e:
        print(f"gRPC failed with {e.code()}: {e.details()}")


async def collectIndStyle4Metrics():
    async with grpc.aio.insecure_channel("localhost:5051") as ch:
        stub = xapp_pb2_grpc.KPMIndicationServiceStub(ch)
        while True:
            try:
                # Log de conexão
                logger.info("Conectando ao servidor gRPC...")
                # Request
                request = xapp_pb2.EmptyRequest()
                # Log para indicar envio de request
                logger.info("Enviando requisição ao servidor...")
                # Response
                async for response in stub.IndicationStyle4Stream(request):
                    print("Header:")
                    # show response
                    # Header
                    print("\tCollect Time [us]:", response.collectTime)
                    print("\tMessage Counter:", response.messageCounter)
                    # UE IDs
                    ue_ids = response.ueIds
                    print("UE IDs:")
                    print(f"\tamfUeNgapId: {ue_ids.amfUeNgapId}")
                    print(f"\tranUeId: {ue_ids.ranUeId}")
                    print(f"\tgnbCuCpUeE1apId: {ue_ids.gnbCuCpUeE1apId}")
                    print(f"\tgnbCuUeF1apId: {ue_ids.gnbCuUeF1apId}")
                   # List metrics
                    print("Measurements:")
                    for int_metric in response.reported_meas.int_metrics:
                        print(f"\t{int_metric.name}: {int_metric.value}")
                    for real_metric in response.reported_meas.real_metrics:
                        print(f"\t{real_metric.name}: {real_metric.value}")
                    print(50*"-")

            except grpc.aio.AioRpcError as e:
                logger.error(f"gRPC Error: {e.code()} - {e.details()}")
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    logger.error(
                        "Service usap-xapp unavailable, trying in 5 seconds...")
                    await asyncio.sleep(5)
                else:
                    logger.error(f"Unexpected gRPC error: {e}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
