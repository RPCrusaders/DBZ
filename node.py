from threading import Thread
import time

from raft_init import confirm, serve, get_node_stubs_other_than
from node_implementation import Node
from proto import raft_pb2

node = Node(1)
thread = Thread(target=serve, args=('50051', node))
thread.start()
time.sleep(1)
confirm()

node.other_nodes = get_node_stubs_other_than('localhost:50051')
for stub in node.other_nodes:
    args = {
        "term": 1,
        "candidate_id": 2,
        "last_log_index": 3,
        "last_log_term": 4
    }
    response = stub.RequestVote(raft_pb2.VoteRequest(**args))
    print(response.vote_granted)
    while True:
        pass




