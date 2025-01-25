import grpc
import json
import time

from concurrent import futures
from grpc_reflection.v1alpha import reflection
from usap_e2sm.pb import e2sm_pb2
from usap_e2sm.pb import e2sm_pb2_grpc
from usap_e2sm.asn1.e2sm.e2sm_kpm_packer import e2sm_kpm_packer

from loguru import logger


class EventTriggerService(e2sm_pb2_grpc.EventTriggerDefinitionServicer):
    def __init__(self, e2sm_kpm):
        self.e2sm_kpm = e2sm_kpm

    def EncodeEventTriggerDefFormat1(self, request, context):
        try:
            client_id = context.peer()
            logger.debug(
                f"Received request from: {client_id} to function: EncodeEventTriggerDefFormat1")

            response = self.e2sm_kpm.encode_event_trigger_def(
                request.reportingPeriod)
            return e2sm_pb2.EncodeEventTriggerResponse(eventTriggerDef=response)
        except Exception as e:
            context.set_details(f"Error: {str(e)}")
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            return e2sm_pb2.EncodeEventTriggerResponse()


class RanFunctionService(e2sm_pb2_grpc.RanFunctionDefinitionServicer):
    def __init__(self, e2sm_kpm):
        self.e2sm_kpm = e2sm_kpm

    def DecodeRanFunctionDefinition(self, request, context):
        try:
            client_id = context.peer()
            logger.debug(
                f"Received request from: {client_id} to function: DecodeRanFunctionDefinition")
            response = self.e2sm_kpm.decode_ran_function_definition(
                request.ranFuncDefinition)

            # Convert to json (need in proto)
            response = json.dumps(response)

            return e2sm_pb2.DecodeRanFunctionResponse(
                decodedRanFuncDef=response
            )
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            return e2sm_pb2.DecodeRanFunctionResponse()


class ActionDefinitionService(e2sm_pb2_grpc.ActionDefinitionServicer):
    def __init__(self, e2sm_kpm):
        self.e2sm_kpm = e2sm_kpm

    def EncodeActionDefinitionFormat4(self, request, context):
        try:
            client_id = context.peer()
            logger.debug(
                f"Received request from: {client_id} to function: EncodeActionDefinitionFormat4")

            matchingUeCondsList = None
            testCondInfo = request.matchingUEConds.testCondInfo

            # Check measType
            match testCondInfo.testCondValue.WhichOneof("value"):
                case "valueInt":
                    test_value = testCondInfo.testCondValue.valueInt
                    matchingUeCondsList = [{'testCondInfo': {'testType': (
                        testCondInfo.testType, 'true'), 'testExpr': testCondInfo.testExpr, 'testValue': ('valueInt', test_value)}}]
                case "valueEnum":
                    test_value = testCondInfo.testCondValue.valueEnum
                    matchingUeCondsList = [{'testCondInfo': {'testType': (
                        testCondInfo.testType, 'true'), 'testExpr': testCondInfo.testExpr, 'testValue': ('valueEnum', test_value)}}]
                case "valueBool":
                    test_value = testCondInfo.testCondValue.valueBool
                    matchingUeCondsList = [{'testCondInfo': {'testType': (
                        testCondInfo.testType, 'true'), 'testExpr': testCondInfo.testExpr, 'testValue': ('valueBool', test_value)}}]
                case "valueBitS":
                    test_value = testCondInfo.testCondValue.valueBitS
                    matchingUeCondsList = [{'testCondInfo': {'testType': (
                        testCondInfo.testType, 'true'), 'testExpr': testCondInfo.testExpr, 'testValue': ('valueBitS', test_value)}}]
                case "valueOctS":
                    test_value = testCondInfo.testCondValue.valueOctS
                    matchingUeCondsList = [{'testCondInfo': {'testType': (
                        testCondInfo.testType, 'true'), 'testExpr': testCondInfo.testExpr, 'testValue': ('valueOctS', test_value)}}]
                case "valuePrtS":
                    test_value = testCondInfo.testCondValue.valuePrtS
                    matchingUeCondsList = [{'testCondInfo': {'testType': (
                        testCondInfo.testType, 'true'), 'testExpr': testCondInfo.testExpr, 'testValue': ('valuePrtS', test_value)}}]
                case "valueReal":
                    test_value = testCondInfo.testCondValue.valueReal
                    matchingUeCondsList = [{'testCondInfo': {'testType': (
                        testCondInfo.testType, 'true'), 'testExpr': testCondInfo.testExpr, 'testValue': ('valueReal', test_value)}}]
                case _:
                    raise ValueError("No valid field set in testCondValue")

            encodedActDef = self.e2sm_kpm.encode_action_def_format4(
                matchingUeCondsList, request.measNameList, request.granularityPeriod)

            return e2sm_pb2.EncActDefResponse(actionDefinitionEnc=encodedActDef)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            return e2sm_pb2.EncActDefResponse()


