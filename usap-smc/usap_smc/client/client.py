import grpc
import asyncio
import numpy as np
import csv
from tensorflow.keras.models import load_model

from usap_smc.logger.logger import Log
from usap_smc.pb import xapp_pb2
from usap_smc.pb import xapp_pb2_grpc
from usap_smc.core5g.ia_model.IA_module import run_ia_task

logger = Log().get_logger()

# Função para salvar latências de forma iterativa no CSV
def save_latency_iteratively(latency, message_id):
    with open('latencias.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        if file.tell() == 0:  # Se o arquivo estiver vazio, escreve o cabeçalho
            writer.writerow(['Mensagem', 'Latência (ms)'])
        writer.writerow([message_id, latency])
    logger.info(f"Latência salva: {latency} ms, Mensagem: {message_id}")

# Função principal do cliente assíncrono
async def run_client() -> None:
    # Endereço do servidor
    server_address = "10.126.1.141:30052"

    # Cria o canal gRPC
    async with grpc.aio.insecure_channel(server_address) as channel:
        # Cria o stub do serviço
        stub = xapp_pb2_grpc.UeMeasIndicationStub(channel)

        # Faz a chamada de stream
        try:
            # Configura o request
            request = xapp_pb2.StreamUeMetricsRequest(client_id="usap-smc")
            response_stream = stub.StreamUeMetrics(request)

            logger.info("Conectado ao servidor. Recebendo métricas...")

            # Processa o stream de respostas
            features = ['DRB.UEThpDl', 'DRB.UEThpUl', 'RRU.PrbUsedDl', 'RRU.PrbUsedUl']
            buffer = []
            message_id = 0  # Contador de mensagens

            async for response in response_stream:
                # Incrementa o id da mensagem
                message_id += 1

                # Captura e armazena a latência
                latency = response.latency_ms

                # Salva a latência de forma iterativa
                save_latency_iteratively(latency, message_id)

                logger.info(f"Timestamp: {latency} ms")

                # Processa as métricas
                for ue in response.ueList:
                    plmn = "00101"
                    zeros = "0000000"
                    ueid_enumerated = ue.ueID + 1
                    convert = str(ueid_enumerated).zfill(3)
                    convert_ueid = plmn + zeros + convert

                    logger.debug(f"UE ID: {convert_ueid[-1]}, Granul. Period: {ue.granulPeriod}, imsi: {convert_ueid}")

                    meas_dict = {feature: 0 for feature in features}

                    for meas in ue.ueMeas:
                        meas_value = None
                        if meas.HasField("valueInt"):
                            meas_value = meas.valueInt
                        elif meas.HasField("valueReal"):
                            meas_value = meas.valueReal
                        elif meas.HasField("noValue"):
                            meas_value = "No Value"
                        logger.debug(f"  MeasName: {meas.measName}, MeasValue: {meas_value}")

                        if meas.measName in features:
                            meas_dict[meas.measName] = meas_value

                    prb_sum = meas_dict['RRU.PrbUsedDl'] + meas_dict['RRU.PrbUsedUl']
                    buffer.append([
                        meas_dict['DRB.UEThpDl'],
                        meas_dict['DRB.UEThpUl'],
                        prb_sum
                    ])

                    # Chama a função de inferência se o buffer estiver cheio
                    if len(buffer) == 2:
                        run_ia_task(buffer, convert_ueid)  # Chama a função de inferência
                        buffer.clear()  # Limpa o buffer após o uso

        except grpc.RpcError as e:
            logger.error(f"Falha ao receber o stream: {e.details()} (Status: {e.code()})")

# Função principal para iniciar o cliente assíncrono
if __name__ == "__main__":
    asyncio.run(run_client())
