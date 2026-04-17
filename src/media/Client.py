import socket
import json
#import threading
#import Heartbeat
#if __name__ == "__main__":
import media_controls as controls
#else:
#import src.media.media_controls as controls
class Client:
    defaultAddr = '127.0.0.1'
    defaultPort = 2022
    def __init__(self, addr:str=defaultAddr, port:int=defaultPort, deviceType:str='client', mediaStatus = 'Not Playing'):
        self.addr = addr
        self.port = port
        self.deviceType = deviceType
        self.mediaStatus = mediaStatus

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
            if status != 'Not Playing' or 'Playing' or 'Paused' or 'Stopped': self.mediaStatus = status
            else:
                print("Invalid Status Input")
        else: 
            return self.mediaStatus

    def run(self):
        received = self.socket.recv(1024)
        return self.receive_command(received)

    """
    def beat_heart(self, server:str = '127.0.1', port:int = 2202):
        heart = Heartbeat.Heartbeat(self)
        beat = heart.heartbeat()
    """


if __name__ == "__main__":
    ctl = Client()
    ctl.connect()