class IndicationMessage(e2sm_pb2_grpc.IndicationMessageServicer):
    def __init__(self, e2sm_kpm):
        self.e2sm_kpm = e2sm_kpm

    def decodeIndicationMessage(self, request, context):
        try:
            client_id = context.peer()
            logger.debug(
                f"Received request from: {client_id} to function: decodeIndicationMessage")

            response = e2sm_pb2.DecodeIndMessageResponse()

            # Ind Header
            decodedIndHeader = self.e2sm_kpm.decode_indication_header(
                request.indicationHeader)

            collectStartTime = self.e2sm_kpm.extract_hdr_info(decodedIndHeader)[
                'colletStartTime']

            logger.info(f"""StartTime: {collectStartTime} | Timestamp: {
                        request.timestamp}""")

            timestamp = time.time() * 1000

            # Calcule latency
            response.latency_ms = timestamp - \
                collectStartTime

            # Ind Message
            decodedIndMessage = self.e2sm_kpm.decode_indication_message(
                request.indicationMessage)
            ueMeasList = self.e2sm_kpm.extract_meas_data(decodedIndMessage)

            for ueID, ueMeas in ueMeasList['ueMeasData'].items():
                ueMeasResponse = e2sm_pb2.UeMeasData()
                ueMeasResponse.UEID = ueID
                ueMeasResponse.granularityPeriod = ueMeas['granulPeriod']

                # fill meas data to UEID
                measData = e2sm_pb2.MeasData()
                for measName, measValue in ueMeas['measData'].items():
                    measData.measName = measName
                    # Check value type
                    if isinstance(measValue[0], int):
                        measData.valueInt = measValue[0]
                    elif isinstance(measValue[0], float):
                        measData.valueReal = measValue[0]
                    else:
                        measData.noValue = True
                    ueMeasResponse.measData.append(measData)

                response.ueMeasData.add().CopyFrom(ueMeasResponse)

            return response

        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
            return e2sm_pb2.EncActDefResponse()


class Server():
    def __init__(self):
        # E2SM packer
        self.e2sm_kpm = e2sm_kpm_packer()

        # Services
        self.eventTriggerSvc = EventTriggerService(self.e2sm_kpm)
        self.ranFuncDefSvc = RanFunctionService(self.e2sm_kpm)
        self.actDefinitionSvc = ActionDefinitionService(self.e2sm_kpm)
        self.indMessageSvc = IndicationMessage(self.e2sm_kpm)

        # Server
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

        # Add services to server
        e2sm_pb2_grpc.add_EventTriggerDefinitionServicer_to_server(
            self.eventTriggerSvc, self.server)
        e2sm_pb2_grpc.add_RanFunctionDefinitionServicer_to_server(
            self.ranFuncDefSvc, self.server
        )
        e2sm_pb2_grpc.add_ActionDefinitionServicer_to_server(
            self.actDefinitionSvc, self.server
        )
        e2sm_pb2_grpc.add_IndicationMessageServicer_to_server(
            self.indMessageSvc, self.server
        )
        # Enable reflection
        SERVICE_NAMES = (
            e2sm_pb2.DESCRIPTOR.services_by_name['EventTriggerDefinition'].full_name,
            e2sm_pb2.DESCRIPTOR.services_by_name['RanFunctionDefinition'].full_name,
            e2sm_pb2.DESCRIPTOR.services_by_name['ActionDefinition'].full_name,
            e2sm_pb2.DESCRIPTOR.services_by_name['IndicationMessage'].full_name,
            reflection.SERVICE_NAME,  # Reflection service itself
        )
        reflection.enable_server_reflection(SERVICE_NAMES, self.server)

    def Start(self):
        self.server.add_insecure_port("[::]:5051")
        logger.info("Server listening on *:5051")

        self.server.start()
        self.server.wait_for_termination()
