from typing import Dict
from grpc import StatusCode, RpcError

from proto import raft_pb2_grpc, raft_pb2
from raft_init import get_node_stubs_other_than, confirm


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
            self.request_server(request)

    def request_server(self, request:str):
        try:
            response: raft_pb2.ClientReply = self.nodes_and_stubs[self.current_leader_id].ServeClient(raft_pb2.ClientRequest(request=request))
            if response.success:
                print('Request served: {}'.format(response.data))
                return

        # the following code will only be executed if the leader wasn't contacted
        # or if the 'leader' was down
        except RpcError as rpc_error:
            if rpc_error.code() == StatusCode.UNAVAILABLE:
                print('The node {} is down! OHHH NO!'.format(self.current_leader_id))
            else:
                print('That did not work out for you lil buddy, and we will never know why.')

        for node, stub in self.nodes_and_stubs.items():
            try:
                response = stub.ServeClient(raft_pb2.ClientRequest(request))
                if not response.success:
                    continue
                self.current_leader_id = response.leader_id
                print('Received from the server: {}'.format(response.data))
            except RpcError as rpc_error:
                if rpc_error.code() == StatusCode.UNAVAILABLE:
                    print('The node {} is down! OHHH NO!'.format(node))
                else:
                    print('That did not work out for you lil buddy, and we will never know why.')


def main():
    client = DBZClient(get_node_stubs_other_than('', -1))
    client.request_server('SET ur mom')
    # confirm()
    # client.menu()


main()
