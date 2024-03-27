from concurrent import futures
import logging
import random
import threading
import time

import grpc
import tmp_pb2
import tmp_pb2_grpc




# enum State {FOLLOWER, CANDIDATE, LEADER}
FOLLOWER = 0
CANDIDATE = 1
LEADER = 2


class Node:
    def __init__(self, id, timeout_min=150, timeout_max=300):
        self.id = id
        self.timeout_min = timeout_min
        self.timeout_max = timeout_max
        self.reset_election_timeout()
        self.current_term = 0
        self.voted_for = None
        self.current_role = FOLLOWER
        self.votes_received = -1

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
        self.current_role = CANDIDATE
        self.votes_received = 0
        # Send RequestVote RPCs to all other servers
        # If votes received from majority of servers: become leader


    def run(self):
        while True:
            self.reset_election_timeout()
            self.start_election_timer()
            time.sleep(5)


class VotingService(tmp_pb2_grpc.VotingService):
    def RequestVote(self, request, context):
        global current_term
        global voted_for
        global current_role
        global votes_received
        if request.term < current_term:
            return tmp_pb2.VoteReply(term=current_term, voteGranted=False)
        if request.term > current_term:
            current_term = request.term
            voted_for = None
            current_role = FOLLOWER
        if voted_for is None or voted_for == request.candidateId:
            voted_for = request.candidateId
            return tmp_pb2.VoteReply(term=current_term, voteGranted=True)
        return tmp_pb2.VoteReply(term=current_term, voteGranted=False)

    def Heartbeat(self, request, context):
        global current_term
        global current_role
        global votes_received
        global voted_for
        if current_term > request.term:
            return tmp_pb2.HeartbeatReply(term=current_term, success=False)
        if request.term >= current_term:
            current_term = request.term
            current_role = FOLLOWER
            votes_received = -1
        if voted_for == request.leaderId:
            return tmp_pb2.HeartbeatReply(term=current_term, success=True)
        return tmp_pb2.HeartbeatReply(term=current_term, success=False)


def serve():
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    tmp_pb2_grpc.add_VotingServiceServicer_to_server(VotingService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("Server started, listening on " + port)
    server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig()
    serve()