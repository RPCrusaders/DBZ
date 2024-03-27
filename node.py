from threading import Thread
import time
import grpc
import argparse

from node_implementation import Node
from proto import raft_pb2
from raft_init import confirm, serve, get_node_stubs_other_than


def parse_args():
    parser = argparse.ArgumentParser(description='Start a Raft node')
    parser.add_argument('--id', type=int, help='ID of the node')
    parser.add_argument('--address', type=str, help='Address of the node in the format ip:port')
    return parser.parse_args()


# Broadcast RequestVote requests to all other nodes
def broadcast_request_vote(node: Node):
    vote_request = {
        "term": node.current_term,
        "candidate_id": node.id,
        "last_log_index": -1,
        "last_log_term": -1
    }
    for stub in node.other_nodes_stubs.items():
        try:
            response = stub.RequestVote(raft_pb2.VoteRequest(**vote_request))
            print(f"Node {node.id} received vote from {response.node_id} for term {response.term}, vote granted: {response.vote_granted}")
        except grpc.RpcError as rpc_error:
            if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                print('The node {} is down!'.format(node))

    node.reset_election_timeout()
    node.start_election_timer()
    return


# Broadcast SendLogs requests to all other nodes
def broadcast_send_logs(node: Node):
    while True:
        append_entries_request = {
            "term": node.current_term,
            "leader_id": node.current_leader,
            "prev_log_index": 1,
            "prev_log_term": 1,
            "logs": [raft_pb2.LogEntry(term=1, msg="bruhhh")],
            "leader_commit_index": 1
        }
        for node, stub in node.other_nodes_stubs.items():
            try:
                response = stub.SendLogs(raft_pb2.LogRequest(**append_entries_request))
                print(response.term)
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    print('The node {} is down!'.format(node))


def main(args):
    # start listening for RPC requests from other nodes
    node = Node(args.id)
    port = args.address.split(':')[-1]
    print(f"Node {node.id} started at {args.address}")
    thread = Thread(target=serve, args=(port, node))
    thread.start()
    node.other_nodes_stubs = get_node_stubs_other_than(args.address, args.id)
    time.sleep(1)
    confirm()
    # start the election timer
    node.reset_election_timeout()

    # this is needed to keep the node alive
    while True:
        pass


if __name__ == '__main__':
    args = parse_args()
    main(args)
