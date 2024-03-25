# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\"`\n\x0bVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\x05\x12\x16\n\x0elast_log_index\x18\x03 \x01(\x05\x12\x15\n\rlast_log_term\x18\x04 \x01(\x05\"2\n\x0cVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0cvote_granted\x18\x02 \x01(\x08\"\x87\x01\n\nLogRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x16\n\x0eprev_log_index\x18\x03 \x01(\x05\x12\x15\n\rprev_log_term\x18\x04 \x01(\x05\x12\x0c\n\x04logs\x18\x05 \x03(\t\x12\x1b\n\x13leader_commit_index\x18\x06 \x01(\x05\",\n\x0bLogResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\" \n\rClientRequest\x12\x0f\n\x07request\x18\x01 \x01(\t\"?\n\x0b\x43lientReply\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x0f\n\x07success\x18\x03 \x01(\x08\x32\x91\x01\n\x0bRaftService\x12,\n\x0bRequestVote\x12\x0c.VoteRequest\x1a\r.VoteResponse\"\x00\x12\'\n\x08SendLogs\x12\x0b.LogRequest\x1a\x0c.LogResponse\"\x00\x12+\n\x0bServeClient\x12\x0e.ClientRequest\x1a\x0c.ClientReplyb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_VOTEREQUEST']._serialized_start=14
  _globals['_VOTEREQUEST']._serialized_end=110
  _globals['_VOTERESPONSE']._serialized_start=112
  _globals['_VOTERESPONSE']._serialized_end=162
  _globals['_LOGREQUEST']._serialized_start=165
  _globals['_LOGREQUEST']._serialized_end=300
  _globals['_LOGRESPONSE']._serialized_start=302
  _globals['_LOGRESPONSE']._serialized_end=346
  _globals['_CLIENTREQUEST']._serialized_start=348
  _globals['_CLIENTREQUEST']._serialized_end=380
  _globals['_CLIENTREPLY']._serialized_start=382
  _globals['_CLIENTREPLY']._serialized_end=445
  _globals['_RAFTSERVICE']._serialized_start=448
  _globals['_RAFTSERVICE']._serialized_end=593
# @@protoc_insertion_point(module_scope)
