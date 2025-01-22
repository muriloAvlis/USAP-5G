from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class StreamUeMetricsRequest(_message.Message):
    __slots__ = ("client_id",)
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    def __init__(self, client_id: _Optional[str] = ...) -> None: ...

class UeMeas(_message.Message):
    __slots__ = ("measName", "valueInt", "valueReal", "noValue")
    MEASNAME_FIELD_NUMBER: _ClassVar[int]
    VALUEINT_FIELD_NUMBER: _ClassVar[int]
    VALUEREAL_FIELD_NUMBER: _ClassVar[int]
    NOVALUE_FIELD_NUMBER: _ClassVar[int]
    measName: str
    valueInt: int
    valueReal: float
    noValue: bool
    def __init__(self, measName: _Optional[str] = ..., valueInt: _Optional[int] = ..., valueReal: _Optional[float] = ..., noValue: bool = ...) -> None: ...

class UeList(_message.Message):
    __slots__ = ("ueID", "imsi", "ueMeas", "granulPeriod")
    UEID_FIELD_NUMBER: _ClassVar[int]
    IMSI_FIELD_NUMBER: _ClassVar[int]
    UEMEAS_FIELD_NUMBER: _ClassVar[int]
    GRANULPERIOD_FIELD_NUMBER: _ClassVar[int]
    ueID: int
    imsi: str
    ueMeas: _containers.RepeatedCompositeFieldContainer[UeMeas]
    granulPeriod: int
    def __init__(self, ueID: _Optional[int] = ..., imsi: _Optional[str] = ..., ueMeas: _Optional[_Iterable[_Union[UeMeas, _Mapping]]] = ..., granulPeriod: _Optional[int] = ...) -> None: ...

class StreamUeMetricsResponse(_message.Message):
    __slots__ = ("latency_ms", "ueList")
    LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
    UELIST_FIELD_NUMBER: _ClassVar[int]
    latency_ms: float
    ueList: _containers.RepeatedCompositeFieldContainer[UeList]
    def __init__(self, latency_ms: _Optional[float] = ..., ueList: _Optional[_Iterable[_Union[UeList, _Mapping]]] = ...) -> None: ...
