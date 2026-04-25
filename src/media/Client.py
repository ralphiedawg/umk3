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
        print('Searching for server, sleeping for 5 seconds')
        time.sleep(5)

        with open('known_services.json', 'r') as file:
            data = json.load(file)
            self.addr = data['addresses'][0]
            self.port = data['port']
            # TODO: CHeck all addreses to see if they work, use the first one that does? Ask client which they'd prefer?
            # Get host name from addr to select.

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
