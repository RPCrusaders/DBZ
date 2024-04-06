import random
import threading
from collections import namedtuple
from math import ceil
from typing import List, Dict
import time
import grpc
from .dbz_logger import DBZLogger
from pathlib import Path
from proto import raft_pb2, raft_pb2_grpc
from .roles import Role

log_entry = namedtuple('log_entry', ['msg', 'term'])


class Node(raft_pb2_grpc.RaftServiceServicer):
    def __init__(self, _id, timeout_min=5000, timeout_max=10000):
        self.election_timeout = None
        self.election_timer = None
        self.id = _id
        self.timeout_min = timeout_min
        self.timeout_max = timeout_max
        # self.broadcast_thread = None

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

        #logger
        self.logger = DBZLogger(self.id)
        self.other_nodes_stubs = {}

        # the point of DBZ
        self.db_hashmap: Dict[str, str] = {}
        self.init_db_state()

    def reset_election_timeout(self):
        self.stop_election_timer()  # Stop the election timer if it's running
        self.election_timeout = random.randint(self.timeout_min,
                                               self.timeout_max) / 1000.0  # Set a new random election timeout
        self.start_election_timer()  # Start the election timer

    def start_election_timer(self):
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()

    def stop_election_timer(self):
        # print(self.election_timer)
        if self.election_timer:
            # print(f"Server {self.id}: Election timer stopped")
            self.election_timer.cancel()

    def start_election(self):
        self.logger.write_dump(f"Election timeout expired. Starting election...")
        self.stop_election_timer()
        self.current_term += 1
        self.voted_for = self.id
        self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)

        self.current_role = Role.CANDIDATE
        self.votes_received = 1
        self.voters = [self.id]
        vote_request = {
            "c_term": self.current_term,
            "c_id": self.id,
            "c_log_length": len(self.log),
            "c_log_term": self.log[-1].term if len(self.log) > 0 else 0
        }
        for node, stub in self.other_nodes_stubs.items():
            if node == self.id:
                continue
            try:
                response = stub.RequestVote(raft_pb2.VoteRequest(**vote_request))
                print(
                    f"Node {self.id} received vote from {response.node_id} for term {response.term}, vote granted: {response.vote_granted}")
                if response.vote_granted and self.current_role == Role.CANDIDATE and self.current_term == response.term:
                    self.votes_received += 1

                    self.voters.append(response.node_id)
                else:
                    self.logger.write_dump(
                        f"Node {self.id} did not receive vote from {response.node_id} for term {response.term}")
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    self.logger.write_dump(f"Error while sending RPC request to: {node}")
                    # assuming the down node is not a candidate
                    self.votes_received += 1

        required_votes = ceil((len(self.other_nodes_stubs) + 1) / 2)
        # print(f"Server {self.id}: Received {self.votes_received} votes. Needed {required_votes} votes.")
        if self.votes_received >= required_votes:
            self.logger.write_dump(
                f"Server {self.id}: Election successful. Received {self.votes_received} votes. Needed {required_votes} votes.")
            self.current_role = Role.LEADER
            self.current_leader = self.id
            self.sent_length[self.id] = len(self.log)
            self.acked_length[self.id] = len(self.log)
            for node, stub in self.other_nodes_stubs.items():
                if node == self.id:
                    continue
                self.sent_length[node] = 0
                self.acked_length[node] = 0
                self.replicate_log(self.id, node)
            self.stop_election_timer()

            # leader routine
            self.LeaderRoutine()

        else:
            self.logger.write_dump(
                f"Election failed. Received {self.votes_received} votes. Needed {len(self.other_nodes_stubs) + 1 // 2} votes.")
            # self.current_term = old_term
            self.current_role = Role.FOLLOWER
            self.voted_for = -1
            self.stop_election_timer()
            # self.reset_election_timeout()
            # self.start_election_timer()
        return
        # Send RequestVote RPCs to all other servers
        # If votes received from majority of servers: become leader

    # TODO: (Raft 4/9): Periodically send heartbeats to other servers. Also, broadcast the commit index to other servers periodically
    def LeaderRoutine(self):
        """
        Method that is called when a node becomes a leader. 
        Does periodic tasks like sending heartbeats to all followers to maintain leadership.
        Args:
            None
        Returns:
            None
        """
        while self.current_role == Role.LEADER:
            # sleep for 0.3 of the minimum timeout
            self.logger.write_dump(f"Sending heartbeats to all followers.")
            for follower_id, stub in self.other_nodes_stubs.items():
                if follower_id == self.id:
                    continue
                self.replicate_log(self.id, follower_id)
                time.sleep(self.timeout_min * 0.3 / 1000.0)
                if self.current_role != Role.LEADER:
                    self.logger.write_dump(f"Stepping down.")

    # RPC related section
    def RequestVote(self, request: raft_pb2.VoteRequest, context):
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
        cId = request.c_id
        cTerm = request.c_term
        cLogLength = request.c_log_length
        cLogTerm = request.c_log_term

        if cTerm > self.current_term:
            self.current_term = cTerm
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)
            self.voted_for = None
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)
            self.current_role = Role.FOLLOWER
            self.stop_election_timer()
            print(f"Server {self.id}: Updated term to {cTerm} and voted for {cId}")

        last_term = 0

        if len(self.log) > 0:
            last_term = self.log[-1].term

        logOk = cLogTerm > last_term or (cLogTerm == last_term and cLogLength >= len(self.log))

        if cTerm == self.current_term and (self.voted_for is None or self.voted_for == cId) and logOk:
            self.voted_for = cId
            ret_args = {
                "term": cTerm,
                "node_id": self.id,
                "vote_granted": True
            }
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)
            self.logger.write_dump(f"Voted for {cId} in term {cTerm}")
        else:
            ret_args = {
                "term": cTerm,
                "node_id": self.id,
                "vote_granted": False
            }
            self.logger.write_dump(f"Did not vote for {cId} in term {cTerm}")

        self.reset_election_timeout()
        # self.start_election_timer()
        return raft_pb2.VoteResponse(**ret_args)

    def ServeClient(self, request: raft_pb2.ClientRequest, context):
        """
        Method for handling client requests.
        """
        if self.current_role is not Role.LEADER:
            return raft_pb2.ClientReply(data='', leader_id=self.current_leader, success=False)

        request_string = request.request
        request_string = request_string.split(' ')

        # GET K
        self.logger.write_dump(f"(Leader) Received request: {request_string}")
        if request_string[0] == 'GET':
            key = request_string[1]
            data = self.db_hashmap.get(key)
            if data is None:
                data = ""
            # self.logger.write_logs("{} {}".format(request.request, self.current_term))
            return raft_pb2.ClientReply(data=data, leader_id=self.current_leader, success=True)
        # SET K V
        elif request_string[0] == 'SET':
            key = request_string[1]
            value = request_string[2]
            self.db_hashmap[key] = value
            data = 'Successfully set {} to {}'.format(key, value)
            self.logger.write_logs("{} {}".format(request.request, self.current_term))
            self.log.append(raft_pb2.LogEntry(term=self.current_term, msg=request.request))
            return raft_pb2.ClientReply(data=data, leader_id=self.current_leader, success=True)

    def init_db_state(self):
        file_path = f"./log_nodes_{self.id}"
        Path(file_path).mkdir(parents=True, exist_ok=True)
        try:
            with open(f"log_nodes_{self.id}/logs.txt", "r") as logs_file:
                history = logs_file.readlines()
                for request in history:
                    self.execute_db_command(request)
        except:
            print(f"FRESH AS A NEWBORN BABY: Server {self.id}")

    def execute_db_command(self, request: str):
        tokens = request.split(" ")
        command = tokens[0]
        if command == "NO-OP":
            return
        # else the command is assumed to be always SET
        key = tokens[1]
        value = tokens[2]
        self.db_hashmap[key] = value

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
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)
            # cancel election timer
            self.stop_election_timer()

        if request.term == self.current_term:
            self.current_role = Role.FOLLOWER
            self.current_leader = request.leader_id

        # Reset election timer
        self.reset_election_timeout()

        # print(self.log, request.prev_log_index, request.prev_log_term, request.logs, request.leader_commit_index)
        flag = len(self.log) >= request.prev_log_index and (
                request.prev_log_index <= 0 or self.log[request.prev_log_index - 1].term == request.prev_log_term)
        # print(request.term , self.current_term , flag)
        if request.term == self.current_term and flag:
            # append log entries
            # print(f"Server {self.id}: Appending log entries with log size {len(self.log)}")
            self.append_log_entries(request.prev_log_index, request.leader_commit_index, request.logs)
            ack = request.prev_log_index + len(request.logs)  # original pseudocode does not use min
            self.logger.write_dump(f"Log entries accepted from leader {request.leader_id}")
            ret_args = {
                "follower_id": request.leader_id,
                "term": request.term,
                "acked_length": ack,
                "success": True
            }

        else:
            self.logger.write_dump(f"Log entries rejected from leader {request.leader_id}")
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
        success = True
        if self.current_role == Role.LEADER:
            self.log.append(raft_pb2.LogEntry(msg=message, term=self.current_term))
            self.acked_length[self.id] = len(self.log)
            for follower_id, follower_stub in self.other_nodes_stubs.items():
                self.replicate_log(self.id, follower_id)
                print(f"Server {self.id}: Sent log entries to server {follower_id}")
        else:
            print(f"Server {self.id}: I am not the leader. Forwarding the message to the leader.")
            try:
                stub = self.other_nodes_stubs[self.current_leader]
                return stub.broadcast(message)
            except AttributeError:
                print(f"Server {self.id}: Leader {self.current_leader} is down!!")
                success = False
        print(f"Server {self.id}: Broadcasted message to all other nodes successfully")
        return {"success": success}

    # TODO: implement the functions for receiving LogRequest, sending LogResponse, and receiving LogResponse

    def replicate_log(self, leader_id, follower_id):
        """
        TODO: This function is called by the leader to send log entries to a follower
        TODO: implement functionality for sending LogRequest
        """
        prefix_length = self.sent_length[follower_id]
        suffix = self.log[prefix_length:]
        # print(f"Server {self.id}: Replicating log entries to server {follower_id} with prefix length {prefix_length} and suffix {suffix}")
        prefix_term = 0

        if prefix_length > 0:
            prefix_term = self.log[prefix_length - 1].term

        # Send LogRequest to follower
        for _follower_id, stub in self.other_nodes_stubs.items():
            if _follower_id == follower_id:
                try:
                    log_response = stub.SendLogs(
                        raft_pb2.LogRequest(term=self.current_term,
                                            leader_id=leader_id,
                                            prefix_length=prefix_length,
                                            prefix_term=prefix_term,
                                            logs=suffix,
                                            leader_commit_index=self.commit_length)
                    )
                    print(f"Server {self.id}: Sent LogRequest to server {follower_id}")
                    self._receive_log_response(log_response)
                except grpc.RpcError as rpc_error:
                    if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                        self.logger.write_dump(f"Error while sending RPC request to: {follower_id}")
                        self.sent_length[follower_id] = 0
                        self.acked_length[follower_id] = 0
                    # else:
                    #     self.logger.write_dump(f"Error while sending RPC request to: {follower_id}")
                    #     self.sent_length[follower_id] = 0
                    #     self.acked_length[follower_id] = 0

        print(f"Received LogResponse from server {follower_id}")

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
                self.replicate_log(self.id,
                                   log_response.follower_id)  # Question: Could this possibly lead to infinite recursion in some case?

        elif log_response.term > self.current_term:
            self.current_term = log_response.term
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)
            self.current_role = Role.FOLLOWER
            self.voted_for = None
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)
            self.stop_election_timer()

    def append_log_entries(self, prefix_length: int, leader_commit: int, suffix):
        """
        A follower will call this method to extend logs with entries received from leader.
        Args:
            prefix_length: Number of log entries that precede the new suffix.
            leader_commit: Something I will have to confirm later
            suffix: Remaining log entries
        """
        # print(f"Server {self.id}: The prefix length is {prefix_length} and the suffix is {suffix} and the log length is {len(self.log)}")
        if (len(suffix) > 0) and (len(self.log) > prefix_length):
            index = min(len(self.log), prefix_length + len(suffix)) - 1
            if self.log[index].term != suffix[index - prefix_length].term:
                self.log = [self.log[i] for i in range(prefix_length - 1)]

        # print(f"Server {self.id}: The prefix length is {prefix_length} and the suffix is {suffix} and the log length is {len(self.log)}")
        if prefix_length + len(suffix) > len(self.log):
            for i in range(len(self.log) - prefix_length, len(suffix)):
                # print('Appending this thing', suffix[i])
                self.log.append(suffix[i])
                tmp = suffix[i].msg.split(' ')
                if tmp[0].upper() == 'SET':
                    key = tmp[1]
                    value = tmp[2]
                    self.db_hashmap[key] = value
                self.logger.write_logs("{} {}".format(suffix[i].msg, suffix[i].term))
                self.logger.write_dump(f"Committing log entry (follower) {suffix[i].msg} with term {suffix[i].term}")

        if leader_commit > self.commit_length:
            for i in range(self.commit_length, leader_commit):
                # TODO: deliver self.log[i] to application (?)
                pass
            self.commit_length = leader_commit
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)

    def DetermineFollowerAcks(self, request: raft_pb2.FollowerAckRequest, context):
        return raft_pb2.FollowerAckResponse(self.commit_length)

    def commit_log_entries(self):
        # define acks(len) = number of nodes who have acknowledged the receipt of len logs or more
        min_acks = len(self.other_nodes_stubs) + 1
        ready = set()
        acks_len_set = set()
        for node, stub in self.other_nodes_stubs.items():
            try:
                response: raft_pb2.FollowerAckResponse = stub.DetermineFollowerAcks(raft_pb2.FollowerAckRequest())
                acks_len_set.add(response.committed_length)
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    self.logger.write_dump(f"Error while sending RPC request to: {node}")

        for i in range(1, len(self.log)):
            counter = 0
            for j in acks_len_set:
                if j >= min_acks:
                    counter += 1
            if counter >= min_acks:
                ready.add(i)

        if (len(ready) != 0) and (max(ready) > self.commit_length) and (
                self.log[max(ready) - 1].term == self.current_term):
            for i in range(self.commit_length, max(ready)):
                # TODO: deliver self.log[i] to application (?)
                pass
            self.commit_length = max(ready)
            self.logger.write_metadata(self.commit_length, self.current_term, self.voted_for)
