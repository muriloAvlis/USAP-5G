import asyncio
import logging
import grpc
import numpy as np
from ..pb import xapp_pb2
from ..pb import xapp_pb2_grpc

log = logging.getLogger(__name__)


class Client(object):
    def __init__(self, server_addr: str, server_port: int):
        self.server_addr = server_addr
        self.server_port = server_port
        # ue_metrics["ue_id"] = {"metric_name": "metric_value"}
        self.amf_ue_ngap_id_lst = np.array([])
        self.ue_metrics = dict()

    # Update amf ue ngap ID list
    def __update_amf_ue_ngap_id_list(self, amf_ue_ngap_id: int):
        if not amf_ue_ngap_id in self.amf_ue_ngap_id_lst:
            self.amf_ue_ngap_id_lst = np.append(
                self.amf_ue_ngap_id_lst, amf_ue_ngap_id)

    # Find ue_id based in amf_ue_ngap_id
    def __get_ue_id_by_amf_ue_ngap_id(self, amf_ue_ngap_id: int) -> int:
        idx = np.where(self.amf_ue_ngap_id_lst == amf_ue_ngap_id)[0]
        if idx.size > 0:
            return idx[0] + 1
        return -1

    def __amf_ngap_id_to_imsi(self, amf_ue_ngap_id: int) -> str:
        plmn = "72470"  # 5 digits
        zeros = "0000000"  # 7 digits
        ue_id = self.__get_ue_id_by_amf_ue_ngap_id(amf_ue_ngap_id)

        if ue_id == -1:  # check if UE ID was found
            return "UE ID not found!"

        ue_id = str(ue_id).zfill(3)  # 3 digits
        imsi = plmn + zeros + ue_id  # 15 digits (3GPP standard)

        return imsi

    async def get_kpm_indication(self):
        async with grpc.aio.insecure_channel(f"{self.server_addr}:{self.server_port}") as ch:
            # gRPC service stub
            stub = xapp_pb2_grpc.E2SM_KPM_ServiceStub(ch)

            log.info(f'''Connecting to gRPC server {self.server_addr}:{
                self.server_port} to get KPM indication stream''')

            try:
                # Prepare request
                request = xapp_pb2.KPMIndicationRequest(
                    svc_name="usap-classifier")

                # Make requisition
                response_stream = stub.GetIndicationStream(request)

                async for res in response_stream:
                    # Update UE ID list
                    self.__update_amf_ue_ngap_id_list(
                        res.ue.ue_id.amf_ue_ngap_id)
                    # Get IMSI
                    imsi = self.__amf_ngap_id_to_imsi(
                        res.ue.ue_id.amf_ue_ngap_id)

                    # Update IMSI in dict if not exist
                    if imsi not in self.ue_metrics:
                        self.ue_metrics[imsi] = {}

                    for meas_info in res.ue.ue_meas_info:
                        meas_name = meas_info.meas_name

                        # Check if value is integer or double
                        if meas_info.HasField('int_value'):
                            meas_value = meas_info.int_value
                        elif meas_info.HasField('real_value'):
                            meas_value = meas_info.real_value
                        else:
                            log.warning(
                                "No measurement value set for meas_name: %s", meas_name)
                            continue

                       # Update UE metrics
                        self.ue_metrics[imsi][meas_name] = meas_value

                    log.debug(self.ue_metrics)

            except grpc.aio.AioRpcError as e:
                log.error(f"Error to call gRPC service: {e.details()}")
            except asyncio.CancelledError as e:
                log.error(f"Indication stream was cancelled: {e.details()}")
            finally:
                loop = asyncio.get_event_loop()
                if not loop.is_closed():
                    loop.stop()
                log.debug("kpimon finished")
