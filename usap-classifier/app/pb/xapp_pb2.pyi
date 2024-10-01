from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EmptyRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class IndStyle4Response(_message.Message):
    __slots__ = ("collectTime", "messageCounter", "ueIds", "reported_meas")
    COLLECTTIME_FIELD_NUMBER: _ClassVar[int]
    MESSAGECOUNTER_FIELD_NUMBER: _ClassVar[int]
    UEIDS_FIELD_NUMBER: _ClassVar[int]
    REPORTED_MEAS_FIELD_NUMBER: _ClassVar[int]
    collectTime: int
    messageCounter: int
    ueIds: ueIds_t
    reported_meas: kpm_reported_meas_t
    def __init__(self, collectTime: _Optional[int] = ..., messageCounter: _Optional[int] = ..., ueIds: _Optional[_Union[ueIds_t, _Mapping]] = ..., reported_meas: _Optional[_Union[kpm_reported_meas_t, _Mapping]] = ...) -> None: ...

class kpm_reported_meas_t(_message.Message):
    __slots__ = ("int_metrics", "real_metrics")
    INT_METRICS_FIELD_NUMBER: _ClassVar[int]
    REAL_METRICS_FIELD_NUMBER: _ClassVar[int]
    int_metrics: _containers.RepeatedCompositeFieldContainer[kpm_int_metric_t]
    real_metrics: _containers.RepeatedCompositeFieldContainer[kpm_real_metric_t]
    def __init__(self, int_metrics: _Optional[_Iterable[_Union[kpm_int_metric_t, _Mapping]]] = ..., real_metrics: _Optional[_Iterable[_Union[kpm_real_metric_t, _Mapping]]] = ...) -> None: ...

class kpm_int_metric_t(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: int
    def __init__(self, name: _Optional[str] = ..., value: _Optional[int] = ...) -> None: ...

class kpm_real_metric_t(_message.Message):
    __slots__ = ("name", "value")
    NAME_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    name: str
    value: float
    def __init__(self, name: _Optional[str] = ..., value: _Optional[float] = ...) -> None: ...

class ueIds_t(_message.Message):
    __slots__ = ("amfUeNgapId", "ranUeId", "gnbCuCpUeE1apId", "gnbCuUeF1apId")
    AMFUENGAPID_FIELD_NUMBER: _ClassVar[int]
    RANUEID_FIELD_NUMBER: _ClassVar[int]
    GNBCUCPUEE1APID_FIELD_NUMBER: _ClassVar[int]
    GNBCUUEF1APID_FIELD_NUMBER: _ClassVar[int]
    amfUeNgapId: str
    ranUeId: str
    gnbCuCpUeE1apId: str
    gnbCuUeF1apId: str
    def __init__(self, amfUeNgapId: _Optional[str] = ..., ranUeId: _Optional[str] = ..., gnbCuCpUeE1apId: _Optional[str] = ..., gnbCuUeF1apId: _Optional[str] = ...) -> None: ...

class e2ap_plmn_t(_message.Message):
    __slots__ = ("mcc", "mnc", "mnc_digit_len")
    MCC_FIELD_NUMBER: _ClassVar[int]
    MNC_FIELD_NUMBER: _ClassVar[int]
    MNC_DIGIT_LEN_FIELD_NUMBER: _ClassVar[int]
    mcc: int
    mnc: int
    mnc_digit_len: int
    def __init__(self, mcc: _Optional[int] = ..., mnc: _Optional[int] = ..., mnc_digit_len: _Optional[int] = ...) -> None: ...

class e2ap_gnb_id_t(_message.Message):
    __slots__ = ("nb_id",)
    NB_ID_FIELD_NUMBER: _ClassVar[int]
    nb_id: int
    def __init__(self, nb_id: _Optional[int] = ...) -> None: ...

class global_e2_node_id_t(_message.Message):
    __slots__ = ("type", "plmn", "nb_id", "cu_du_id")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PLMN_FIELD_NUMBER: _ClassVar[int]
    NB_ID_FIELD_NUMBER: _ClassVar[int]
    CU_DU_ID_FIELD_NUMBER: _ClassVar[int]
    type: str
    plmn: e2ap_plmn_t
    nb_id: e2ap_gnb_id_t
    cu_du_id: int
    def __init__(self, type: _Optional[str] = ..., plmn: _Optional[_Union[e2ap_plmn_t, _Mapping]] = ..., nb_id: _Optional[_Union[e2ap_gnb_id_t, _Mapping]] = ..., cu_du_id: _Optional[int] = ...) -> None: ...

class e2_node_connected_xapp_t(_message.Message):
    __slots__ = ("id", "len_cca")
    ID_FIELD_NUMBER: _ClassVar[int]
    LEN_CCA_FIELD_NUMBER: _ClassVar[int]
    id: global_e2_node_id_t
    len_cca: int
    def __init__(self, id: _Optional[_Union[global_e2_node_id_t, _Mapping]] = ..., len_cca: _Optional[int] = ...) -> None: ...

class E2NodesResponse(_message.Message):
    __slots__ = ("len", "e2Node")
    LEN_FIELD_NUMBER: _ClassVar[int]
    E2NODE_FIELD_NUMBER: _ClassVar[int]
    len: int
    e2Node: _containers.RepeatedCompositeFieldContainer[e2_node_connected_xapp_t]
    def __init__(self, len: _Optional[int] = ..., e2Node: _Optional[_Iterable[_Union[e2_node_connected_xapp_t, _Mapping]]] = ...) -> None: ...
