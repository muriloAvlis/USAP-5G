import os
import asn1tools


class e2sm_kpm_packer(object):
    def __init__(self):
        self.my_dir = os.path.dirname(os.path.abspath(__file__))
        asn1_files = [self.my_dir + '/e2sm-v5.00.asn',
                      self.my_dir + '/e2sm-kpm-v4.00.asn']
        self.asn1_compiler = asn1tools.compile_files(asn1_files, 'per')

    # Just format 1 is available in E2SM-KPM V4.00
    def encode_event_trigger_def(self, reportingPeriod):
        e2sm_kpm_trigger_def = {
            'eventDefinition-formats': ('eventDefinition-Format1', {'reportingPeriod': reportingPeriod})}
        e2sm_kpm_trigger_def = self.asn1_compiler.encode(
            'E2SM-KPM-EventTriggerDefinition', e2sm_kpm_trigger_def)
        return e2sm_kpm_trigger_def

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
        return action_def

    def encode_action_def_format4(self, matchingUeConds: list, metric_names: list, granulPeriod: int = 1000):
        '''
        Used to carry measurement report for a group of UEs across a set of
        measurement types satisfying common subscribed conditions from a target
        E2 Node
        '''
        if not isinstance(metric_names, list):
            metric_names = [metric_names]

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

    def decode_ran_function_definition(self, ran_func_def_bytes: bytes):
        ran_func_def_decoded = self.asn1_compiler.decode(
            'E2SM-KPM-RANfunction-Description', ran_func_def_bytes
        )
        return ran_func_def_decoded
