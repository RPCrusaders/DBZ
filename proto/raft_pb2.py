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




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\"`\n\x0bVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\x05\x12\x16\n\x0elast_log_index\x18\x03 \x01(\x05\x12\x15\n\rlast_log_term\x18\x04 \x01(\x05\"C\n\x0cVoteResponse\x12\x0f\n\x07node_id\x18\x01 \x01(\x05\x12\x0c\n\x04term\x18\x02 \x01(\x05\x12\x14\n\x0cvote_granted\x18\x03 \x01(\x08\"\x92\x01\n\nLogRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x16\n\x0eprev_log_index\x18\x03 \x01(\x05\x12\x15\n\rprev_log_term\x18\x04 \x01(\x05\x12\x17\n\x04logs\x18\x05 \x03(\x0b\x32\t.LogEntry\x12\x1b\n\x13leader_commit_index\x18\x06 \x01(\x05\"W\n\x0bLogResponse\x12\x13\n\x0b\x66ollower_id\x18\x01 \x01(\x05\x12\x0c\n\x04term\x18\x02 \x01(\x05\x12\x14\n\x0c\x61\x63ked_length\x18\x03 \x01(\x05\x12\x0f\n\x07success\x18\x04 \x01(\x08\"%\n\x08LogEntry\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0b\n\x03msg\x18\x02 \x01(\t\" \n\rClientRequest\x12\x0f\n\x07request\x18\x01 \x01(\t\"?\n\x0b\x43lientReply\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\t\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x0f\n\x07success\x18\x03 \x01(\x08\"\x14\n\x12\x46ollowerAckRequest\"/\n\x13\x46ollowerAckResponse\x12\x18\n\x10\x63ommitted_length\x18\x01 \x01(\x05\"d\n\x0f\x62roadcasted_msg\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\x05\x12\x16\n\x0elast_log_index\x18\x03 \x01(\x05\x12\x15\n\rlast_log_term\x18\x04 \x01(\x05\"%\n\x12\x62roadcast_response\x12\x0f\n\x07success\x18\x01 \x01(\x08\x32\x92\x02\n\x0bRaftService\x12,\n\x0bRequestVote\x12\x0c.VoteRequest\x1a\r.VoteResponse\"\x00\x12\'\n\x08SendLogs\x12\x0b.LogRequest\x1a\x0c.LogResponse\"\x00\x12-\n\x0bServeClient\x12\x0e.ClientRequest\x1a\x0c.ClientReply\"\x00\x12\x44\n\x15\x44\x65termineFollowerAcks\x12\x13.FollowerAckRequest\x1a\x14.FollowerAckResponse\"\x00\x12\x37\n\x0c\x42roadcastMsg\x12\x10.broadcasted_msg\x1a\x13.broadcast_response\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_VOTEREQUEST']._serialized_start=14
  _globals['_VOTEREQUEST']._serialized_end=110
  _globals['_VOTERESPONSE']._serialized_start=112
  _globals['_VOTERESPONSE']._serialized_end=179
  _globals['_LOGREQUEST']._serialized_start=182
  _globals['_LOGREQUEST']._serialized_end=328
  _globals['_LOGRESPONSE']._serialized_start=330
  _globals['_LOGRESPONSE']._serialized_end=417
  _globals['_LOGENTRY']._serialized_start=419
  _globals['_LOGENTRY']._serialized_end=456
  _globals['_CLIENTREQUEST']._serialized_start=458
  _globals['_CLIENTREQUEST']._serialized_end=490
  _globals['_CLIENTREPLY']._serialized_start=492
  _globals['_CLIENTREPLY']._serialized_end=555
  _globals['_FOLLOWERACKREQUEST']._serialized_start=557
  _globals['_FOLLOWERACKREQUEST']._serialized_end=577
  _globals['_FOLLOWERACKRESPONSE']._serialized_start=579
  _globals['_FOLLOWERACKRESPONSE']._serialized_end=626
  _globals['_BROADCASTED_MSG']._serialized_start=628
  _globals['_BROADCASTED_MSG']._serialized_end=728
  _globals['_BROADCAST_RESPONSE']._serialized_start=730
  _globals['_BROADCAST_RESPONSE']._serialized_end=767
  _globals['_RAFTSERVICE']._serialized_start=770
  _globals['_RAFTSERVICE']._serialized_end=1044
# @@protoc_insertion_point(module_scope)
