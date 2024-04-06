import random
from typing import Dict
from grpc import StatusCode, RpcError

from proto import raft_pb2_grpc, raft_pb2
from src.raft_init import get_node_stubs_other_than, confirm


class DBZClient:
    def __init__(self, stubs: Dict[int, raft_pb2_grpc.RaftServiceStub]):
        self.current_leader_id = 1
        self.nodes_and_stubs = stubs
        self.run = True

    def menu(self):
        print("Welcome to DBZ, the database that even Goku can't defeat!")
        menu_string = """Usage:
1) SET {key} {value}
2) GET {key}
3) EXIT
        """
        while self.run:
            print(menu_string)
            request = input()
            request = request.split(' ')
            if request[0] not in {'SET', 'GET', 'EXIT'}:
                print('Invalid operation!')
                continue
            if request[0] == 'EXIT':
                self.run = False
                break
            request = " ".join(request)
            self.request_server(request)

    def request_server(self, request: str):
        """
        Ackshually I will keep on trying to get a response from the leader.
        And keep on trying until I get a success.
        """
        while True:
            try:
                response: raft_pb2.ClientReply = self.nodes_and_stubs[self.current_leader_id].ServeClient(raft_pb2.ClientRequest(request=request))
                # If I did not contact the leader I cannot break the loop
                if response.success:
                    print('Request served: {}'.format(response.data))
                    return
                # if I heard that the leader is None, well. This control branch is probably not
                # going to be called, though.
                if response.leader_id is None:
                    print('DBZError!')
                    self.current_leader_id = random.randint(1, len(self.nodes_and_stubs))
                    return
                # well, time to set the leader
                print('Did not find leader, so setting leader to {}'.format(response.leader_id))
                self.current_leader_id = response.leader_id
            except RpcError as rpc_error:
                if rpc_error.code() == StatusCode.UNAVAILABLE:
                    print('Sent a request to a dead leader!')
                    self.current_leader_id = random.randint(1, len(self.nodes_and_stubs))


def main():
    client = DBZClient(get_node_stubs_other_than('', -1))
    confirm()
    client.menu()


main()

