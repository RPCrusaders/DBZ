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
    while True:
        vote_request = {
            "term": node.current_term,
            "candidate_id": node.id,
            "last_log_index": -1,
            "last_log_term": -1
        }
        for stub in node.other_nodes:
            try:
                response = stub.RequestVote(raft_pb2.VoteRequest(**vote_request))
                print(response.vote_granted)
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    # currently can't tell which request failed, can add that later
                    # by changing type of other_nodes to dict instead of set
                    print('The node is down!')


# Broadcast AppendEntries requests to all other nodes
def broadcast_append_entries(node: Node):
    while True:
        append_entries_request = {
            "term": node.current_term,
            "leader_id": node.current_leader,
            "prev_log_index": 1,
            "prev_log_term": 1,
            "logs": [],
            "leader_commit_index": 1
        }
        for stub in node.other_nodes:
            try:
                response = stub.AppendEntries(raft_pb2.AppendEntriesRequest(**append_entries_request))
                print(response.term)
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    # currently can't tell which request failed, can add that later
                    # by changing type of other_nodes to dict instead of set
                    print('The node is down!')


def main(args):
    # start listening for RPC requests from other nodes
    node = Node(args.id)
    port = args.address.split(':')[-1]
    thread = Thread(target=serve, args=(port, node))
    thread.start()
    node.other_nodes = get_node_stubs_other_than(args.address)
    time.sleep(1)
    confirm()

    append_entries_thread = Thread(target=broadcast_append_entries, args=(node, ))
    request_vote_thread = Thread(target=broadcast_request_vote, args=(node, ))

    append_entries_thread.start()
    request_vote_thread.start()

    # Broadcast RequestVote RPCs to all other nodes
    # node.broadcast(message={
    #     "term": 1,
    #     "candidate_id": node.id,
    #     "last_log_index": -1,
    #     "last_log_term": -1
    # })

    # this is needed to keep the node alive
    while True:
        pass


if __name__ == '__main__':
    args = parse_args()
    main(args)
