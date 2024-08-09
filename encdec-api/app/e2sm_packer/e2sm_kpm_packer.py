import os
import asn1tools


class e2sm_kpm_packer(object):
    def __init__(self) -> None:
        asn1_files = ["../../asn1/e2sm/e2sm-v5.00.asn",
                      "../../asn1/e2sm/e2sm-kpm-v4.00.asn"]
        self.asn1_compiler = asn1tools.compile_files(asn1_files, "per")

    def pack_event_trigger_def_fmt_1(self, reportingPeriod):
        e2sm_kpm_trigger_def = {
            'eventDefinition-formats': ('eventDefinition-Format1', {'reportingPeriod': reportingPeriod})}
        e2sm_kpm_trigger_def = self.asn1_compiler.encode(
            'E2SM-KPM-EventTriggerDefinition', e2sm_kpm_trigger_def)
        return e2sm_kpm_trigger_def


test = e2sm_kpm_packer()

event_trigger_def = test.pack_event_trigger_def_fmt_1(
    reportingPeriod=10000)
print(event_trigger_def)
print(f"Encoded {len(event_trigger_def)} bytes")
event_trigger_def = [event_trigger_def[i]
                     for i in range(0, len(event_trigger_def))]
print(event_trigger_def)
