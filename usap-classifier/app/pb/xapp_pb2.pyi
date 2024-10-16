from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KPMIndicationRequest(_message.Message):
    __slots__ = ("svc_name",)
    SVC_NAME_FIELD_NUMBER: _ClassVar[int]
    svc_name: str
    def __init__(self, svc_name: _Optional[str] = ...) -> None: ...

class KPMIndicationResponse(_message.Message):
    __slots__ = ("latency", "ue")
    LATENCY_FIELD_NUMBER: _ClassVar[int]
    UE_FIELD_NUMBER: _ClassVar[int]
    latency: float
    ue: UEInfos
    def __init__(self, latency: _Optional[float] = ..., ue: _Optional[_Union[UEInfos, _Mapping]] = ...) -> None: ...

class E2NodeInfos(_message.Message):
    __slots__ = ("nodeb_id", "node_type_name", "mcc", "mnc", "mnc_digit_len", "cu_du_id")
    NODEB_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_NAME_FIELD_NUMBER: _ClassVar[int]
    MCC_FIELD_NUMBER: _ClassVar[int]
    MNC_FIELD_NUMBER: _ClassVar[int]
    MNC_DIGIT_LEN_FIELD_NUMBER: _ClassVar[int]
    CU_DU_ID_FIELD_NUMBER: _ClassVar[int]
    nodeb_id: int
    node_type_name: str
    mcc: int
    mnc: int
    mnc_digit_len: int
    cu_du_id: int
    def __init__(self, nodeb_id: _Optional[int] = ..., node_type_name: _Optional[str] = ..., mcc: _Optional[int] = ..., mnc: _Optional[int] = ..., mnc_digit_len: _Optional[int] = ..., cu_du_id: _Optional[int] = ...) -> None: ...

class UEInfos(_message.Message):
    __slots__ = ("ue_id", "ue_meas_info")
    UE_ID_FIELD_NUMBER: _ClassVar[int]
    UE_MEAS_INFO_FIELD_NUMBER: _ClassVar[int]
    ue_id: UEIDs
    ue_meas_info: _containers.RepeatedCompositeFieldContainer[MeasInfo]
    def __init__(self, ue_id: _Optional[_Union[UEIDs, _Mapping]] = ..., ue_meas_info: _Optional[_Iterable[_Union[MeasInfo, _Mapping]]] = ...) -> None: ...

class UEIDs(_message.Message):
    __slots__ = ("gnb_cu_ue_f1ap_id", "amf_ue_ngap_id", "gnb_cu_cp_ue_e1ap_id", "ran_ue_id")
    GNB_CU_UE_F1AP_ID_FIELD_NUMBER: _ClassVar[int]
    AMF_UE_NGAP_ID_FIELD_NUMBER: _ClassVar[int]
    GNB_CU_CP_UE_E1AP_ID_FIELD_NUMBER: _ClassVar[int]
    RAN_UE_ID_FIELD_NUMBER: _ClassVar[int]
    gnb_cu_ue_f1ap_id: int
    amf_ue_ngap_id: int
    gnb_cu_cp_ue_e1ap_id: int
    ran_ue_id: int
    def __init__(self, gnb_cu_ue_f1ap_id: _Optional[int] = ..., amf_ue_ngap_id: _Optional[int] = ..., gnb_cu_cp_ue_e1ap_id: _Optional[int] = ..., ran_ue_id: _Optional[int] = ...) -> None: ...

class Guami_t(_message.Message):
    __slots__ = ("plmn", "amf_region_id", "amf_set_id")
    PLMN_FIELD_NUMBER: _ClassVar[int]
    AMF_REGION_ID_FIELD_NUMBER: _ClassVar[int]
    AMF_SET_ID_FIELD_NUMBER: _ClassVar[int]
    plmn: PlmnId
    amf_region_id: int
    amf_set_id: int
    def __init__(self, plmn: _Optional[_Union[PlmnId, _Mapping]] = ..., amf_region_id: _Optional[int] = ..., amf_set_id: _Optional[int] = ...) -> None: ...

class PlmnId(_message.Message):
    __slots__ = ("mcc", "mnc", "mnc_digit_len")
    MCC_FIELD_NUMBER: _ClassVar[int]
    MNC_FIELD_NUMBER: _ClassVar[int]
    MNC_DIGIT_LEN_FIELD_NUMBER: _ClassVar[int]
    mcc: int
    mnc: int
    mnc_digit_len: int
    def __init__(self, mcc: _Optional[int] = ..., mnc: _Optional[int] = ..., mnc_digit_len: _Optional[int] = ...) -> None: ...

class MeasInfo(_message.Message):
    __slots__ = ("meas_name", "int_value", "real_value")
    MEAS_NAME_FIELD_NUMBER: _ClassVar[int]
    INT_VALUE_FIELD_NUMBER: _ClassVar[int]
    REAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    meas_name: str
    int_value: int
    real_value: float
    def __init__(self, meas_name: _Optional[str] = ..., int_value: _Optional[int] = ..., real_value: _Optional[float] = ...) -> None: ...
