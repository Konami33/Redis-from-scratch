import socket
import threading

class TCPServer:
    def __init__(self, host='localhost', port=6379):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow port reuse
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)  # Backlog of 5 connections
        print(f"Server listening on {host}:{port}")
    
    def handle_client(self, conn, addr):
        print(f"Connected by {addr}")
        try:
            while True:
                data = conn.recv(1024).decode().strip()
                if not data:
                    break  # Client disconnected
                if data.upper() == "PING":
                    conn.send(b"+PONG\r\n")
                else:
                    conn.send(b"-ERR Unknown command\r\n")
        except Exception as e:
            conn.send(f"-ERR {str(e)}\r\n".encode())
        finally:
            conn.close()
            print(f"Disconnected: {addr}")
    
    def run(self):
        try:
            while True:
                conn, addr = self.server_socket.accept()
                # Start a new thread for each client
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = TCPServer()
    server.run()