import socket
import threading
import json
import time
import logging
import multiprocessing
from queue import Empty

from multiprocessing import Process, Queue

from src.gesture.Landmarker import Landmarker
from src.discovery.ServiceRegistry import ServiceRegistry
from src.media.recency_arbitration.RecencyArbiter import RecencyArbiter
from src.app_logging import configure_logging

logger = logging.getLogger(__name__)


def gesture_detection_worker(command_queue, stop_event):
    configure_logging()
    try:
        Landmarker().open_cam(command_queue, stop_event)
    except Exception:
        logger.exception("Gesture detection worker failed")
        raise

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
        self.stop_event = threading.Event()
        self.camera_stop_event = None
        self.gesture_process = None
        self.listener_thread = None
        self.client_sockets = set()
        self.client_sockets_lock = threading.Lock()
        self.shutdown_lock = threading.Lock()
        self.is_shutdown = False

        self.arbiter = RecencyArbiter()

    def on_new_client(self, clientsocket: socket.socket, client_id: int):
        print(f'New client incoming... socket: {clientsocket} with potential id {client_id}')
        while not self.stop_event.is_set():
            try:
                data = clientsocket.recv(1024)
                if not data:
                    print('Failed to Receive Data')
                    break
                
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
            except OSError:
                if not self.stop_event.is_set():
                    logger.exception("Client connection failed")
                break
            except json.JSONDecodeError:
                print(f'Recieved invalid json from client {client_id}')
        with self.client_sockets_lock:
            self.client_sockets.discard(clientsocket)
        clientsocket.close()

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
        self.socket.listen()
        self.socket.settimeout(0.5)
        while not self.stop_event.is_set():
            try:
                connection, addr = self.socket.accept()
            except socket.timeout:
                continue
            except OSError:
                if not self.stop_event.is_set():
                    logger.exception("Server socket failed")
                break

            with self.client_sockets_lock:
                self.client_sockets.add(connection)
            connection.settimeout(1)
            try:
                connection.sendall(self.handshake())
                resp = connection.recv(1024).decode()
                if not resp:
                    print(f'No response from {addr}, closing connection')
                    connection.close()
                    with self.client_sockets_lock:
                        self.client_sockets.discard(connection)
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
                    with self.client_sockets_lock:
                        self.client_sockets.discard(connection)
            except ValueError as e:
                print(f'Error parsing handshake response from {addr}: {e}')
                connection.close()
                with self.client_sockets_lock:
                    self.client_sockets.discard(connection)
            except Exception as e:
                if self.stop_event.is_set():
                    break
                print(f'Error in handshake with {addr}: {e}')
                connection.close()
                with self.client_sockets_lock:
                    self.client_sockets.discard(connection)


    def run_server(self):
        self.camera_stop_event = multiprocessing.Event()
        try:
            self.registry = ServiceRegistry(port=self.port)
            self.registry.register()

            self.listener_thread = threading.Thread(target=self._socket_listener, daemon=True)
            self.listener_thread.start()

            self.gesture_process = Process(
                target=gesture_detection_worker,
                args=(self.command_queue, self.camera_stop_event),
                daemon=True,
            )
            self.gesture_process.start()

            self.listening = False
            self.listen_timestamp = 0
            self.stabilizaiton_delay = .18

            while not self.stop_event.is_set():
                if not self.gesture_process.is_alive():
                    raise RuntimeError(
                        f"Gesture detection worker exited with code {self.gesture_process.exitcode}; "
                        "see ~/Library/Application Support/UMK/UMK.log"
                    )
                if self.listening and (time.time() - self.listen_timestamp >= self.listen_timeout):
                    print('Window for listening expired')
                    self.listening = False

                try:
                    command = self.command_queue.get(timeout=0.1)
                except Empty:
                    continue

                if command == 'No command found' or not command:
                    continue

                if not self.listening:
                    if command == 'listen':
                        print('Wake detected, 5 second window activated...')
                        self.listening = True
                        self.listen_timestamp = time.time()
                        while True:
                            try:
                                self.command_queue.get_nowait()
                            except Empty:
                                break
                else:
                    if command == 'listen':
                        self.listen_timestamp = time.time()
                        continue
                    if time.time() - self.listen_timestamp < self.stabilizaiton_delay:
                        continue
                    if self.active_client:
                        try:
                            print(f"Sending command {command} to client {self.active_client['id']}")
                            self.active_client['socket'].sendall(
                                (json.dumps({'type': 'command', 'command': command}) + '\n').encode()
                            )
                        except OSError:
                            logger.exception("Failed to send gesture command")
                    else:
                        print(f"Command '{command}' detected, but no active client found.")

                    self.listening = False
                    print('Command executed, sleeping...')
                    while True:
                        try:
                            self.command_queue.get_nowait()
                        except Empty:
                            break
        except Exception:
            logger.exception("Server failed")
        finally:
            self.shutdown()

    def shutdown(self):
        with self.shutdown_lock:
            if self.is_shutdown:
                return
            self.is_shutdown = True

        self.stop_event.set()
        if self.camera_stop_event is not None:
            self.camera_stop_event.set()

        if self.registry:
            try:
                self.registry.unregister()
            except Exception:
                logger.exception("Failed to unregister Bonjour service")
            self.registry = None

        try:
            self.socket.close()
        except OSError:
            logger.exception("Failed to close server socket")

        with self.client_sockets_lock:
            client_sockets = list(self.client_sockets)
            self.client_sockets.clear()
        for client_socket in client_sockets:
            try:
                client_socket.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            client_socket.close()

        if self.listener_thread and self.listener_thread is not threading.current_thread():
            self.listener_thread.join(timeout=2)

        if self.gesture_process and self.gesture_process.pid is not None:
            self.gesture_process.join(timeout=5)
            if self.gesture_process.is_alive():
                self.gesture_process.terminate()
                self.gesture_process.join(timeout=2)
            self.gesture_process.close()

        print('\nServer shutdown complete.')

if __name__ == "__main__":
    S1 = Server()
    S1.run_server()
