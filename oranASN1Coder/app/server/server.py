from concurrent import futures
import grpc
import logging
from .proto import e2sm_pb2
from .proto import e2sm_pb2_grpc
from ..e2sm_wrapper import e2sm_kpm_wrapper
from .configs import ExceptionToStatusInterceptor
from grpc_reflection.v1alpha import reflection


class RanFuncDefDecoder(e2sm_pb2_grpc.RanFuncDefDecoderServicer):
    def __init__(self) -> None:
        self.kpm_wrapper = e2sm_kpm_wrapper.e2sm_kpm_wrapper()

    def getMeasListbyRicReportStyle(self, request, context):
        encodedRanFunctionDefinition = request.encodedRanFunctionDefinition
        ReportStyleType = request.ReportStyleType

        # Decode RAN function description
        ran_func_description = self.kpm_wrapper.decode_ran_function_description(
            encodedRanFunctionDefinition)

        # get Meas Name List from RAN Function Definition and report style
        measList = self.kpm_wrapper.get_meas_name_list_by_ric_report_style(
            ran_func_description, ReportStyleType)

        return e2sm_pb2.MeasListResponse(measList=measList)


class ActDefEncoder(e2sm_pb2_grpc.ActDefEncoderServicer):
    def __init__(self) -> None:
        self.kpm_wrapper = e2sm_kpm_wrapper.e2sm_kpm_wrapper()

    def encodeActionDefinitionFmt4(self, request, context):
        measNameList = [str(i) for i in request.measNameList]
        granularityPeriod = request.granularityPeriod

        # Encode Action Definition Format 4
        encodedActionDefinition = self.kpm_wrapper.encode_action_definition_fmt_4(
            measNameList, granularityPeriod)

        return e2sm_pb2.EncodedActDefResponse(encodedActionDefinition=encodedActionDefinition)


class EventTriggerFmtEncoder(e2sm_pb2_grpc.EventTriggerFmtEncoder):
    def __init__(self) -> None:
        self.kpm_wrapper = e2sm_kpm_wrapper.e2sm_kpm_wrapper()

    def encodeEventTriggerFmt1(self, request, context):
        reportingPeriod = request.reportingPeriod

        # Encode Event Trigger Definition Format 1
        encodedEventTriggerDefinition = self.kpm_wrapper.encode_event_trigger_def_fmt_1(
            reportingPeriod)

        return e2sm_pb2.EncodedEventTriggerDefResponse(encodedEventTriggerDefinition=encodedEventTriggerDefinition)


def run_server():
    # Configure logger
    logging.basicConfig(level=logging.INFO)

    server = grpc.server(futures.ThreadPoolExecutor(
        max_workers=10), interceptors=[ExceptionToStatusInterceptor()])
    # Add services implementations to server
    # Meas List Decoder
    e2sm_pb2_grpc.add_RanFuncDefDecoderServicer_to_server(
        RanFuncDefDecoder(), server)

    # Action Definition Encoder
    e2sm_pb2_grpc.add_ActDefEncoderServicer_to_server(
        ActDefEncoder(), server)

    # Event Trigger Definition Encoder
    e2sm_pb2_grpc.add_EventTriggerFmtEncoderServicer_to_server(
        EventTriggerFmtEncoder(), server)

    SERVICE_NAMES = (
        e2sm_pb2.DESCRIPTOR.services_by_name["RanFuncDefDecoder"].full_name,
        e2sm_pb2.DESCRIPTOR.services_by_name["ActDefEncoder"].full_name,
        e2sm_pb2.DESCRIPTOR.services_by_name["EventTriggerFmtEncoder"].full_name,
        reflection.SERVICE_NAME,
    )

    # Enable server reflection
    reflection.enable_server_reflection(SERVICE_NAMES, server)

    # Set server port
    severAddr = "0.0.0.0:5051"
    server.add_insecure_port(severAddr)

    # Start gRPC server
    server.start()

    logging.info(f"gRPC server running on port {severAddr}")

    server.wait_for_termination()
