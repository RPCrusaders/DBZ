from threading import Thread
import time
from grpc._channel import _InactiveRpcError
import argparse

from node_implementation import Node
from proto import raft_pb2
from raft_init import confirm, serve, get_node_stubs_other_than


def parse_args():
    parser = argparse.ArgumentParser(description='Start a Raft node')
    parser.add_argument('--id', type=int, help='ID of the node')
    parser.add_argument('--address', type=str, help='Address of the node in the format ip:port')
    return parser.parse_args()


def main(args):
    node = Node(args.id)
    port = args.address.split(':')[-1]
    thread = Thread(target=serve, args=(port, node))
    thread.start()
    time.sleep(1)
    confirm()

    node.other_nodes = get_node_stubs_other_than(args.address)
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


if __name__ == '__main__':
    args = parse_args()
    main(args)
