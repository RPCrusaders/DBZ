from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class VoteRequest(_message.Message):
    __slots__ = ("term", "candidate_id", "last_log_index", "last_log_term")
    TERM_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    candidate_id: int
    last_log_index: int
    last_log_term: int
    def __init__(self, term: _Optional[int] = ..., candidate_id: _Optional[int] = ..., last_log_index: _Optional[int] = ..., last_log_term: _Optional[int] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ("node_id", "term", "vote_granted")
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTE_GRANTED_FIELD_NUMBER: _ClassVar[int]
    node_id: int
    term: int
    vote_granted: bool
    def __init__(self, node_id: _Optional[int] = ..., term: _Optional[int] = ..., vote_granted: bool = ...) -> None: ...

class LogRequest(_message.Message):
    __slots__ = ("term", "leader_id", "prev_log_index", "prev_log_term", "logs", "leader_commit_index")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    LEADER_COMMIT_INDEX_FIELD_NUMBER: _ClassVar[int]
    term: int
    leader_id: int
    prev_log_index: int
    prev_log_term: int
    logs: _containers.RepeatedCompositeFieldContainer[LogEntry]
    leader_commit_index: int
    def __init__(self, term: _Optional[int] = ..., leader_id: _Optional[int] = ..., prev_log_index: _Optional[int] = ..., prev_log_term: _Optional[int] = ..., logs: _Optional[_Iterable[_Union[LogEntry, _Mapping]]] = ..., leader_commit_index: _Optional[int] = ...) -> None: ...

class LogResponse(_message.Message):
    __slots__ = ("follower_id", "term", "acked_length", "success")
    FOLLOWER_ID_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    ACKED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    follower_id: int
    term: int
    acked_length: int
    success: bool
    def __init__(self, follower_id: _Optional[int] = ..., term: _Optional[int] = ..., acked_length: _Optional[int] = ..., success: bool = ...) -> None: ...

class LogEntry(_message.Message):
    __slots__ = ("term", "msg")
    TERM_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    term: int
    msg: str
    def __init__(self, term: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...

class ClientRequest(_message.Message):
    __slots__ = ("request",)
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    request: str
    def __init__(self, request: _Optional[str] = ...) -> None: ...

class ClientReply(_message.Message):
    __slots__ = ("data", "leader_id", "success")
    DATA_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    data: str
    leader_id: int
    success: bool
    def __init__(self, data: _Optional[str] = ..., leader_id: _Optional[int] = ..., success: bool = ...) -> None: ...

class FollowerAckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FollowerAckResponse(_message.Message):
    __slots__ = ("committed_length",)
    COMMITTED_LENGTH_FIELD_NUMBER: _ClassVar[int]
    committed_length: int
    def __init__(self, committed_length: _Optional[int] = ...) -> None: ...

class broadcasted_msg(_message.Message):
    __slots__ = ("term", "candidate_id", "last_log_index", "last_log_term")
    TERM_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_INDEX_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    candidate_id: int
    last_log_index: int
    last_log_term: int
    def __init__(self, term: _Optional[int] = ..., candidate_id: _Optional[int] = ..., last_log_index: _Optional[int] = ..., last_log_term: _Optional[int] = ...) -> None: ...

class broadcast_response(_message.Message):
    __slots__ = ("success",)
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    success: bool
    def __init__(self, success: bool = ...) -> None: ...
