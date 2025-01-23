import grpc
import csv
from usap_smc.utils.utils import get_ip_by_hostname

from usap_smc.logger.logger import Log
from usap_smc.pb import xapp_pb2
from usap_smc.pb import xapp_pb2_grpc
from usap_smc.ml_model.model import Model
from usap_smc.core5g.database import Database

from loguru import logger


def save_latency_iteratively(latency, message_id):
    with open('latencias.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Se o arquivo estiver vazio, escreve o cabeçalho
            writer.writerow(['Mensagem', 'Latência (ms)'])
        writer.writerow([message_id, latency])
    logger.info(f"Latência salva: {latency} ms, Mensagem: {message_id}")


class Client(object):
    def __init__(self):
        # Endereço do servidor
        # TODO: obter a partir de configuração/values.yaml
        server_ip = get_ip_by_hostname(
            "service-ricxapp-usap-xapp-grpc.ricxapp.svc")
        server_port = "5052"
        self.server_address = server_ip + ":" + server_port

        # Model
        self.model = Model()

        # Core
        self.core5g = Database()

    async def run(self) -> None:
        # Cria o canal gRPC
        async with grpc.aio.insecure_channel(self.server_address) as channel:
            # Cria o stub do serviço
            stub = xapp_pb2_grpc.UeMeasIndicationStub(channel)

            # Faz a chamada de stream
            try:
                # Configura o request
                request = xapp_pb2.StreamUeMetricsRequest(client_id="usap-smc")
                response_stream = stub.StreamUeMetrics(request)

                logger.info("Conectado ao servidor. Aguardando métricas...")

                # Processa o stream de respostas
                features = ['DRB.UEThpDl', 'DRB.UEThpUl',
                            'RRU.PrbUsedDl', 'RRU.PrbUsedUl']
                buffer = {}
                message_id = 0  # Contador de mensagens

                async for response in response_stream:
                    # Incrementa o id da mensagem
                    message_id += 1

                    # Captura e armazena a latência
                    latency = response.latency_ms

                    # Salva a latência de forma iterativa
                    # save_latency_iteratively(latency, message_id)

                    logger.info(f"Timestamp: {latency} ms")

                    # Processa as métricas
                    for ue in response.ueList:
                        # Inicializar o buffer por UE IMSI
                        if ue.imsi not in buffer:
                            buffer[ue.imsi] = []

                        meas_dict = {feature: 0 for feature in features}

                        for meas in ue.ueMeas:
                            meas_value = None
                            if meas.HasField("valueInt"):
                                meas_value = meas.valueInt
                            elif meas.HasField("valueReal"):
                                meas_value = meas.valueReal
                            elif meas.HasField("noValue"):
                                meas_value = "No Value"
                            logger.debug(
                                f"  MeasName: {meas.measName}, MeasValue: {meas_value}")

                            if meas.measName in features:
                                meas_dict[meas.measName] = meas_value

                        prb_sum = meas_dict['RRU.PrbUsedDl'] + \
                            meas_dict['RRU.PrbUsedUl']
                        buffer[ue.imsi].append([
                            meas_dict['DRB.UEThpDl'],
                            meas_dict['DRB.UEThpUl'],
                            prb_sum
                        ])

                        # Chama a função de inferência se o buffer estiver cheio
                        if len(buffer[ue.imsi]) == 2:
                            # Chama a função de inferência (TODO: dá pra fazer com multi thread ??)
                            sst_inference = self.model.get_sst_inference(
                                buffer[ue.imsi], ue.imsi)  # np.int64

                            # Verifica se a UE já está no slice inferido
                            if self.core5g.check_ue_in_slice(ue.imsi, sst_inference):
                                logger.warning(
                                    f"UE {ue.imsi} is already in slice with SST {sst_inference}, ignoring...")
                            else:
                                # TODO: update UE slice
                                logger.info(
                                    f"UE slice ({ue.imsi}) updated to SST {sst_inference}")

                            # Limpa o buffer após o uso
                            buffer[ue.imsi].clear()

            except grpc.RpcError as e:
                logger.error(
                    f"Falha ao receber o stream: {e.details()} (Status: {e.code()})")

    def stop(self):
        self.model.stop()
        self.core5g.stop()
