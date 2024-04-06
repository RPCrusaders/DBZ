from threading import Thread
import time
import argparse

from node_implementation import Node
from raft_init import confirm, serve, get_node_stubs_other_than


def parse_args():
    parser = argparse.ArgumentParser(description='Start a Raft node')
    parser.add_argument('--id', type=int, help='ID of the node')
    parser.add_argument('--address', type=str, help='Address of the node in the format ip:port')
    return parser.parse_args()


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
