import socket
import json
import threading
import time

from zeroconf import Zeroconf, ServiceBrowser

from Heartbeat import Heartbeat
#if __name__ == "__main__":
import media_controls as controls
#else:
#import src.media.media_controls as controls
from ..discovery.ServiceRegistry import Listener

class Client:
    defaultAddr = '127.0.0.1'
    defaultPort = 2022
    def __init__(self, addr:str=defaultAddr, port:int=defaultPort, deviceType:str='client', mediaStatus = 'not_playing'):
        self.addr = addr
        self.port = port
        self.deviceType = deviceType
        self.mediaStatus = mediaStatus

        listener = Listener()
        zc = Zeroconf()
        _ = ServiceBrowser(zc, '_umk._tcp.local.', listener) # Not static so we need some way to call it
        print('Searching for servers, sleeping for 5 seconds')
        time.sleep(5)
        chosen_server = self.test_servers()
        self.addr = chosen_server[0]
        self.port = chosen_server[1]


    def test_servers(self) -> tuple[str, int]:
        server = ('', 0)
        valid_servers = []
        with open('known_services.json', 'r') as file:
            data = json.load(file)
            shake_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            shake_socket.settimeout(2)
            # send UMK handshake, otherwise don't include in list
            try:
                for i in range(len(data['addresses'])):
                    try:
                        shake_socket.connect((data['addresses'][i], data['port']))
                        try:
                            handshake = json.loads(shake_socket.recv(1024).decode())
                            if handshake['umk'] == 'True':
                                shake_socket.send('22'.encode())
                                valid_servers.append((data['addresses'][i], data['port']))
                            else:
                                print('Address is not a UMK server, moving on')
                        except json.JSONDecodeError or KeyError:
                            print('Either not UMK server or incomplete data')
                        shake_socket.close()
                    except ConnectionError:
                        print('Server unreachable, moving on')
            finally:
                shake_socket.close()

        if len(valid_servers) > 1:
            print('Multiple Valid Servers found, please select from list')
            for s in range(len(valid_servers)):
                ip = valid_servers[s][0]
                hostname = socket.gethostbyaddr(ip)
                port = valid_servers[s][1]
                print(f'{s}: {hostname} with port {port} (IP :{ip})')
            choice = int(input('Index: '))
            server = valid_servers[choice]
        else:
            server = valid_servers[0]

        return server
        

    def connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.addr, self.port))
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

    # 2-in-1 getter setter to enforce status rules
    def playStatus(self, status:str = ''):
        if status != '':
            if status not in ('not_playing','playing','paused','stopped'): self.mediaStatus = status
            else:
                print("Invalid Status Input")
        else: 
            return self.mediaStatus

    def beat_heart(self):
        h = Heartbeat(self)
        while True:
            heartbeat_string = h.heartbeat()
            self.socket.sendall(heartbeat_string.encode())
            time.sleep(10)
    def listen_for_command(self):
        while True:
            received = self.socket.recv(1024)
            jsonStr = json.loads(received.decode())
            if jsonStr.get('type') == 'command':
                command = jsonStr['command']
                self.receive_command(command.encode())

    def run(self):
        threading.Thread(target=self.listen_for_command, daemon=False).start()
        threading.Thread(target=self.beat_heart, daemon=False).start()
        

if __name__ == "__main__":
    ctl = Client()
    ctl.connect()
    ctl.run()
