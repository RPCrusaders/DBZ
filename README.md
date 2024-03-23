# DBZ

Hey, I head your database is strong. Let me fight it!

## Usage
`python3 node.py --id <node id> --address <ip:port>`
  - You can invoke `python3 node.py --help` to see launch options.

## Developer Notes

### node.py
- contains code for _sending_ the required RPC requests. Clearly this will require multithreading.
- RPC requests to dead nodes can now be simulated without the system
falling apart thanks to try-catch.

### node_implementation.py
- contains the canonical Node class.
- inherits the correct gRPC class for handling RPC requests.
- contains code for _handling_ the event that an RPC request comes to the node. 
  - Depending on the contents of the request, the node's internal state should be 
  updated accordingly. 
  - This can be achieved using other methods in the node class
  if so needed.

### raft_init.py
- contains the addresses of all the other
nodes in the system. That's the thing to update when
moving to GCP.
- the functions here can be moved another file if so wish, but it makes the node
files shorter, so let it be.

![ultra instinct theme plays](dbz.gif)