import random
import threading
import time
from collections import namedtuple

from proto import raft_pb2, raft_pb2_grpc
from roles import Role


log_entry = namedtuple('log_entry', ['msg', 'term'])


class Node(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, _id, timeout_min=150, timeout_max=300):
        self.election_timeout = None
        self.election_timer = None
        self.id = _id
        self.timeout_min = timeout_min
        self.timeout_max = timeout_max
        self.reset_election_timeout()
        
        # Persistent state on all servers (Updated on stable storage before responding to RPCs)
        self.current_term = 0
        self.voted_for = None
        self.log = []
        self.commit_length = 0

        # Volatile state on all servers
        self.current_role = Role.FOLLOWER
        self.current_leader = None
        self.votes_received = 0
        self.sent_length = {}
        self.acked_length = {}

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

            # TODO: (Raft 4/9): Periodically send heartbeats to other servers. Also, broadcast the commit index to other servers periodically
            time.sleep(5)

    # RPC related section
    def RequestVote(self, request, context):
        print('omg received a vote request')
        print(request.term)
        print(request.candidate_id)
        print(request.last_log_index)
        print(request.last_log_term)

        ret_args = {
            "term": 1,
            "vote_granted": False
        }
        return raft_pb2.VoteReply(**ret_args)

    def ServeClient(self, request, context):
        ret_args = {
            "data": 'teri mummy',
            "leader_id": 69,
            "success": False
        }
        return raft_pb2.ClientReply(**ret_args)

    def AppendEntries(self, request, context):
        pass

    def broadcast(self, message):
        """
        This function broadcasts the message to all other nodes
        Args:
            message: a dictionary containing the keys 'term', 'candidate_id', 'last_log_index', 'last_log_term'
        """
        if self.current_role == Role.LEADER:
            self.log.append(log_entry(message, self.current_term))
            self.acked_length[self.id] = len(self.log)
            for follower in self.other_nodes:
                self.replicate_log(self.id, follower.id)
                print(f"Server {self.id}: Sent log entries to server {follower.id}")
        else:
            print(f"Server {self.id}: I am not the leader. Forwarding the message to the leader.")
            try:
                self.current_leader.broadcast(message)
            except AttributeError:
                print(f"Server {self.id}: Leader {self.current_leader} is down!!")

    # TODO: implement the functions for receiving LogRequest, sending LogResponse, and receiving LogResponse

    def replicate_log(self, leader_id, follower_id):
        """
        TODO: This function is called by the leader to send log entries to a follower
        TODO: implement functionality for sending LogRequest
        """
        pass

    def append_log_entries(self, prefix_length, leader_commit, suffix):
        pass

    def commit_log_entries(self):
        pass