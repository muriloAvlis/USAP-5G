import asn1tools
import os


class e2sm_kpm_packer(object):
    def __init__(self) -> None:
        asn1_files = ["./asn1/e2sm-v5.00.asn",
                      "./asn1/e2sm-kpm-v4.00.asn"]
        self.asn1_compiler = asn1tools.compile_files(asn1_files, "uper")

    def pack_event_trigger_def_fmt_1(self, reportingPeriod):
        e2sm_kpm_trigger_def = {
            'eventDefinition-formats': ('eventDefinition-Format1', {'reportingPeriod': reportingPeriod})}
        e2sm_kpm_trigger_def = self.asn1_compiler.encode(
            'E2SM-KPM-EventTriggerDefinition', e2sm_kpm_trigger_def)
        return e2sm_kpm_trigger_def

    def _pack_matching_ue_conds_list(self, matchingUeConds):
        matchingUeCondList = matchingUeConds
        return matchingUeCondList

    def _pack_meas_info_list(self, metric_names):
        measInfoList = []
        # TODO: pack also labels
        for metric_name in metric_names:
            metric_def = {'measType': ('measName', metric_name), 'labelInfoList': [
                {'measLabel': {'noLabel': 'true'}}]}
            measInfoList.append(metric_def)
        return measInfoList

    def pack_action_def_format4(self, matchingUeConds, metric_names, granulPeriod=100):
        if not isinstance(metric_names, list):
            metric_names = [metric_names]

        measInfoList = self._pack_meas_info_list(metric_names)
        matchingUeCondList = self._pack_matching_ue_conds_list(matchingUeConds)

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


test = e2sm_kpm_packer()

event_trigger_def = test.pack_action_def_format4(
    granulPeriod=1000,
    metric_names="CQI",
    matchingUeConds=[{'testCondInfo': {'testType': (
        'ul-rSRP', 'true'), 'testExpr': 'lessthan', 'testValue': ('valueInt', 1000)}}]
)

print(event_trigger_def)
print(f"Encoded {len(event_trigger_def)} bytes")
event_trigger_def = [event_trigger_def[i]
                     for i in range(0, len(event_trigger_def))]
print(event_trigger_def)
