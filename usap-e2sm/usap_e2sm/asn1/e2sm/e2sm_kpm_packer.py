import os
import asn1tools
from usap_e2sm.asn1.e2sm.utils import ntp_ts_to_ms


class e2sm_kpm_packer(object):
    def __init__(self):
        self.my_dir = os.path.dirname(os.path.abspath(__file__))
        asn1_files = [self.my_dir + '/e2sm-v5.00.asn',
                      self.my_dir + '/e2sm-kpm-v4.00.asn']
        self.asn1_compiler = asn1tools.compile_files(asn1_files, 'per')

    def _pack_meas_info_list(self, metric_names: list, measurement_label: dict = {'noLabel': 'true'}):
        measInfoList = []
        for metric_name in metric_names:
            metric_def = {'measType': ('measName', metric_name), 'labelInfoList': [
                {'measLabel': measurement_label}]}
            measInfoList.append(metric_def)
        return measInfoList

    def _pack_ue_id_list(self, ue_ids):
        # TODO: filter by others UE IDs
        matchingUEidList = []
        for ue_id in ue_ids:
            matchingUEidList.append(
                {'ueID': ('gNB-DU-UEID', {'gNB-CU-UE-F1AP-ID': ue_id})})
        return matchingUEidList

    # Just format 1 is available in E2SM-KPM V4.00
    def encode_event_trigger_def(self, reportingPeriod: int) -> list:
        e2sm_kpm_trigger_def = {
            'eventDefinition-formats': ('eventDefinition-Format1', {'reportingPeriod': reportingPeriod})}
        e2sm_kpm_trigger_def = self.asn1_compiler.encode(
            'E2SM-KPM-EventTriggerDefinition', e2sm_kpm_trigger_def)

        # Convert byte to []int64 data
        e2sm_kpm_trigger_def = [e2sm_kpm_trigger_def[i]
                                for i in range(0, len(e2sm_kpm_trigger_def))]

        return e2sm_kpm_trigger_def

    def encode_action_def_format1(self, metric_names: list, granulPeriod: int = 1000):
        '''
        Used to carry measurement report from a target E2 Node
        '''
        if not isinstance(metric_names, list):
            metric_names = [metric_names]

        # TODO: test SST label filter
        measInfoList = self._pack_meas_info_list(metric_names)

        action_def = {'ric-Style-Type': 1,
                      'actionDefinition-formats': ('actionDefinition-Format1', {
                          'measInfoList': measInfoList,
                          'granulPeriod': granulPeriod
                      })
                      }
        
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)

        # Convert byte to []int64 data
        action_def = [action_def[i]
                      for i in range(0, len(action_def))]

        return action_def

    def encode_action_def_format2(self, ue_id, metric_names: list, granulPeriod=1000):
        '''
        Used to carry measurement report for a single UE of interest from a target E2 Node
        '''
        if not isinstance(metric_names, list):
            metric_names = [metric_names]

        ue_id = self._pack_ue_id_list([ue_id])
        ue_id = tuple(ue_id[0]['ueID'])  # extract as there is only 1 UE

        measInfoList = self._pack_meas_info_list(metric_names)
        action_def = {'ric-Style-Type': 2,
                      'actionDefinition-formats': ('actionDefinition-Format2', {
                          'ueID': ue_id,
                          'subscriptInfo': {
                              'measInfoList': measInfoList,
                              'granulPeriod': granulPeriod}
                      })
                      }
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)

        # Convert byte to []int64 data
        action_def = [action_def[i]
                      for i in range(0, len(action_def))]

        return action_def

    def encode_action_def_format3(self, matchingConds: list, metric_names: list, granulPeriod: int = 1000):
        '''
        Used to carry UE-level measurement report for a group of UEs per
        measurement type matching subscribed conditions from a target E2 Node
        '''
        if not isinstance(metric_names, list):
            metric_names = [metric_names]

        if (len(metric_names) > 1):
            print("Currently only 1 metric can be requested in E2SM-KPM Report Style 3")
            exit(1)

        matchingCondList = matchingConds

        action_def = {'ric-Style-Type': 3,
                      'actionDefinition-formats': ('actionDefinition-Format3', {
                          'measCondList': [
                              {
                                  'measType': ('measName', metric_names[0]),
                                  'matchingCond': matchingCondList
                              }
                          ],
                          'granulPeriod': granulPeriod})
                      }
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)

        # Convert byte to []int64 data
        action_def = [action_def[i]
                      for i in range(0, len(action_def))]

        return action_def

    def encode_action_def_format4(self, matchingUeConds: list, metric_names: list, granulPeriod: int = 1000) -> list:
        '''
        Used to carry measurement report for a group of UEs across a set of
        measurement types satisfying common subscribed conditions from a target
        E2 Node
        '''
        # if not isinstance(metric_names, list):
        #     metric_names = [metric_names]

        measInfoList = self._pack_meas_info_list(metric_names)

        matchingUeCondList = matchingUeConds

        action_def = {'ric-Style-Type': 4,
                      'actionDefinition-formats': ('actionDefinition-Format4',
                                                   {'matchingUeCondList': matchingUeCondList,
                                                    'subscriptionInfo': {
                                                        'measInfoList': measInfoList,
                                                        'granulPeriod': granulPeriod
                                                    }}
                                                   )}
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)

        # Convert byte to []int64 data
        action_def = [action_def[i]
                      for i in range(0, len(action_def))]

        return action_def

    def encode_action_def_format5(self, ue_ids: list, metric_names: list, granulPeriod=1000):
        '''
        Used to carry measurement report for multiple UE of interest from a target E2 Node
        '''
        if not isinstance(metric_names, list):
            metric_names = [metric_names]

        matchingUEidList = self._pack_ue_id_list(ue_ids)
        measInfoList = self._pack_meas_info_list(metric_names)

        action_def = {'ric-Style-Type': 5,
                      'actionDefinition-formats': ('actionDefinition-Format5',
                                                   {'matchingUEidList': matchingUEidList,
                                                    'subscriptionInfo': {
                                                        'measInfoList': measInfoList,
                                                        'granulPeriod': granulPeriod}
                                                    })
                      }
        action_def = self.asn1_compiler.encode(
            'E2SM-KPM-ActionDefinition', action_def)

        # Convert byte to []int64 data
        action_def = [action_def[i]
                      for i in range(0, len(action_def))]

        return action_def

    def decode_indication_header_format1(self, msg_bytes):
        indication_hdr = self.asn1_compiler.decode(
            'E2SM-KPM-IndicationHeader-Format1', msg_bytes)
        return indication_hdr

    def decode_indication_header(self, msg_bytes):
        return self.decode_indication_header_format1(msg_bytes)

    def decode_indication_message(self, msg_bytes):
        indication_msg = self.asn1_compiler.decode(
            'E2SM-KPM-IndicationMessage', msg_bytes)
        return indication_msg

    def decode_ran_function_definition(self, ran_func_def: str) -> dict:
        ran_func_def = bytes.fromhex(ran_func_def)

        ran_func_def_decoded = self.asn1_compiler.decode(
            'E2SM-KPM-RANfunction-Description', ran_func_def
        )
        return ran_func_def_decoded

    def get_metric_names_by_report_style(self, ran_func_def: dict, report_style_type: int):
        return [
            metric['measName']
            for report_style in ran_func_def.get('ric-ReportStyle-List', [])
            if report_style.get('ric-ReportStyle-Type') == report_style_type
            for metric in report_style.get('measInfo-Action-List', [])
        ]

    def extract_hdr_info(self, indication_hdr):
        timestamp = int.from_bytes(indication_hdr['colletStartTime'], "big")
        dt_object = ntp_ts_to_ms(timestamp)
        indication_hdr['colletStartTime'] = dt_object
        return indication_hdr

    def _extract_meas_data_ind_msg_f1(self, indication_msg_content):
        indication_dict = {}
        metric_names = []
        meas_data_dict = {}
        measData = indication_msg_content["measData"]
        measInfoList = indication_msg_content["measInfoList"]
        granulPeriod = indication_msg_content.get("granulPeriod", None)

        # extract metric names
        # TODO: extract metric labels as well
        for measInfoItem in measInfoList:
            metric_name = measInfoItem["measType"][1]
            metric_names.append(metric_name)
            meas_data_dict[metric_name] = []

        # extract measurements data
        # map measData to metrics
        for measDataItem in measData:
            measRecord = measDataItem['measRecord']
            idx = 0
            for measRecordItem in measRecord:
                valueType = measRecordItem[0]
                value = measRecordItem[1]
                metric_name = metric_names[idx]
                meas_data_dict[metric_name].append(value)
                idx += 1

        indication_dict["measData"] = meas_data_dict
        # add granulPeriod to dict
        if (granulPeriod is not None):
            indication_dict['granulPeriod'] = granulPeriod

        return indication_dict

    def _extract_content_ind_msg_f1(self, indication_msg):
        '''
        # example content
        {'indicationMessage-formats': ('indicationMessage-Format1', {
            'measData': [{'measRecord': [('integer', 8), ('integer', 8)]}],
            'measInfoList': [{'measType': ('measName', 'DRB.UEThpDl'), 'labelInfoList': [{'measLabel': {'noLabel': 'true'}}]},
                             {'measType': ('measName', 'DRB.UEThpUl'), 'labelInfoList': [{'measLabel': {'noLabel': 'true'}}]}],
            'granulPeriod': 1000})}
        '''
        meas_data_dict = self._extract_meas_data_ind_msg_f1(
            indication_msg["indicationMessage-formats"][1])
        return meas_data_dict

    def _extract_content_ind_msg_f2(self, indication_msg):
        '''
        # example content
        {'indicationMessage-formats': ('indicationMessage-Format2',
            {
            'measData': [{'measRecord': [('integer', 0)]}],
            'measCondUEidList': [{
                                'measType': ('measName', 'DRB.UEThpDl'),
                                'matchingCond': [{'matchingCondChoice': ('testCondInfo', {'testType': ('ul-rSRP', 'true'), 'testExpr': 'lessthan', 'testValue': ('valueInt', 1000)})}],
                                'matchingUEidList': [{'ueID': ('gNB-DU-UEID', {'gNB-CU-UE-F1AP-ID': 0})}]}],
            'granulPeriod': 1000
            }
        )}
        '''
        indication_dict = {}
        metric_names = []
        ue_ids = []
        meas_data_dict = {}
        indication_msg_content = indication_msg["indicationMessage-formats"][1]
        measData = indication_msg_content["measData"]
        measCondUEidList = indication_msg_content["measCondUEidList"]
        granulPeriod = indication_msg_content.get("granulPeriod", None)

        # extract metric names
        # Note: currently only 1 metric in indication msg format 2 is supported
        for measInfoItem in measCondUEidList:
            metric_name = measInfoItem["measType"][1]
            # copy of the matchingCond from Subscription Request
            matchingCond = measInfoItem["matchingCond"]
            # list of UEs that satisfy the matchingCond
            matchingUEidList = measInfoItem.get("matchingUEidList", None)
            matchingUEidPerGP = measInfoItem.get("matchingUEidPerGP", None)
            metric_names.append(metric_name)

        if matchingUEidList is None:
            return meas_data_dict

        for matchingUE in matchingUEidList:
            ueID = list(matchingUE["ueID"][1].values())[0]
            ue_ids.append(ueID)
            meas_data_dict[ueID] = {"measData": {}}
            # for each UE create an entry for each metric_name
            for metric_name in metric_names:
                meas_data_dict[ueID]["measData"] = {metric_name: []}

        # map measData to UE and Metric name
        for measDataItem in measData:
            measRecord = measDataItem['measRecord']
            idx = 0
            for measRecordItem in measRecord:
                ueID = ue_ids[idx]
                # currently only 1 metric supported in format 2
                metric_name = metric_names[0]
                valueType = measRecordItem[0]
                value = measRecordItem[1]
                meas_data_dict[ueID]["measData"][metric_name].append(value)
                idx += 1

        indication_dict["ueMeasData"] = meas_data_dict
        indication_dict["matchingCond"] = matchingCond
        # add granulPeriod to dict
        if (granulPeriod is not None):
            indication_dict['granulPeriod'] = granulPeriod

        return indication_dict

    def _extract_content_ind_msg_f3(self, indication_msg):
        '''
        # example content
        {'indicationMessage-formats': ('indicationMessage-Format3', {
            'ueMeasReportList': [{
                   'ueID': ('gNB-DU-UEID', {'gNB-CU-UE-F1AP-ID': 0}),
                   'measReport': {
                                'measData': [{'measRecord': [('integer', 0), ('integer', 0)]}],
                                'measInfoList': [{'measType': ('measName', 'DRB.UEThpDl'), 'labelInfoList': [{'measLabel': {'noLabel': 'true'}}]},
                                                 {'measType': ('measName', 'DRB.UEThpUl'), 'labelInfoList': [{'measLabel': {'noLabel': 'true'}}]}],
                                'granulPeriod': 1000
                   }}]
            })
        }
        '''
        indication_dict = {}
        meas_data_dict = {}
        ueMeasReportList = indication_msg["indicationMessage-formats"][1]["ueMeasReportList"]
        for ueMeasReport in ueMeasReportList:
            ueID = list(ueMeasReport["ueID"][1].values())[0]
            measReport = ueMeasReport['measReport']
            meas_data_dict[ueID] = self._extract_meas_data_ind_msg_f1(
                measReport)

        indication_dict["ueMeasData"] = meas_data_dict
        return indication_dict

    def extract_meas_data(self, indication_msg):
        meas_data = {}
        indication_msg_format = indication_msg["indicationMessage-formats"][0]
        if indication_msg_format == "indicationMessage-Format1":
            meas_data = self._extract_content_ind_msg_f1(indication_msg)
        elif indication_msg_format == "indicationMessage-Format2":
            meas_data = self._extract_content_ind_msg_f2(indication_msg)
        elif indication_msg_format == "indicationMessage-Format3":
            meas_data = self._extract_content_ind_msg_f3(indication_msg)
        return meas_data


