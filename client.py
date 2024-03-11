import random
import threading
import time

class RaftServer:
    def __init__(self, server_id, timeout_min=150, timeout_max=300):
        self.server_id = server_id
        self.timeout_min = timeout_min
        self.timeout_max = timeout_max
        self.election_timer = None
        self.reset_election_timeout()

    def reset_election_timeout(self):
        # Generate a random timeout value within the specified range
        self.election_timeout = random.randint(self.timeout_min, self.timeout_max) / 1000.0  # Convert to seconds
        print(f"Server {self.server_id}: Election timeout set to {self.election_timeout:.3f} seconds")

    def start_election_timer(self):
        # Start a timer to trigger an election when the timeout expires
        self.election_timer = threading.Timer(self.election_timeout, self.start_election)
        self.election_timer.start()

    def stop_election_timer(self):
        # Stop the election timer if it's running
        if self.election_timer and self.election_timer.is_alive():
            print(f"Server {self.server_id}: Election timer stopped")
            self.election_timer.cancel()

    def receive_heartbeat(self):
        # Reset the election timeout upon receiving a heartbeat
        print(f"Server {self.server_id}: Received heartbeat")

        self.stop_election_timer()
        self.start_election_timer()

    def start_election(self):
        print(f"Server {self.server_id}: Election timeout expired. Starting election...")
        # Transition to the candidate state and initiate a new election term

    def run(self):
        # Simulate server operation by continuously resetting the election timeout
        while True:
            self.stop_election_timer()
            self.reset_election_timeout()
            self.start_election_timer()
            time.sleep(0.16)  # Simulate server operation (e.g., handling client requests)

# Example usage
server1 = RaftServer(server_id=1)
server1.run()  # This will continuously reset the election timeout and simulate server operation
