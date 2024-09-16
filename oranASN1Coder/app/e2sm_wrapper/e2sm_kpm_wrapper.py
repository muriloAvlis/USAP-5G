import os
import asn1tools


class e2sm_kpm_wrapper(object):
    def __init__(self) -> None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        asn1_files = [os.path.join(base_dir, "../../asn1/e2sm/e2sm-v5.00.asn"),
                      os.path.join(base_dir, "../../asn1/e2sm/e2sm-kpm-v4.00.asn")]
        # asn1_files = [os.path.join(
        #     base_dir, "../../asn1/e2sm/oai-e2sm-kpm-v3.00.asn")]
        self.asn1_compiler = asn1tools.compile_files(asn1_files, "per")

    def __format_meas_info_list(self, metric_names):
        measInfoList = []
        # TODO: format also labels
        for metric_name in metric_names:
            metric_def = {'measType': ('measName', metric_name), 'labelInfoList': [
                {'measLabel': {'noLabel': 'true'}}]}
            measInfoList.append(metric_def)
        return measInfoList

    def __format_ueId_list(self, ue_ids):
        matchingUEidList = []
        for ue_id in ue_ids:
            matchingUEidList.append(
                {'ueID': ('gNB-DU-UEID', {'gNB-CU-UE-F1AP-ID': ue_id})})
        return matchingUEidList

    def encode_event_trigger_def_fmt_1(self, reportingPeriod) -> list:
        e2sm_kpm_trigger_def = {
            'eventDefinition-formats': ('eventDefinition-Format1', {'reportingPeriod': reportingPeriod})}
        e2sm_kpm_trigger_def = self.asn1_compiler.encode(
            'E2SM-KPM-EventTriggerDefinition', e2sm_kpm_trigger_def)
        return list(e2sm_kpm_trigger_def)

    def encode_action_definition_fmt_1(self, measNameList: list, granularityPeriod=1000) -> list:
        """E2SM-KPM Action Definition encoder on format 1

        Args:
            measNameList (list): meas name list
            granularityPeriod (int, optional): report granularity period. Defaults to 1000.

        Returns:
            list: encoded action definition
        """
        if not isinstance(measNameList, list):
            measNameList = [measNameList]

        measInfoList = self.__format_meas_info_list(measNameList)

        action_def = {'ric-Style-Type': 1,
                      'actionDefinition-formats': ('actionDefinition-Format1', {
                          'measInfoList': measInfoList,
                          'granulPeriod': granularityPeriod
                      })
                      }
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)
        return list(action_def)

    def encode_action_definition_fmt_2(self, ueId: str, measNameList: list, granularityPeriod=1000) -> list:
        """E2SM-KPM Action Definition encoder on format 2

        Args:
            ueId (str): The UE ID from which the metrics will be obtained
            measNameList (list): meas name list
            granularityPeriod (int, optional): report granularity period. Defaults to 1000.

        Returns:
            list: encoded action definition
        """
        if not isinstance(measNameList, list):
            measNameList = [measNameList]

        measInfoList = self.__format_meas_info_list(measNameList)

        ueId = self.__format_ueId_list([ueId])

        action_def = {'ric-Style-Type': 2,
                      'actionDefinition-formats': ('actionDefinition-Format2', {
                          'ueID': ueId,
                          'subscriptInfo': {
                              'measInfoList': measInfoList,
                              'granulPeriod': granularityPeriod}
                      })
                      }

        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)
        return list(action_def)

    def encode_action_definition_fmt_3(self, measName: str, granularityPeriod=1000) -> list:
        """E2SM-KPM Action Definition encoder on format 3

        Args:
            measName (str): meas name to get
            granularityPeriod (int, optional): report granularity period. Defaults to 1000.

        Returns:
            list: encoded action definition
        """
        # TODO: currently only dummy condition that is always satisfied, useful to get IDs of all connected UEs
        # example matching UE condition: ul-rSRP < 1000
        matchingConds = [{'matchingCondChoice': ('testCondInfo', {'testType': (
            'ul-rSRP', 'true'), 'testExpr': 'lessthan', 'testValue': ('valueInt', 1000)})}]

        action_def = {'ric-Style-Type': 3,
                      'actionDefinition-formats': ('actionDefinition-Format3', {
                          'measCondList': [
                              {'measType': (
                                  'measName', measName), 'matchingCond': matchingConds}
                          ],
                          'granulPeriod': granularityPeriod})
                      }

        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)
        return list(action_def)

    def encode_action_definition_fmt_4(self, measNameList: list, granularityPeriod: int = 1000) -> list:
        """E2SM-KPM Action Definition encoder on format 4

        Args:
            measNameList (list): meas name list
            granularityPeriod (int, optional): report granularity period. Defaults to 1000.

        Returns:
            list: encoded action definition
        """
        if not isinstance(measNameList, list):
            measNameList = [measNameList]

        measInfoList = self.__format_meas_info_list(measNameList)

        # TODO: currently only dummy condition that is always satisfied, useful to get IDs of all connected UEs
        # example matching UE condition: ul-rSRP < 1000
        matchingUeCondList = [{'testCondInfo': {'testType': (
            'ul-rSRP', 'true'), 'testExpr': 'lessthan', 'testValue': ('valueInt', 1000)}}]

        action_def = {'ric-Style-Type': 4,
                      'actionDefinition-formats': ('actionDefinition-Format4',
                                                   {'matchingUeCondList': matchingUeCondList,
                                                    'subscriptionInfo': {
                                                        'measInfoList': measInfoList,
                                                        'granulPeriod': granularityPeriod
                                                    }}
                                                   )}
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)
        return list(action_def)

    def encode_action_definition_fmt_5(self, ueIds: list, measNameList: list, granularityPeriod: int = 1000) -> list:
        """E2SM-KPM Action Definition encoder on format 5

        Args:
            ueIds (list): UEs ID list
            measNameList (list): meas name list
            granularityPeriod (int, optional): report granularity period. Defaults to 1000.

        Returns:
            list: encoded action definition
        """
        matchingUEidList = self.__format_ueId_list(ueIds)
        measInfoList = self.__format_meas_info_list(measNameList)

        action_def = {'ric-Style-Type': 5,
                      'actionDefinition-formats': ('actionDefinition-Format5',
                                                   {'matchingUEidList': matchingUEidList,
                                                    'subscriptionInfo': {
                                                        'measInfoList': measInfoList,
                                                        'granulPeriod': granularityPeriod}
                                                    })
                      }
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)
        return list(action_def)

    def decode_ran_function_description(self, hex_string):
        byte_string = list(bytes.fromhex(hex_string))
        ran_function_description = self.asn1_compiler.decode(
            'E2SM-KPM-RANfunction-Description', byte_string)
        return ran_function_description

    def decode_ric_ind_header_fmt_1(self, encoded_data):
        indication_hdr = self.asn1_compiler.decode(
            'E2SM-KPM-IndicationHeader-Format1', encoded_data
        )
        return indication_hdr

    def get_meas_name_list_by_ric_report_style(self, ran_function_description, reportStyleType) -> list:
        measNameList = []
        for reportStyle in ran_function_description['ric-ReportStyle-List']:
            if reportStyle['ric-ReportStyle-Type'] == reportStyleType:
                for meas in reportStyle['measInfo-Action-List']:
                    measNameList.append(meas['measName'])
                break
        return measNameList


# test = e2sm_kpm_wrapper()

# oai_metrics = ["DRB.PdcpSduVolumeDL", "DRB.PdcpSduVolumeUL", "DRB.RlcSduDelayDl",
#                "DRB.UEThpDl", "DRB.UEThpUl", "RRU.PrbTotDl", "RRU.PrbTotUl"]
# srs_metrics = ['CQI', 'DRB.AirIfDelayUl', 'DRB.PacketSuccessRateUlgNBUu', 'DRB.RlcDelayUl', 'DRB.RlcPacketDropRateDl', 'DRB.RlcSduDelayDl', 'DRB.RlcSduTransmittedVolumeDL',
#                'DRB.RlcSduTransmittedVolumeUL', 'DRB.UEThpDl', 'DRB.UEThpUl', 'RRU.PrbAvailDl', 'RRU.PrbAvailUl', 'RRU.PrbTotDl', 'RRU.PrbTotUl', 'RSRP', 'RSRQ']

# act_def = test.encode_action_definition_fmt_4(oai_metrics, 1000)

# event_trigger_def = test.encode_event_trigger_def_fmt_1(1000)
# print(f"Action Definition: \n {act_def}")

# print(f"Event Trigger Definition: \n {event_trigger_def}")
