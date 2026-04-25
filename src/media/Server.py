import socket
import threading
import json
import time

if __name__ == "__main__":
         import multiprocessing
         multiprocessing.set_start_method('spawn', force=True)

from multiprocessing import Process, Queue

from ..gesture.Landmarker import Landmarker
from ..discovery.ServiceRegistry import ServiceRegistry

def gesture_detection_worker(command_queue):
         landmarker = Landmarker()
         landmarker.open_cam(command_queue)

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

        self.listening = False
        self.listen_timestamp = 0
        self.listen_timeout = 5 

        self.command_queue = Queue()

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
                print(heartbeat_str)
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
            "playStatus": "not_playing"
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
                play_status == 'playing' 
            ): 
                self.active_client['id'] = device_id
                self.active_client['timestamp'] = ts
                self.active_client['media_status'] = play_status
                self.active_client['type'] = device_type
                self.active_client['socket'] = self.clients[device_id]['socket']
                return device_id
        except KeyError:
            print('Key not found, ensure that all data transferred properly')
        return -1

    def handshake(self):
        handshake = json.dumps({'umk': 'True'})
        return handshake.encode('utf-8')

    def _socket_listener(self):
        while True:
            self.socket.listen()
            connection, addr = self.socket.accept()
            connection.sendall(self.handshake())
            resp = connection.recv(1024).decode()
            if int(resp) == 22: # 22 cause we still gotta make sure that it's def a umk client idc if redundant, custom OK code just to make sure
                print('Client verified, beginning server loop w/ client')
                thread = threading.Thread(target=self.on_new_client, args = (connection, addr))
                thread.start()
            else:
                print('Unable to verify whether client is an UMK client, exiting')


    def run_server(self):
        registry = ServiceRegistry()
        registry.register()
        
        threading.Thread(target=self._socket_listener, daemon=True).start()

        Process(target=gesture_detection_worker,args = (self.command_queue,), daemon=True).start()

        while True:
            if not self.command_queue.empty():
                command = self.command_queue.get()

                if command == 'listen':
                    self.listen_timestamp = time.time()

                self.listening = time.time() - self.listen_timestamp <= self.listen_timeout

                if (self.active_client and self.listening):
                    self.listening = False
                    try:
                        self.active_client['socket'].sendall(json.dumps({'type': 'command', 'command': command}).encode())
                    except:
                        print(f"Failed to send command to client {self.active_client['id']}")
            time.sleep(0.1)

if __name__ == "__main__":
    S1 = Server()
    S1.run_server()
