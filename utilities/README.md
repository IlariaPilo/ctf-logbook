# Utilities
This folder contains some useful Python scripts, as well as a collection of interesting tools.

## Python scripts

- [`connect`](./connect.py) : Connects to a TCP server and automatically replies to it. Requires implementing the correct response logic (e.g., if the server sends a string and expects it backwards, this behavior must be manually implemented before running the script).
- [`server_302`](./server_302.py) : Creates a dumb Python server redirecting every request it receives.
