import socket
from src.media.Client import Client

class Server:
    def __init__(self, addr:str = '127.0.0.1', port:int = 2022):
        self.addr = addr
        self.port = port
    def run_server(self):
        try: 
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((self.addr, self.port))
                s.listen()
                conn, addr = s.accept()
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        try:
                            data = conn.recv(1024)
                            print(data.decode("utf-8"))
                            if not data:
                                print("Failed to Receive Data")
                                break
                            response = Client().recieve_command(data)
                            print(response)
                            conn.sendall(response.encode('utf-8'))
                        except socket.timeout:
                            continue
        except KeyboardInterrupt:
            print('Process Exited by User, shutting down')
            if not conn:
                exit()
            else:
                conn.close()
                exit()
