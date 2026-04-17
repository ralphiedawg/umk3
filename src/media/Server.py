import socket
import threading
import json

"""
if __name__ == "__main__":
    from Client import Client
else:
    from src.media.Client import Client
"""

class Server():
    def __init__(self, addr:str = '127.0.0.1', port:int = 2022):
        self.addr = addr
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.bind((addr, port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.clients = {}
        self.active_client = {}
        self.next_client_id = 0
        self.id_lock = threading.Lock()

    def on_new_client(self, clientsocket: socket.socket, addr):
        with self.id_lock:
            self.next_client_id += 1
            id = self.next_client_id

        self.clients[id] = {'addr': addr, 'socket': clientsocket}
        clientsocket.sendall(json.dumps({'type':'id_assignment', 'id': id}).encode())

        print(f'Client with address {addr} assigned id {id}')
        
        while True:
            try:
                data = clientsocket.recv(1024)
                if not data:
                    print('Failed to Receive Data')
                
                heartbeat_str = data.decode()
                active = self.parse_heartbeat(heartbeat_str) == True
                resp = json.dumps(
                    {
                        'type':'acknowledgement',
                        'active': active
                    }
                )

                clientsocket.sendall(resp.encode())
            except TimeoutError:
                continue
            except json.JSONDecodeError:
                print(f'Recieved invalid json from client {id}')

    """
        {
            "type": "heartbeat", 
            "device-id": 0, 
            "timestamp": "Thu Apr 16 14:26:38 2026", 
            "device-type": "client", 
            "playStatus": "Not Playing"
        }
    """
    def parse_heartbeat(self, heartbeat):
        """ Process Hearbeat and update server"""
        beat = json.loads(heartbeat)
        try: 
            device_id = beat['device-id']
            ts = float(beat['timestamp'])
            device_type = beat['device-type']
            play_status = beat['playStatus']

            if (not self.active_client) or (
                self.active_client['timestamp'] < ts and 
                play_status in ('playing') # Add back 'paused' if issues occur
            ): #Complex if statements > nested ones
                self.active_client['id'] = device_id
                self.active_client['timestamp'] = ts
                self.active_client['media_status'] = play_status
                self.active_client['type'] = device_type
                return device_id
        except KeyError:
            print('Key not found, ensure that all data transferred properly')
        return -1

    def run_server(self):
        while True:
            self.socket.listen()
            connection, addr = self.socket.accept()
            thread = threading.Thread(target=self.on_new_client, args = (connection, addr))
            thread.start()
if __name__ == "__main__":
    S1 = Server()
    S1.run_server()
