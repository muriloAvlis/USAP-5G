import grpc
import time
import os

import pandas as pd
import numpy as np
from usap_smc.utils.utils import get_ip_by_hostname
from usap_smc.logger.logger import Log
from usap_smc.pb import xapp_pb2
from usap_smc.pb import xapp_pb2_grpc
from usap_smc.ml_model.model import Model
from usap_smc.core5g.database import Database

from loguru import logger


class Client(object):
    def __init__(self):
        # Endereço do servidor
        # TODO: obter a partir de configuração/values.yaml
        server_ip = get_ip_by_hostname(
            "service-ricxapp-usap-xapp-grpc.ricxapp.svc")
        server_port = "5052"
        self.server_address = server_ip + ":" + server_port

        self.my_dir = os.path.dirname(os.path.abspath(__file__))

        # Model
        self.model = Model()

        # Core
        self.core5g = Database()

    def save_latencies(self, columns, latencies):
        df = pd.DataFrame(latencies, columns=columns)
        file_path = self.my_dir + \
            "/data/latencies.csv"
        df.to_csv(file_path, index=False)
        logger.info(f"Registros de latência salvos em {file_path}")

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

                message_count = 0  # Contador de mensagens
                latencies = np.empty((0, 5))

                async for response in response_stream:
                    # Calcula a latência de recebimento
                    recv_latency = (time.time() * 1000) - response.latency_ms

                    # Captura e armazena a latência
                    ind_latency = response.latency_ms

                    logger.info(f"Ind_latency: {ind_latency}")

                    logger.info(f"""msg_count={message_count}, recv_latency: {
                                recv_latency} ms""")

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
                                f"MeasName: {meas.measName}, MeasValue: {meas_value}")

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
                        if len(buffer[ue.imsi]) == 5:
                            # Chama a função de inferência (TODO: dá pra fazer com multi thread ??)
                            inference_time_start = time.time()
                            sst_inference = self.model.get_sst_inference(
                                buffer[ue.imsi], ue.imsi)  # np.int64
                            inference_time_stop = time.time()

                            sst_inference = int(sst_inference)

                            if sst_inference == 0:  # default slice
                                sst_inference = 128

                            inference_latency = (
                                inference_time_stop - inference_time_start) * 1000  # in ms
                            # Verifica se a UE já está no slice inferido
                            if self.core5g.check_ue_in_slice(ue.imsi, sst_inference):
                                logger.warning(
                                    f"UE {ue.imsi} is already in slice with SST {sst_inference}, ignoring...")
                            else:
                                alloc_time_start = time.time()
                                self.core5g.update_ue_slice_by_imsi(
                                    ue.imsi, sst_inference)
                                alloc_time_stop = time.time()

                                alloc_latency = (
                                    alloc_time_stop - alloc_time_start) * 1000  # in ms
                                logger.info(
                                    f"UE slice ({ue.imsi}) updated to SST {sst_inference}")

                            # Limpa o buffer após o uso
                            buffer[ue.imsi].clear()
                        else:
                            inference_latency = 0
                            alloc_latency = 0

                        # Até 1000 registros
                        if message_count <= 1000:
                            latencies = np.vstack([latencies, [
                                message_count, ind_latency, recv_latency, inference_latency, alloc_latency]])

                            # Incrementa o id da mensagem
                            message_count += 1
                        elif message_count == 1001:
                            columns = ["msg_count", "ind_latency", "recv_latency",
                                       "inference_latency", "alloc_latency"]
                            self.save_latencies(latencies, columns)

            except grpc.RpcError as e:
                logger.error(
                    f"Falha ao receber o stream: {e.details()} (Status: {e.code()})")

    def stop(self):
        self.model.stop()
        self.core5g.stop()
