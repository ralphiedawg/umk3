import socket
import json
import threading
import time

from zeroconf import Zeroconf, ServiceBrowser

from src.media.Heartbeat import Heartbeat
from src.media import media_controls as controls
from src.media.recency_arbitration.WrapperHelper import WrapperHelper
from src.discovery.ServiceRegistry import Listener

class Client:
    defaultAddr = '127.0.0.1'
    defaultPort = 2022
    def __init__(self, addr:str=defaultAddr, port:int=defaultPort, deviceType:str='client', mediaStatus = 'not_playing'):
        self.addr = addr
        self.port = port
        self.deviceType = deviceType
        self.mediaStatus = mediaStatus
        self.killswitch = False
        self._stop_event = threading.Event()

        if self.addr == self.defaultAddr:
            listener = Listener()
            zc = Zeroconf()
            browser = ServiceBrowser(zc, '_umk._tcp.local.', listener)
            print('Searching for servers for 5 seconds')
            try:
                time.sleep(5)
                discovered = listener.get_services()
            finally:
                browser.cancel()
                zc.close()
            candidates = [
                (address, service['port'])
                for service in discovered
                for address in service['addresses']
            ]
            chosen_server = self.test_servers(candidates)
            self.addr = chosen_server[0]
            self.port = chosen_server[1]
        
        self.connect()


    def test_servers(self, candidates: list[tuple[str, int]]) -> tuple[str, int]:
        for address, port in candidates:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as test_socket:
                test_socket.settimeout(2)
                try:
                    if test_socket.connect_ex((address, port)) == 0:
                        print(f"Server at {address}:{port} is reachable")
                        return address, port
                except OSError as error:
                    print(f"Error testing server at {address}:{port}: {error}")

        raise ConnectionError(
            "No reachable UMK server was found on the local network. "
            "Start a server and verify both devices are on the same LAN."
        )
        

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.addr, self.port))
        
        # Receive and respond to handshake
        handshake = json.loads(self.socket.recv(1024).decode())
        if handshake.get('umk') == True:
            self.socket.send('22'.encode())
        
        # Receive ID assignment
        id_assignment = self.socket.recv(1024).decode()
        id_data = json.loads(id_assignment)
        self.id = id_data['id']


    def send_comm(self, communication):
        encoded = communication.encode('utf-8')
        self.socket.sendall(encoded)
        response = self.socket.recv(1024)
        print(f'Response: {response.decode('utf-8')}')

    def send_command(self, command: str):
        self.send_comm(communication=command)

    @staticmethod
    def receive_command(received: bytes):
        decoded = received.decode('utf-8')
        status = controls.send_cmd(decoded)
        return status

    def play_status(self):
        if WrapperHelper.agnostic_media_status():
            return 'playing'
        return 'not_playing'

    def beat_heart(self):
        h = Heartbeat(self)
        while not self._stop_event.is_set():
            try:
                if not self.killswitch:
                    heartbeat_string = h.heartbeat()
                    self.socket.sendall(heartbeat_string.encode())
                    if self._stop_event.wait(timeout=10):
                        break
                else:
                    if self._stop_event.wait(timeout=1):
                        break
            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"Error sending heartbeat: {e}")
                break

    def listen_for_command(self):
        self.socket.settimeout(1)
        buffer = ""
        while not self._stop_event.is_set():
            try:
                received = self.socket.recv(1024)
                if not received:
                    break
                buffer += received.decode()
                
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line:
                        jsonStr = json.loads(line)
                        if jsonStr.get('type') == 'command':
                            command = jsonStr['command']
                            if self.killswitch:
                                print(f"Killswitch active: dropping command '{command}'")
                            else:
                                self.receive_command(command.encode())
            except socket.timeout:
                continue
            except Exception as e:
                if not self._stop_event.is_set():
                    print(f"Error listening for command: {e}")
                break

    def shutdown(self):
        print("Shutting down client")
        self._stop_event.set()

        if hasattr(self, 'socket') and self.socket:
            try:
                self.socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.socket.close()
            except Exception:
                pass

        print("Client shutdown successful")
        

    def run(self):
        self.command_thread = threading.Thread(target=self.listen_for_command, daemon=True)
        self.heart_thread = threading.Thread(target=self.beat_heart, daemon=True)
        self.command_thread.start()
        self.heart_thread.start()
        

if __name__ == "__main__":
    ctl = Client()
    ctl.connect()
    ctl.run()
