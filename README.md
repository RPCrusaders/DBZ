# DBZ
Hey, I head your database is strong. Let me fight it!

## Developer Notes
- `node_implementation.py` contains the canonical Node class.
It also inherits the correct gRPC class so write the handling
of RPC requests in the class itself.
- Usage is updated to `python node.py <id> <ip:port>`
- `raft_init.py` can be broken if so wish, but it makes the node 
files shorter, so let it be.
- I hope I have not made a mistake.
- As of now the implementation lacks the skill to handle
communication channels that become inaccessible (to simulate
dead nodes.)
- `raft_init.py` also contains the addresses of all the other
nodes in the system. That's the thing to update when 
moving to GCP.

Bruh. Writing readmes is hard if just before, you got rekt in gym.
