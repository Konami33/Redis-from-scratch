import socket
import threading
import time
import sys
from typing import Dict, Optional, Any
from datetime import datetime, timedelta

class RedisServer:
    def __init__(self, host='localhost', port=6379):
        self.host = host
        self.port = port
        self.running = False
        self.socket = None
        
        # In-memory key-value store
        self.store: Dict[str, Any] = {}
        self.expiry_times: Dict[str, float] = {}
        
        # Server stats
        self.connected_clients = 0
        self.total_commands = 0
        
        # Start cleanup thread for expired keys
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_keys, daemon=True)
        self.cleanup_thread.start()
    
    def start(self):
        """Start the TCP server"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            
            print(f"Redis server starting on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.socket.accept()
                    print(f"New connection from {address}")
                    
                    # Handle each client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        print(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server"""
        self.running = False
        if self.socket:
            self.socket.close()
    
    def _handle_client(self, client_socket, address):
        """Handle individual client connection (Lab 1)"""
        self.connected_clients += 1
        buffer = ""
        
        try:
            client_socket.send(b"+OK Redis server ready\r\n")
            
            while self.running:
                try:
                    # Receive data from client
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    
                    buffer += data
                    
                    # Process complete commands (handle pipelining)
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        command_line = line.strip()
                        
                        if command_line:
                            response = self._process_command(command_line)
                            client_socket.send(response.encode('utf-8'))
                            
                except socket.timeout:
                    continue
                except socket.error:
                    break
                    
        except Exception as e:
            print(f"Client {address} error: {e}")
        finally:
            self.connected_clients -= 1
            client_socket.close()
            print(f"Client {address} disconnected")
    
    def _process_command(self, command_line: str) -> str:
        """Process Redis-style commands"""
        self.total_commands += 1
        
        # Parse command
        parts = command_line.split()
        if not parts:
            return "-ERR empty command\r\n"
        
        command = parts[0].upper()
        args = parts[1:]
        
        try:
            # Basic commands
            if command == "SET":
                return self._cmd_set(args)
            elif command == "GET":
                return self._cmd_get(args)
            elif command == "DEL":
                return self._cmd_del(args)
            
            # TTL commands
            elif command == "EXPIRE":
                return self._cmd_expire(args)
            elif command == "TTL":
                return self._cmd_ttl(args)
            elif command == "PTTL":
                return self._cmd_pttl(args)
            
            # Utility commands
            elif command == "PING":
                return "+PONG\r\n"
            elif command == "ECHO":
                return f"+{' '.join(args)}\r\n" if args else "+\r\n"
            elif command == "KEYS":
                return self._cmd_keys(args)
            elif command == "EXISTS":
                return self._cmd_exists(args)
            elif command == "TYPE":
                return self._cmd_type(args)
            elif command == "FLUSHALL":
                return self._cmd_flushall()
            elif command == "INFO":
                return self._cmd_info()
            else:
                return f"-ERR unknown command '{command}'\r\n"
                
        except Exception as e:
            return f"-ERR {str(e)}\r\n"
    
    def _is_expired(self, key: str) -> bool:
        """Check if a key has expired"""
        if key not in self.expiry_times:
            return False
        return time.time() > self.expiry_times[key]
    
    def _cleanup_expired_keys(self):
        """Background thread to clean up expired keys"""
        while True:
            try:
                current_time = time.time()
                expired_keys = [
                    key for key, expiry in self.expiry_times.items()
                    if current_time > expiry
                ]
                
                for key in expired_keys:
                    if key in self.store:
                        del self.store[key]
                    if key in self.expiry_times:
                        del self.expiry_times[key]
                
                time.sleep(1)  # Check every second
            except Exception as e:
                print(f"Cleanup thread error: {e}")
                time.sleep(1)
    
    # Command implementations
    def _cmd_set(self, args) -> str:
        """SET key value"""
        if len(args) < 2:
            return "-ERR wrong number of arguments for 'set' command\r\n"
        
        key, value = args[0], ' '.join(args[1:])
        self.store[key] = value
        
        # Remove any existing expiry
        if key in self.expiry_times:
            del self.expiry_times[key]
        
        return "+OK\r\n"
    
    def _cmd_get(self, args) -> str:
        """GET key"""
        if len(args) != 1:
            return "-ERR wrong number of arguments for 'get' command\r\n"
        
        key = args[0]
        
        # Check if key exists and hasn't expired
        if key not in self.store or self._is_expired(key):
            if self._is_expired(key):
                # Clean up expired key
                if key in self.store:
                    del self.store[key]
                if key in self.expiry_times:
                    del self.expiry_times[key]
            return "$-1\r\n"  # Redis null bulk string
        
        value = self.store[key]
        return f"${len(value)}\r\n{value}\r\n"
    
    def _cmd_del(self, args) -> str:
        """DEL key [key ...]"""
        if len(args) < 1:
            return "-ERR wrong number of arguments for 'del' command\r\n"
        
        deleted_count = 0
        for key in args:
            if key in self.store:
                del self.store[key]
                deleted_count += 1
            if key in self.expiry_times:
                del self.expiry_times[key]
        
        return f":{deleted_count}\r\n"
    
    def _cmd_expire(self, args) -> str:
        """EXPIRE key seconds"""
        if len(args) != 2:
            return "-ERR wrong number of arguments for 'expire' command\r\n"
        
        key, seconds_str = args
        
        try:
            seconds = int(seconds_str)
        except ValueError:
            return "-ERR value is not an integer or out of range\r\n"
        
        if key not in self.store or self._is_expired(key):
            return ":0\r\n"  # Key doesn't exist
        
        self.expiry_times[key] = time.time() + seconds
        return ":1\r\n"
    
    def _cmd_ttl(self, args) -> str:
        """TTL key (returns seconds)"""
        if len(args) != 1:
            return "-ERR wrong number of arguments for 'ttl' command\r\n"
        
        key = args[0]
        
        if key not in self.store or self._is_expired(key):
            return ":-2\r\n"  # Key doesn't exist
        
        if key not in self.expiry_times:
            return ":-1\r\n"  # Key exists but has no expiry
        
        remaining = int(self.expiry_times[key] - time.time())
        return f":{max(0, remaining)}\r\n"
    
    def _cmd_pttl(self, args) -> str:
        """PTTL key (returns milliseconds)"""
        if len(args) != 1:
            return "-ERR wrong number of arguments for 'pttl' command\r\n"
        
        key = args[0]
        
        if key not in self.store or self._is_expired(key):
            return ":-2\r\n"  # Key doesn't exist
        
        if key not in self.expiry_times:
            return ":-1\r\n"  # Key exists but has no expiry
        
        remaining_ms = int((self.expiry_times[key] - time.time()) * 1000)
        return f":{max(0, remaining_ms)}\r\n"
    
    def _cmd_keys(self, args) -> str:
        """KEYS pattern (simplified - returns all keys)"""
        # Clean up expired keys first
        current_keys = []
        for key in list(self.store.keys()):
            if not self._is_expired(key):
                current_keys.append(key)
        
        if not current_keys:
            return "*0\r\n"
        
        result = f"*{len(current_keys)}\r\n"
        for key in current_keys:
            result += f"${len(key)}\r\n{key}\r\n"
        
        return result
    
    def _cmd_exists(self, args) -> str:
        """EXISTS key [key ...]"""
        if len(args) < 1:
            return "-ERR wrong number of arguments for 'exists' command\r\n"
        
        count = 0
        for key in args:
            if key in self.store and not self._is_expired(key):
                count += 1
        
        return f":{count}\r\n"
    
    def _cmd_type(self, args) -> str:
        """TYPE key"""
        if len(args) != 1:
            return "-ERR wrong number of arguments for 'type' command\r\n"
        
        key = args[0]
        
        if key not in self.store or self._is_expired(key):
            return "+none\r\n"
        
        return "+string\r\n"  # For now, everything is a string
    
    def _cmd_flushall(self) -> str:
        """FLUSHALL - clear all data"""
        self.store.clear()
        self.expiry_times.clear()
        return "+OK\r\n"
    
    def _cmd_info(self) -> str:
        """INFO - server information"""
        uptime = int(time.time())  # Simplified
        info = f"""# Server
redis_version:1.0.0-custom
uptime_in_seconds:{uptime}
connected_clients:{self.connected_clients}
total_commands_processed:{self.total_commands}

# Memory
used_memory:{len(self.store)}

# Stats
total_connections_received:{self.total_commands}
keyspace_hits:0
keyspace_misses:0
"""
        return f"${len(info)}\r\n{info}\r\n"


def main():
    server = RedisServer()
    
    try:
        server.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.stop()


if __name__ == "__main__":
    main()