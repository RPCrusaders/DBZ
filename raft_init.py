# This makes the files cleaner but might make testing difficult

from typing import Dict
import grpc
from concurrent import futures

from proto import raft_pb2_grpc


addresses = {
    1: '10.190.0.5:50051',
    2: '10.190.0.6:50051',
    3: '10.190.0.7:50051',
    4: '10.190.0.8:50051',
    5: '10.190.0.9:50051'
}


def get_node_stubs_other_than(current_node_address: str, current_node:int):
    if current_node_address in addresses:
        # addresses.remove(current_node_address)
        del addresses[current_node]

    stubs: Dict[int, raft_pb2_grpc.RaftServiceStub] = dict()
    for node, address in addresses.items():
        channel = grpc.insecure_channel(target=address)
        stub = raft_pb2_grpc.RaftServiceStub(channel=channel)
        stubs[node] = stub
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
