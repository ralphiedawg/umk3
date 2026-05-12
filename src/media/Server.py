import socket
import threading
import json
import time

from multiprocessing import Process, Queue

from src.gesture.Landmarker import Landmarker
from src.discovery.ServiceRegistry import ServiceRegistry
from src.media.recency_arbitration.RecencyArbiter import RecencyArbiter

def gesture_detection_worker(command_queue):
    landmarker = Landmarker()
    landmarker.open_cam(command_queue)

class Server():
    def __init__(self, addr:str = '0.0.0.0', port:int = 2022):
        self.addr = addr
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((addr, port))

        self.clients = {}
        self.active_client = {}
        self.next_client_id = 0
        self.id_lock = threading.Lock()

        self.listening = False
        self.listen_timestamp = 0
        self.listen_timeout = 5 

        self.command_queue = Queue()
        self.registry = None

        self.arbiter = RecencyArbiter()

    def on_new_client(self, clientsocket: socket.socket, client_id: int):
        while True:
            try:
                data = clientsocket.recv(1024)
                if not data:
                    print('Failed to Receive Data')
                
                heartbeat_str = data.decode().strip()
                self.parse_heartbeat(heartbeat_str)
                arbitration_res = self.arbiter.arbitrate(heartbeat_str)
                if arbitration_res != 0 and arbitration_res in self.clients:
                    self.active_client = self.clients[arbitration_res]
                    print(f'Active client set to id {arbitration_res}')
                print(heartbeat_str)
                
                resp = json.dumps(
                    {
                        'type':'acknowledgement',
                        'active': arbitration_res != 0
                    }
                ) + '\n'

                clientsocket.sendall(resp.encode())
            except TimeoutError:
                continue
            except json.JSONDecodeError:
                print(f'Recieved invalid json from client {client_id}')

    def parse_heartbeat(self, heartbeat):
        """Update client info from heartbeat"""
        beat = json.loads(heartbeat)
        try: 
            device_id = beat['device-id']
            ts = float(beat['timestamp'])
            device_type = beat['device-type']
            play_status = beat['play-status']

            if device_id in self.clients:
                self.clients[device_id]['timestamp'] = ts
                self.clients[device_id]['media_status'] = play_status
                self.clients[device_id]['type'] = device_type
                return device_id
        except KeyError:
            print('Key not found in heartbeat, ensure all data transferred properly')
        return -1

    def handshake(self):
        handshake = json.dumps({'umk': True})
        return handshake.encode('utf-8')

    def _socket_listener(self):
        while True:
            self.socket.listen()
            connection, addr = self.socket.accept()
            connection.sendall(self.handshake())
            try:
                resp = connection.recv(1024).decode()
                if not resp:
                    print(f'No response from {addr}, closing connection')
                    connection.close()
                    continue
                if int(resp) == 22:
                    with self.id_lock:
                        self.next_client_id += 1
                        client_id = self.next_client_id
                    
                    self.clients[client_id] = {
                        'addr': addr,
                        'socket': connection,
                        'id': client_id,
                        'timestamp': time.time(),
                        'media_status': 'not_playing',
                        'type': 'client'
                    }
                    connection.sendall(json.dumps({'type':'id_assignment', 'id': client_id}).encode())
                    print(f'Client with address {addr} assigned id {client_id}')
                    
                    thread = threading.Thread(target=self.on_new_client, args = (connection, client_id))
                    thread.start()
                else:
                    print(f'Invalid handshake response from {addr}: {resp}')
                    connection.close()
            except ValueError as e:
                print(f'Error parsing handshake response from {addr}: {e}')
                connection.close()
            except Exception as e:
                print(f'Error in handshake with {addr}: {e}')
                connection.close()


    def run_server(self):
        self.registry = ServiceRegistry(port=self.port)
        self.registry.register()
        
        threading.Thread(target=self._socket_listener, daemon=True).start()

        Process(target=gesture_detection_worker,args = (self.command_queue,), daemon=True).start()

        self.listening = False
        self.listen_timestamp = 0
        self.stabilizaiton_delay = .18

        while True:
            if self.listening and (time.time() - self.listen_timestamp >= self.listen_timeout):
                print('Window for listening expired')
                self.listening = False

            if not self.command_queue.empty():
                command = self.command_queue.get()

                if command == 'No command found' or not command:
                    continue

                if not self.listening:
                    if command == 'listen':
                        print('Wake detected, 5 second window activated...')
                        self.listening = True
                        self.listen_timestamp = time.time()
                        
                        while not self.command_queue.empty():
                            self.command_queue.get_nowait()
                else:
                    if command == 'listen':
                        self.listen_timestamp = time.time() # Refresh Timestamp
                        continue
                    if time.time() - self.listen_timestamp < self.stabilizaiton_delay:
                        # Wait for them to make a gesture
                        continue
                    if self.active_client:
                        try:
                            print(f"Sending command {command} to client {self.active_client['id']}")
                            self.active_client['socket'].sendall(
                                (json.dumps({'type': 'command', 'command': command}) + '\n').encode()
                            )
                        except Exception as e:
                            print(f"Failed to send command {command} to client {self.active_client['id']}: {e}")
                    else:
                        print(f"Command '{command}' detected, but no active client found.")

                    self.listening = False
                    print('Command executed, sleeping...')

                    while not self.command_queue.empty():
                        self.command_queue.get_nowait()

                time.sleep(0.05)

    def shutdown(self):
        print('\nShutting down server...')
        if self.registry:
            self.registry.unregister()
        self.socket.close()
        print('Server shutdown complete.')

if __name__ == "__main__":
    S1 = Server()
    S1.run_server()
