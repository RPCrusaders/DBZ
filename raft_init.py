# This makes the files cleaner but might make testing difficult

from typing import Set
import grpc
from concurrent import futures

from proto import raft_pb2, raft_pb2_grpc


addresses = {
    'localhost:50051',
    'localhost:50052'
}


def get_node_stubs_other_than(current_node_address: str):
    addresses.remove(current_node_address)

    stubs: Set = set()
    for address in addresses:
        channel = grpc.insecure_channel(target=address)
        stub = raft_pb2_grpc.RaftServiceStub(channel=channel)
        stubs.add(stub)
    return stubs


def serve(node_port: str, node):
    port = node_port
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServiceServicer_to_server(node, server=server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server on node {} started, listening on port {}.".format(node.id, port))
    server.wait_for_termination()


def confirm():
    input("Please press enter when the nodes are up to continue with the demonstration...\n")
    print("Let us commence.")
