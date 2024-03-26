import random
import threading
import time
from collections import namedtuple
from math import ceil
from typing import List

from proto import raft_pb2, raft_pb2_grpc
from roles import Role

import grpc


log_entry = namedtuple('log_entry', ['msg', 'term'])


class Node(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, _id, timeout_min=10000, timeout_max=30000):
        self.election_timeout = None
        self.election_timer = None
        self.id = _id
        self.timeout_min = timeout_min
        self.timeout_max = timeout_max
        # self.reset_election_timeout()
        
        # Persistent state on all servers (Updated on stable storage before responding to RPCs)
        self.current_term = 0
        self.voted_for = None
        self.log: List[raft_pb2.LogEntry] = []
        self.commit_length = 0

        # Volatile state on all servers
        self.current_role = Role.FOLLOWER
        self.current_leader = None
        self.votes_received = 0
        self.sent_length = {}
        self.acked_length = {}

        self.other_nodes_stubs = set()

    def reset_election_timeout(self):
        self.stop_election_timer() # Stop the election timer if it's running
        self.election_timeout = random.randint(self.timeout_min, self.timeout_max) / 1000.0 #Set a new random election timeout
        self.start_election_timer() # Start the election timer

    def start_election_timer(self):
        threading.Timer(self.election_timeout, self.start_election).start()

    def stop_election_timer(self):
        if self.election_timer and self.election_timer.is_alive():
            print(f"Server {self.id}: Election timer stopped")
            self.election_timer.cancel()

    def start_election(self):
        print(f"Server {self.id}: Election timeout expired. Starting election...")
        if self.current_role == Role.LEADER:
            self.stop_election_timer()
            print(f"Server {self.id}: Already the leader. Cancelling election.")
            return
        
        self.stop_election_timer()
        self.current_term += 1
        self.voted_for = self.id
        self.current_role = Role.CANDIDATE
        self.votes_received = 1
        self.voters = [self.id]
        followers = [];
        vote_request = {
            "term": self.current_term,
            "candidate_id": self.id,
            "last_log_index": -1,
            "last_log_term": -1
        }
        for stub in self.other_nodes_stubs:
            try:
                response = stub.RequestVote(raft_pb2.VoteRequest(**vote_request))
                print(f"Node {self.id} received vote from {response.node_id} for term {response.term}, vote granted: {response.vote_granted}")
                if response.vote_granted and self.current_role == Role.CANDIDATE and self.current_term == response.term:
                    self.votes_received += 1

                    self.voters.append(response.node_id)
                if response.node_id not in followers:
                    followers.append(response.node_id)
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    # currently can't tell which request failed, can add that later
                    # by changing type of other_nodes to dict instead of set
                    # print(rpc_error.details())
                    # print(rpc_error)
                    print('The node is down!')
        
                        # break
        required_votes = ceil((len(self.other_nodes_stubs)+2) / 2)
        print(f"Server {self.id}: Received {self.votes_received} votes. Needed {required_votes} votes.")
        if self.votes_received >= required_votes:
            print(f"Server {self.id}: Election successful. Received {self.votes_received} votes. Needed {required_votes} votes.")
            self.current_role = Role.LEADER
            self.current_leader = self.id
            self.sent_length[self.id] = len(self.log)
            self.acked_length[self.id] = len(self.log)
            for follower in followers:
                self.sent_length[follower] = 0
                self.acked_length[follower] = 0
                # self.replicate_log(self.id, follower)
            self.stop_election_timer()
        else:
            print(f"Server {self.id}: Election failed. Received {self.votes_received} votes. Needed {len(self.other_nodes_stubs)+1 // 2} votes.")
            # self.current_term = old_term
            self.current_role = Role.FOLLOWER
            self.voted_for = -1
            self.reset_election_timeout()
            # self.start_election_timer()
        return
        # Send RequestVote RPCs to all other servers
        # If votes received from majority of servers: become leader

    # def run(self):
    #     while True:
    #         self.reset_election_timeout()
    #         self.start_election_timer()

    #         # TODO: (Raft 4/9): Periodically send heartbeats to other servers. Also, broadcast the commit index to other servers periodically
    #         time.sleep(5)

    # RPC related section
    def RequestVote(self, request, context):
        """
        Method that determines whether to give a vote to an incoming RequestVote request containing a VoteRequest.
        Args:
            request:VoteRequest = {term:int, candidate_id:int, last_log_index:int, last_log_term:int}
            context:Any, is part of gRPC internals
        Returns:
            ret_args:VoteReply = {term:int, vote_granted:bool}
        TODO: Update this docstring when the voting functionality has been added. We like documentation.
        """
        self.stop_election_timer()
        cId = request.candidate_id
        cTerm = request.term
        cLogLength = request.last_log_index
        cLogTerm = request.last_log_term

        if cTerm > self.current_term:
            self.current_term = cTerm
            self.voted_for = None
            self.current_role = Role.FOLLOWER
            self.stop_election_timer()
            print(f"Server {self.id}: Updated term to {cTerm} and voted for {cId}")
        
        last_term = 0

        if len(self.log) > 0:
            last_term = self.log[-1].term
        
        logOk = cLogTerm > last_term or (cLogTerm == last_term and cLogLength >= len(self.log) - 1)

        if cTerm == self.current_term and (self.voted_for is None or self.voted_for == cId):
            self.voted_for = cId
            ret_args = {
                "term": cTerm,
                "vote_granted": True
            }
        else:
            ret_args = {
                "term": cTerm,
                "vote_granted": False
            }

        self.reset_election_timeout()
        # self.start_election_timer()
        return raft_pb2.VoteResponse(**ret_args)

    def ServeClient(self, request, context):
        """
        Method for handling client requests.
        """
        ret_args = {
            "data": 'teri mummy',
            "leader_id": 69,
            "success": False
        }
        return raft_pb2.ClientReply(**ret_args)

    def SendLogs(self, request, context):
        """
        Method used for heartbeats and log updating.
        Use this method to make decisions on when the node receives a LogRequest request.
        Args:
            request:LogRequest = {term:int, leader_id:int, prev_log_index:int, prev_log_term:int,
             logs:List[raft_pb2.LogEntry: {term:int, msg:str}]
             ,leader_commit_index:int}
            context:Any, is part of gRPC internals
        Returns:
            ret_args:LogResponse = {follower_id:int, term:int, acked_length:int, success:bool}
        TODO: Update this docstring when the logging functionality has been added. We like documentation.
        """

        if request.term > self.current_term:
            self.current_term = request.term
            # self.current_role = Role.FOLLOWER
            self.voted_for = None
            # cancel election timer
            self.stop_election_timer()

        if request.term == self.current_term:
            self.current_role = Role.FOLLOWER
            self.current_leader = request.leader_id

        flag = len(self.log) > request.prev_log_index and (request.prev_log_index < 0 or self.log[request.prev_log_index].term == request.prev_log_term)
        if request.term == self.current_term and flag:
            # append log entries
            self.append_log_entries(request.prev_log_index, request.leader_commit_index, request.logs)
            ack = min(len(self.log), request.prev_log_index + len(request.logs)) # original pseudocode does not use min

            ret_args = {
                "follower_id": request.leader_id,
                "term": request.term,
                "acked_length": ack,
                "success": True
            }

        else:
            ret_args = {
                "follower_id": request.leader_id,
                "term": request.term,
                "acked_length": 0,
                "success": False
            }

        return raft_pb2.LogResponse(**ret_args)

    def broadcast(self, message):
        """
        This function broadcasts the message to all other nodes
        Args:
            message: a dictionary containing the keys 'term', 'candidate_id', 'last_log_index', 'last_log_term'
        """
        if self.current_role == Role.LEADER:
            self.log.append(log_entry(message, self.current_term))
            self.acked_length[self.id] = len(self.log)
            for follower in self.other_nodes_stubs:
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
        prefix_length = self.sent_length[follower_id]
        suffix = self.log[prefix_length:]
        prefix_term = 0

        if prefix_length > 0:
            prefix_term = self.log[prefix_length - 1].term

        # Send LogRequest to follower
        for follower in self.other_nodes_stubs:
            if follower.id == follower_id:
                log_response = follower.SendLogs(raft_pb2.LogRequest(term=self.current_term,
                                        leader_id=leader_id,
                                        prev_log_index=prefix_length,
                                        prev_log_term=prefix_term,
                                        logs=suffix,
                                        leader_commit_index=self.commit_length))

                self._receive_log_response(log_response)

    def _receive_log_response(self, log_response):
        """
        Handles the LogResponse acknowledgements from the follower
        Args:
            log_response:LogResponse = {follower_id:int, term:int, acked_length:int, success:bool}
        """

        if self.current_term == log_response.term and self.current_role == Role.LEADER:
            if log_response.success and log_response.acked_length > self.acked_length[log_response.follower_id]:
                self.sent_length[log_response.follower_id] = log_response.acked_length
                self.acked_length[log_response.follower_id] = log_response.acked_length
                # Commit log entries
                self.commit_log_entries()
            elif self.sent_length[log_response.follower_id] > 0:
                self.sent_length[log_response.follower_id] -= 1
                self.replicate_log(self.id, log_response.follower_id) # Question: Could this possibly lead to infinite recursion in some case?

        elif log_response.term > self.current_term:
            self.current_term = log_response.term
            self.current_role = Role.FOLLOWER
            self.voted_for = None
            self.stop_election_timer()

    def append_log_entries(self, prefix_length: int, leader_commit: int, suffix: List[raft_pb2.LogEntry]):
        """
        A follower will call this method to extend logs with entries received from leader.
        Args:
            prefix_length: Number of log entries that precede the new suffix.
            leader_commit: Something I will have to confirm later
            suffix: Remaining log entries
        """
        if (len(suffix) > 0) and (len(self.log) > prefix_length):
            index = min(len(self.log), prefix_length + len(suffix)) - 1
            if self.log[index].term != suffix[index - prefix_length].term:
                self.log = [self.log[i] for i in range(prefix_length - 1)]

        if prefix_length + len(suffix) > len(self.log):
            for i in range(len(self.log) - prefix_length, len(suffix) - 1):
                self.log.append(suffix[i])

        if leader_commit > self.commit_length:
            for i in range(self.commit_length, leader_commit - 1):
                # TODO: deliver self.log[i] to application (?)
                pass
            self.commit_length = leader_commit

    def commit_log_entries(self):
        # define acks(len) = number of nodes who have acknowledged the receipt of
        # len logs or more
        min_acks = len(self.other_nodes_stubs) + 1
        pass
