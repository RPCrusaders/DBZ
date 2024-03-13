import random
import threading
import time

from proto import raft_pb2, raft_pb2_grpc
from roles import Role


class Node(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, id, timeout_min=150, timeout_max=300):
        self.id = id
        self.timeout_min = timeout_min
        self.timeout_max = timeout_max
        self.reset_election_timeout()
        self.current_term = 0
        self.voted_for = None
        self.current_role = Role.FOLLOWER
        self.votes_received = -1
        self.other_nodes = set()

    def reset_election_timeout(self):
        self.election_timeout = random.randint(self.timeout_min, self.timeout_max) / 1000.0

    def start_election_timer(self):
        threading.Timer(self.election_timeout, self.start_election).start()

    def stop_election_timer(self):
        if self.election_timer and self.election_timer.is_alive():
            self.election_timer.cancel()

    def start_election(self):
        print(f"Server {self.id}: Election timeout expired. Starting election...")
        self.current_term += 1
        self.voted_for = self.id
        self.current_role = Role.CANDIDATE
        self.votes_received = 0
        # Send RequestVote RPCs to all other servers
        # If votes received from majority of servers: become leader

    def run(self):
        while True:
            self.reset_election_timeout()
            self.start_election_timer()
            time.sleep(5)

    # RPC related section
    def RequestVote(self, request, context):
        print('omg a vote request')
        print(request.term)
        print(request.candidate_id)
        print(request.last_log_index)
        print(request.last_log_term)

        ret_args = {
            "term": 1,
            "vote_granted": False
        }
        return raft_pb2.VoteReply(**ret_args)

    def Heartbeat(self, request, context):
        return raft_pb2.HeartbeatReply()
