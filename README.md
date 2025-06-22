# Build Redis from Scratch 

#### **Phase 1: Core System Foundation**
Focus on building the foundational components of a Redis-like system: a TCP server and an in-memory key-value store.

##### **Lab 1: TCP Server Basics**
- **Objective**: Learn socket programming and build a simple TCP server to handle client connections.
- **Learning Goals**:
  - Understand Python’s `socket` module for client-server communication.
  - Learn how to handle a single client connection and process commands.
  - Explore basic I/O handling without advanced multiplexing (`select` or `epoll`).
- **Study**:
  - Basics of TCP: How connections are established (3-way handshake).
  - Python’s `socket` module: `bind`, `listen`, `accept`, `send`, `recv`.
  - Redis’s client-server model: One server, multiple clients.
- **Tools**:
  - Python’s `socket` module.
  - `telnet` or `netcat` (e.g., `nc localhost 6379`) to test connections.
  - `netstat -tuln` to verify the server is listening.
- **Task**:
  - Build a TCP server that accepts a single client connection, receives text commands (e.g., `PING`), and responds with `PONG`.
  - Test the server using `telnet localhost 6379`.

- **Milestone**: A TCP server that responds to `PING` with `PONG` when tested with `telnet`.

##### **Lab 2: In-Memory Key-Value Store**
- **Objective**: Build a simple in-memory key-value store to manage data.
- **Learning Goals**:
  - Understand Python dictionaries as the core data structure for a key-value store.
  - Learn basic CRUD operations (create, read, update, delete).
  - Explore memory usage basics without advanced tools like `valgrind`.
- **Study**:
  - Python dictionary internals: Hash tables, key hashing.
  - Redis’s string data type: Key-value pairs stored in memory.
  - Memory management: How Python allocates memory for dictionaries.
- **Tools**:
  - Python’s built-in `sys.getsizeof()` to measure dictionary memory usage.
  - `pytest` for unit testing.
- **Task**:
  - Create a `DataStore` class with methods for `set`, `get`, and `delete`.
  - Test the class with a script that stores 1,000 key-value pairs and measures memory usage.
- **Milestone**: A `DataStore` class that supports `SET`, `GET`, and `DEL` operations for 1,000 keys with basic memory usage reporting.

#### **Phase 2: Protocol & Persistence**
Implement the Redis Serialization Protocol (RESP) and add persistence to save data to disk.

##### **Lab 3: RESP Protocol Parser**
- **Objective**: Implement a parser for Redis’s RESP protocol to handle client commands.
- **Learning Goals**:
  - Understand RESP: Arrays, bulk strings, simple strings, and errors.
  - Learn to parse and serialize data for client-server communication.
  - Explore protocol design trade-offs (text-based vs. binary).