# test = e2sm_kpm_packer()
# result = test.decode_indication_header(
#     bytes([0, 235, 49, 149, 178, 138, 108, 96, 100]))
# result2 = test.decode_indication_message(bytes([64, 0, 129, 130, 0, 0, 0, 8, 0, 0, 96, 0, 0, 0, 15, 64, 0, 64, 0, 64, 0, 0, 0, 32, 0, 32, 0, 0, 106, 0, 106, 0, 0, 0, 0, 0, 0, 0, 0, 0, 14, 0, 240, 68, 82, 66, 46, 65, 105, 114, 73, 102, 68, 101, 108, 97, 121, 85, 108, 1, 32, 0, 0, 1, 176, 68, 82, 66, 46, 80, 97, 99, 107, 101, 116, 83, 117, 99, 99, 101, 115, 115, 82, 97, 116, 101, 85, 108, 103, 78, 66, 85, 117, 1, 32, 0, 0, 0, 208, 68, 82, 66, 46, 82, 108, 99, 68, 101, 108, 97, 121, 85, 108, 1, 32, 0, 0, 1, 96, 68, 82, 66, 46, 82, 108, 99, 80, 97, 99, 107, 101, 116, 68, 114, 111, 112, 82, 97, 116, 101, 68, 108, 1, 32, 0, 0, 1, 0, 68, 82, 66, 46, 82, 108, 99, 83, 100, 117, 68, 101, 108, 97, 121, 68, 108, 1, 32, 0, 0, 1, 192, 68, 82, 66, 46, 82, 108, 99, 83, 100, 117, 84, 114, 97, 110, 115, 109, 105, 116, 116, 101, 100, 86, 111, 108, 117, 109, 101, 68, 76, 1, 32, 0, 0, 1, 192, 68, 82, 66, 46, 82, 108, 99, 83, 100, 117, 84, 114, 97, 110, 115, 109, 105, 116, 116, 101, 100, 86, 111, 108, 117, 109, 101, 85, 76, 1, 32, 0, 0, 0, 160, 68, 82, 66, 46, 85, 69, 84, 104, 112, 68, 108, 1, 32, 0, 0, 0, 160, 68, 82, 66, 46, 85, 69, 84, 104, 112, 85, 108, 1, 32, 0, 0, 0, 208, 82, 82, 85, 46, 80, 114, 98, 65, 118, 97, 105, 108, 68, 108, 1, 32, 0, 0, 0, 208, 82, 82, 85, 46, 80, 114, 98, 65, 118, 97, 105, 108, 85, 108, 1, 32, 0, 0, 0, 176, 82, 82, 85, 46, 80, 114, 98, 84, 111, 116, 68, 108, 1, 32, 0, 0, 0, 176, 82, 82, 85, 46, 80, 114, 98, 84, 111, 116, 85, 108, 1, 32, 0, 0, 0, 192, 82, 82, 85, 46, 80, 114, 98, 85, 115, 101, 100, 68, 108, 1, 32, 0, 0, 0, 192, 82, 82, 85, 46, 80, 114, 98, 85, 115, 101, 100, 85, 108, 1, 32, 0, 0, 64, 3, 231]
#                                                ))

# print(test.encode_event_trigger_def(4294967295))

# print(test.encode_action_def_format1(['DRB.UEThpDl'], 4294967295))


# print(result)
# timestamp = int.from_bytes(result['colletStartTime'], "big")
# print(timestamp)
# result2 = test.extract_meas_data(result2)
# print(test.extract_hdr_info(result)['colletStartTime'])
# print(type(test.extract_hdr_info(result)['colletStartTime']))

# print(result2['ueMeasData'])

# for ueID, ueMeas in result2['ueMeasData'].items():
#     print(ueID)
#     print(ueMeas['granulPeriod'])
#     for measName, measValue in ueMeas['measData'].items():
#         print(measName)
#         # Check value type
#         if isinstance(measValue[0], int):
#             print(measValue[0])
#         elif isinstance(measValue[0], float):
#             print(measValue[0])
#         else:
#             continue
