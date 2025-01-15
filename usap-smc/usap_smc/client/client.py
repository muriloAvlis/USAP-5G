import grpc

from usap_smc.logger.logger import Log
from usap_smc.pb import xapp_pb2
from usap_smc.pb import xapp_pb2_grpc

logger = Log().get_logger()


def run_client():
    # Endereço do servidor
    server_address = "0.0.0.0:5051"

   # Cria o canal gRPC
    with grpc.insecure_channel(server_address) as channel:
        # Cria o stub do serviço
        stub = xapp_pb2_grpc.UeMeasIndicationStub(channel)
        # Configura o request
        request = xapp_pb2.StreamUeMetricsRequest(client_id="usap-smc")

        # Faz a chamada de stream
        try:
            response_stream = stub.StreamUeMetrics(request)
            logger.info("Conectado ao servidor. Recebendo métricas...")

            # Processa o stream de respostas
            for response in response_stream:
                logger.info(f"Timestamp: {response.timestamp_ms} ms")
                for ue in response.ueList:
                    logger.debug(
                        f"UE ID: {ue.ueID}, Granul. Period: {ue.granulPeriod}")
                    for meas in ue.ueMeas:
                        meas_value = None
                        if meas.HasField("valueInt"):
                            meas_value = meas.valueInt
                        elif meas.HasField("valueFloat"):
                            meas_value = meas.valueFloat
                        elif meas.HasField("noValue"):
                            meas_value = "No Value"
                        logger.debug(
                            f"  MeasName: {meas.measName}, MeasValue: {meas_value}")

        except grpc.RpcError as e:
            logger.error(
                f"Erro ao receber stream: {e.details()} (Status: {e.code()})")


if __name__ == "__main__":
    run_client()
