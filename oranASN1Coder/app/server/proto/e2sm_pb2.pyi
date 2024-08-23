from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class EventTriggerDefFmt1Resquest(_message.Message):
    __slots__ = ("reportingPeriod",)
    REPORTINGPERIOD_FIELD_NUMBER: _ClassVar[int]
    reportingPeriod: int
    def __init__(self, reportingPeriod: _Optional[int] = ...) -> None: ...

class EncodedEventTriggerDefResponse(_message.Message):
    __slots__ = ("encodedEventTriggerDefinition",)
    ENCODEDEVENTTRIGGERDEFINITION_FIELD_NUMBER: _ClassVar[int]
    encodedEventTriggerDefinition: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, encodedEventTriggerDefinition: _Optional[_Iterable[int]] = ...) -> None: ...

class ActDefFmt4Request(_message.Message):
    __slots__ = ("measNameList", "granularityPeriod")
    MEASNAMELIST_FIELD_NUMBER: _ClassVar[int]
    GRANULARITYPERIOD_FIELD_NUMBER: _ClassVar[int]
    measNameList: _containers.RepeatedScalarFieldContainer[str]
    granularityPeriod: int
    def __init__(self, measNameList: _Optional[_Iterable[str]] = ..., granularityPeriod: _Optional[int] = ...) -> None: ...

class EncodedActDefResponse(_message.Message):
    __slots__ = ("encodedActionDefinition",)
    ENCODEDACTIONDEFINITION_FIELD_NUMBER: _ClassVar[int]
    encodedActionDefinition: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, encodedActionDefinition: _Optional[_Iterable[int]] = ...) -> None: ...

class MeasListByReportStyleRequest(_message.Message):
    __slots__ = ("encodedRanFunctionDefinition", "ReportStyleType")
    ENCODEDRANFUNCTIONDEFINITION_FIELD_NUMBER: _ClassVar[int]
    REPORTSTYLETYPE_FIELD_NUMBER: _ClassVar[int]
    encodedRanFunctionDefinition: str
    ReportStyleType: int
    def __init__(self, encodedRanFunctionDefinition: _Optional[str] = ..., ReportStyleType: _Optional[int] = ...) -> None: ...

class MeasListResponse(_message.Message):
    __slots__ = ("measList",)
    MEASLIST_FIELD_NUMBER: _ClassVar[int]
    measList: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, measList: _Optional[_Iterable[str]] = ...) -> None: ...
