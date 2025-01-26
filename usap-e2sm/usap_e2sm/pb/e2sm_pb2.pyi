from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EncodeEventTriggerRequest(_message.Message):
    __slots__ = ("reportingPeriod",)
    REPORTINGPERIOD_FIELD_NUMBER: _ClassVar[int]
    reportingPeriod: int
    def __init__(self, reportingPeriod: _Optional[int] = ...) -> None: ...

class EncodeEventTriggerResponse(_message.Message):
    __slots__ = ("eventTriggerDef",)
    EVENTTRIGGERDEF_FIELD_NUMBER: _ClassVar[int]
    eventTriggerDef: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, eventTriggerDef: _Optional[_Iterable[int]] = ...) -> None: ...

class DecodeRanFunctionRequest(_message.Message):
    __slots__ = ("ranFuncDefinition",)
    RANFUNCDEFINITION_FIELD_NUMBER: _ClassVar[int]
    ranFuncDefinition: str
    def __init__(self, ranFuncDefinition: _Optional[str] = ...) -> None: ...

class DecodeRanFunctionResponse(_message.Message):
    __slots__ = ("decodedRanFuncDef",)
    DECODEDRANFUNCDEF_FIELD_NUMBER: _ClassVar[int]
    decodedRanFuncDef: str
    def __init__(self, decodedRanFuncDef: _Optional[str] = ...) -> None: ...

class TestCondValue(_message.Message):
    __slots__ = ("valueInt", "valueEnum", "valueBool", "valueBitS", "valueOctS", "valuePrtS", "valueReal")
    VALUEINT_FIELD_NUMBER: _ClassVar[int]
    VALUEENUM_FIELD_NUMBER: _ClassVar[int]
    VALUEBOOL_FIELD_NUMBER: _ClassVar[int]
    VALUEBITS_FIELD_NUMBER: _ClassVar[int]
    VALUEOCTS_FIELD_NUMBER: _ClassVar[int]
    VALUEPRTS_FIELD_NUMBER: _ClassVar[int]
    VALUEREAL_FIELD_NUMBER: _ClassVar[int]
    valueInt: int
    valueEnum: int
    valueBool: bool
    valueBitS: bytes
    valueOctS: bytes
    valuePrtS: str
    valueReal: float
    def __init__(self, valueInt: _Optional[int] = ..., valueEnum: _Optional[int] = ..., valueBool: bool = ..., valueBitS: _Optional[bytes] = ..., valueOctS: _Optional[bytes] = ..., valuePrtS: _Optional[str] = ..., valueReal: _Optional[float] = ...) -> None: ...

class TestCondInfo(_message.Message):
    __slots__ = ("testType", "testExpr", "testCondValue")
    TESTTYPE_FIELD_NUMBER: _ClassVar[int]
    TESTEXPR_FIELD_NUMBER: _ClassVar[int]
    TESTCONDVALUE_FIELD_NUMBER: _ClassVar[int]
    testType: str
    testExpr: str
    testCondValue: TestCondValue
    def __init__(self, testType: _Optional[str] = ..., testExpr: _Optional[str] = ..., testCondValue: _Optional[_Union[TestCondValue, _Mapping]] = ...) -> None: ...

class MatchingUEConds(_message.Message):
    __slots__ = ("testCondInfo",)
    TESTCONDINFO_FIELD_NUMBER: _ClassVar[int]
    testCondInfo: TestCondInfo
    def __init__(self, testCondInfo: _Optional[_Union[TestCondInfo, _Mapping]] = ...) -> None: ...

class EncodeActDefFormat4Request(_message.Message):
    __slots__ = ("matchingUEConds", "measNameList", "granularityPeriod")
    MATCHINGUECONDS_FIELD_NUMBER: _ClassVar[int]
    MEASNAMELIST_FIELD_NUMBER: _ClassVar[int]
    GRANULARITYPERIOD_FIELD_NUMBER: _ClassVar[int]
    matchingUEConds: MatchingUEConds
    measNameList: _containers.RepeatedScalarFieldContainer[str]
    granularityPeriod: int
    def __init__(self, matchingUEConds: _Optional[_Union[MatchingUEConds, _Mapping]] = ..., measNameList: _Optional[_Iterable[str]] = ..., granularityPeriod: _Optional[int] = ...) -> None: ...

class EncActDefResponse(_message.Message):
    __slots__ = ("actionDefinitionEnc",)
    ACTIONDEFINITIONENC_FIELD_NUMBER: _ClassVar[int]
    actionDefinitionEnc: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, actionDefinitionEnc: _Optional[_Iterable[int]] = ...) -> None: ...

class DecodeIndMessageRequest(_message.Message):
    __slots__ = ("timestamp", "indicationHeader", "indicationMessage")
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    INDICATIONHEADER_FIELD_NUMBER: _ClassVar[int]
    INDICATIONMESSAGE_FIELD_NUMBER: _ClassVar[int]
    timestamp: int
    indicationHeader: bytes
    indicationMessage: bytes
    def __init__(self, timestamp: _Optional[int] = ..., indicationHeader: _Optional[bytes] = ..., indicationMessage: _Optional[bytes] = ...) -> None: ...

class MeasData(_message.Message):
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

class UeMeasData(_message.Message):
    __slots__ = ("UEID", "measData", "granularityPeriod")
    UEID_FIELD_NUMBER: _ClassVar[int]
    MEASDATA_FIELD_NUMBER: _ClassVar[int]
    GRANULARITYPERIOD_FIELD_NUMBER: _ClassVar[int]
    UEID: int
    measData: _containers.RepeatedCompositeFieldContainer[MeasData]
    granularityPeriod: int
    def __init__(self, UEID: _Optional[int] = ..., measData: _Optional[_Iterable[_Union[MeasData, _Mapping]]] = ..., granularityPeriod: _Optional[int] = ...) -> None: ...

class DecodeIndMessageResponse(_message.Message):
    __slots__ = ("latency_ms", "ueMeasData")
    LATENCY_MS_FIELD_NUMBER: _ClassVar[int]
    UEMEASDATA_FIELD_NUMBER: _ClassVar[int]
    latency_ms: float
    ueMeasData: _containers.RepeatedCompositeFieldContainer[UeMeasData]
    def __init__(self, latency_ms: _Optional[float] = ..., ueMeasData: _Optional[_Iterable[_Union[UeMeasData, _Mapping]]] = ...) -> None: ...