- **Study**:
  - Redis Protocol Specification: [redis.io/topics/protocol](https://redis.io/topics/protocol).
  - How Redis clients send commands (e.g., `*3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n`).
  - Text-based protocols: Simplicity vs. parsing overhead.
- **Tools**:
  - Python’s `bytes` and `str` for handling raw socket data.
  - Wireshark (optional) to inspect Redis traffic (`tcp.port == 6379`).
- **Task**:
  - Write a `Protocol` class to parse RESP arrays and bulk strings for `SET`, `GET`, and `DEL` commands.
  - Test the parser with sample RESP inputs and verify correct command extraction.

- **Milestone**: A `Protocol` class that correctly parses `SET`, `GET`, and `DEL` commands and serializes responses.

##### **Lab 4: Basic Persistence**
- **Objective**: Add persistence to save the key-value store to disk.
- **Learning Goals**:
  - Understand Redis’s persistence: RDB (snapshot) vs. AOF (append-only file).
  - Learn basic file I/O in Python for saving and loading data.
  - Explore trade-offs between snapshot frequency and data loss.
- **Study**:
  - Redis RDB: Periodic snapshots of the entire dataset.
  - Redis AOF: Logging every write operation for durability.
  - Python’s `json` module for simple serialization.
- **Tools**:
  - Python’s `json` module for file storage.
  - `ls -lh` to check file size.
  - `time` command to measure save/load performance.
- **Task**:
  - Implement a `Persistence` class to save the data store to a JSON file and load it on startup.
  - Test by saving 1,000 keys, restarting the program, and verifying data is restored.


- **Milestone**: A `Persistence` class that saves and loads the data store, surviving program restarts.

---

#### **Phase 3: Integrate Components**
Combine the TCP server, data store, RESP parser, and persistence into a functional Redis-like system.

##### **Lab 5: Redis-like Server Integration**
- **Objective**: Build a Redis-like server that handles client commands and persists data.
- **Learning Goals**:
  - Integrate all components: TCP server, data store, RESP parser, and persistence.
  - Learn basic concurrency to handle multiple clients using threading.
  - Understand command execution flow: Parse → Execute → Respond.
- **Study**:
  - Redis’s command processing: Single-threaded event loop.
  - Python’s `threading` module for handling multiple clients.
  - Error handling: Invalid commands, connection drops.
- **Tools**:
  - Python’s `threading` module.
  - `redis-py` (Redis client) to test compatibility.
  - `pytest` for integration tests.
- **Task**:
  - Combine components into a `Server` class that:
    - Listens for client connections.
    - Parses RESP commands.
    - Executes commands on the data store.
    - Persists data on shutdown.
  - Test with multiple clients sending `SET`, `GET`, and `DEL` commands.


- **Milestone**: A Redis-like server that handles multiple clients, processes `SET`, `GET`, `DEL`, and `SAVE` commands, and persists data.

---

#### **Phase 4: Advanced Data Structures**
Extend the system to support Redis’s advanced data types.

##### **Lab 6: Lists and Sets**
- **Objective**: Add support for Redis’s list and set data types.
- **Learning Goals**:
  - Understand Redis’s data structures: Lists (linked lists), Sets (hash tables).
  - Learn to enforce type safety in the data store.
  - Explore memory-efficient storage for small datasets.
- **Study**:
  - Redis lists: `LPUSH`, `RPUSH`, `LPOP`, `RPOP`.
  - Redis sets: `SADD`, `SMEMBERS`, `SREM`.
  - Redis’s ziplist optimization (optional reading).
- **Tools**:
  - Python’s `list` and `set` for implementation.
  - `memory_profiler` to measure memory usage.
- **Task**:
  - Extend `DataStore` to support lists and sets with commands like `LPUSH`, `SADD`.
  - Test with 100 operations on lists and sets, ensuring type safety (e.g., no `GET` on a list).
- **Milestone**: The server supports `LPUSH`, `RPOP`, `SADD`, and `SMEMBERS` commands with type checking.

---

#### **Phase 5: Concurrency & Performance**
Improve the server’s ability to handle multiple clients efficiently.

##### **Lab 7: Concurrent Client Handling**
- **Objective**: Optimize the server for multiple concurrent clients.
- **Learning Goals**:
  - Understand Python’s Global Interpreter Lock (GIL) and its impact.
  - Learn `asyncio` as an alternative to threading for I/O-bound tasks.
  - Explore basic performance profiling.
- **Study**:
  - Python’s `asyncio`: Event loops, coroutines.
  - Redis’s single-threaded event loop vs. Python’s threading.
  - Basic profiling: Measure latency and throughput.
- **Tools**:
  - Python’s `asyncio` module.
  - `time.perf_counter()` for latency measurement.
  - `locust` or `ab` (Apache Benchmark) for load testing.
- **Task**:
  - Rewrite the server using `asyncio` to handle 100 concurrent clients.
  - Measure average latency for `GET` commands under load.
- **Milestone**: The server handles 100 concurrent clients with <10ms latency for `GET` commands.

---

#### **Phase 6: Production-Grade Features**
Add advanced Redis features like replication and observability.

##### **Lab 8: Basic Replication**
- **Objective**: Implement simple master-slave replication.
- **Learning Goals**:
  - Understand Redis’s replication: Master sends commands to slaves.
  - Learn basic distributed systems concepts (CAP theorem briefly).
  - Explore network communication for replication.
- **Study**:
  - Redis replication: `SYNC` command, command propagation.
  - Challenges: Network partitions, partial resync.
- **Tools**:
  - Python’s `socket` for master-slave communication.
  - `tcpdump` (optional) to inspect replication traffic.
- **Task**:
  - Extend the server to support a slave that mirrors the master’s data store.
  - Test by sending commands to the master and verifying they appear on the slave.
- **Milestone**: A master-slave setup where the slave mirrors the master’s data.