import grpc
import asyncio
import numpy as np
from tensorflow.keras.models import load_model

from usap_smc.logger.logger import Log
from usap_smc.pb import xapp_pb2
from usap_smc.pb import xapp_pb2_grpc
from usap_smc.core5g.ia_model.IA_module import run_ia_task
#from usap_smc.core5g.ia_model.IA_module import MODEL

logger = Log().get_logger()
#model = load_model("/home/victor/usap-5g/usap-smc/usap_smc/core5g/ia_model/lstm-oran.keras")

async def run_client() -> None:
    # Endereço do servidor
    #server_address = "service-ricxapp-usap-xapp-grpc.ricxapp.svc.cluster.local:5052"
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
            # async for response in response_stream:
            #     logger.info(f"Timestamp: {response.latency_ms} ms")
            #     for ue in response.ueList:
            #         logger.debug(
            #             f"UE ID: {ue.ueID}, Granul. Period: {ue.granulPeriod}")
            #         for meas in ue.ueMeas:
            #             meas_value = None
            #             if meas.HasField("valueInt"):
            #                 meas_value = meas.valueInt
            #             elif meas.HasField("valueReal"):
            #                 meas_value = meas.valueReal
            #             elif meas.HasField("noValue"):
            #                 meas_value = "No Value"
            #             logger.debug(
            #                 f"  MeasName: {meas.measName}, MeasValue: {meas_value}")
            features = ['DRB.UEThpDl', 'DRB.UEThpUl', 'RRU.PrbUsedDl', 'RRU.PrbUsedUl']

            buffer = []

            async for response in response_stream:
                logger.info(f"Timestamp: {response.latency_ms} ms")

                for ue in response.ueList:
                    plmn = "00101"
                    zeros = "0000000"
                    ueid_enumerated = ue.ueID + 1
                    convert = str(ueid_enumerated).zfill(3)
                    global convert_ueid
                    convert_ueid = None
                    convert_ueid = plmn + zeros + convert

                    #logger.debug(f"UE ID: {ue.ueID}, Granul. Period: {ue.granulPeriod}, imsi: {convert_ueid}")
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
                        logger.debug(
                            f"  MeasName: {meas.measName}, MeasValue: {meas_value}")

                        if meas.measName in features:
                            meas_dict[meas.measName] = meas_value

                    prb_sum = meas_dict['RRU.PrbUsedDl'] + meas_dict['RRU.PrbUsedUl']
                    buffer.append([
                        meas_dict['DRB.UEThpDl'],
                        meas_dict['DRB.UEThpUl'],
                        prb_sum
                    ])


                    # if len(buffer) == 2:
                    #     #X = np.array(buffer)
                    #     #entrada = np.expand_dims(X, axis=0)
                    #     #saida = np.argmax(model.predict(entrada), axis=1)
                    #     #logger.info(f"Entrada modelo:\n{X}")
                    #     #logger.info(f"Entrada modelo convertida:\n{entrada}")
                    #     #logger.info(f"Predição modelo: {saida}")
                    #     buffer = []
                    #     hold = buffer
                    if len(buffer) == 2:  # Quando o buffer está cheio
                        #logger.info(f"Buffer preenchido: {buffer}")
                        run_ia_task(buffer,convert_ueid)  # Chama a função de inferência
                        buffer.clear()  # Limpa o buffer após o uso


        except grpc.RpcError as e:
            logger.error(
                f"Fail to receive stream: {e.details()} (Status: {e.code()})")


if __name__ == "__main__":
    asyncio.run(run_client())
