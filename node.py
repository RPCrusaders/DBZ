from sys import argv
from threading import Thread
import time
from grpc._channel import _InactiveRpcError

from node_implementation import Node
from proto import raft_pb2
from raft_init import confirm, serve, get_node_stubs_other_than

node = Node(int(argv[1]))
ip, port = argv[2].split(':')
thread = Thread(target=serve, args=(port, node))
thread.start()
time.sleep(1)
confirm()

node.other_nodes = get_node_stubs_other_than(argv[2])
for stub in node.other_nodes:
    args = {
        "term": 1,
        "candidate_id": 2,
        "last_log_index": 3,
        "last_log_term": 4
    }
    try:
        response = stub.RequestVote(raft_pb2.VoteRequest(**args))
        print(response.vote_granted)
    except _InactiveRpcError:
        print('Node is down!!')
    while True:
        pass




