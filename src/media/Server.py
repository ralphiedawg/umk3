import socket
import threading
import sys

if __name__ == "__main__":
    from Client import Client
else:
    from src.media.Client import Client

class Server():
    def __init__(self, addr:str = '127.0.0.1', port:int = 2022):
        self.addr = addr
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((addr, port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}
        self.active_client_index = 0

    """
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
    """

    def on_new_client(self, clientsocket: socket.socket, addr):
        raw = clientsocket.recv(1024)
        id = int.from_bytes(raw, byteorder='big')
        self.clients[id] = addr

        print(f'Client with address {addr} assigned id {id}')
        
        while True:
            try:
                data = clientsocket.recv(1024)
                print(f'Incoming Comm from id {id}: {data.decode('utf-8')}')
                if not data:
                    print("Failed to Recieve Data")
                    break
                if data.decode('utf-8') == 'break' or data == 'close':
                    print('Break recieved.')
                    break
                else:
                    resp = Client().receive_command(data)
                print(resp)
                clientsocket.sendall(resp.encode('utf-8'))
            except TimeoutError:
                continue
        sys.exit()

    def run_server(self):
        while True:
            self.socket.listen()
            connection, addr = self.socket.accept()
            thread = threading.Thread(target=self.on_new_client, args = (connection, addr))
            thread.start()
if __name__ == "__main__":
    S1 = Server()
    S1.run_server()
