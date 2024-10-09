from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class KPMIndicationRequest(_message.Message):
    __slots__ = ("svc_name",)
    SVC_NAME_FIELD_NUMBER: _ClassVar[int]
    svc_name: str
    def __init__(self, svc_name: _Optional[str] = ...) -> None: ...

class KPMIndicationResponse(_message.Message):
    __slots__ = ("latency", "node", "ue")
    LATENCY_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    UE_FIELD_NUMBER: _ClassVar[int]
    latency: int
    node: E2NodeInfos
    ue: UEInfos
    def __init__(self, latency: _Optional[int] = ..., node: _Optional[_Union[E2NodeInfos, _Mapping]] = ..., ue: _Optional[_Union[UEInfos, _Mapping]] = ...) -> None: ...

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
    __slots__ = ("ue_id",)
    UE_ID_FIELD_NUMBER: _ClassVar[int]
    ue_id: UEIDs
    def __init__(self, ue_id: _Optional[_Union[UEIDs, _Mapping]] = ...) -> None: ...

class UEIDs(_message.Message):
    __slots__ = ("GnbCuUeF1ApId", "AmfUeNgApId", "Guami", "GnbCuCpUeE1ApId", "RanUeId")
    GNBCUUEF1APID_FIELD_NUMBER: _ClassVar[int]
    AMFUENGAPID_FIELD_NUMBER: _ClassVar[int]
    GUAMI_FIELD_NUMBER: _ClassVar[int]
    GNBCUCPUEE1APID_FIELD_NUMBER: _ClassVar[int]
    RANUEID_FIELD_NUMBER: _ClassVar[int]
    GnbCuUeF1ApId: int
    AmfUeNgApId: int
    Guami: Guami_t
    GnbCuCpUeE1ApId: int
    RanUeId: int
    def __init__(self, GnbCuUeF1ApId: _Optional[int] = ..., AmfUeNgApId: _Optional[int] = ..., Guami: _Optional[_Union[Guami_t, _Mapping]] = ..., GnbCuCpUeE1ApId: _Optional[int] = ..., RanUeId: _Optional[int] = ...) -> None: ...

class Guami_t(_message.Message):
    __slots__ = ("Plmn", "AmfRegionId", "AmfSetId")
    PLMN_FIELD_NUMBER: _ClassVar[int]
    AMFREGIONID_FIELD_NUMBER: _ClassVar[int]
    AMFSETID_FIELD_NUMBER: _ClassVar[int]
    Plmn: PlmnId
    AmfRegionId: int
    AmfSetId: int
    def __init__(self, Plmn: _Optional[_Union[PlmnId, _Mapping]] = ..., AmfRegionId: _Optional[int] = ..., AmfSetId: _Optional[int] = ...) -> None: ...

class PlmnId(_message.Message):
    __slots__ = ("Mcc", "Mnc", "MncDigitLen")
    MCC_FIELD_NUMBER: _ClassVar[int]
    MNC_FIELD_NUMBER: _ClassVar[int]
    MNCDIGITLEN_FIELD_NUMBER: _ClassVar[int]
    Mcc: int
    Mnc: int
    MncDigitLen: int
    def __init__(self, Mcc: _Optional[int] = ..., Mnc: _Optional[int] = ..., MncDigitLen: _Optional[int] = ...) -> None: ...
