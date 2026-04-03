import socket

#if __name__ == "__main__":
import media_controls as controls
#else:
    #import src.media.media_controls as controls

class Controller:
    defaultAddr = '127.0.0.1'
    defaultPort = 2202
    deviceID = 0
    def __init__(self, addr:str=defaultAddr, port:int=defaultPort, deviceType:str='client'):
        self.addr = addr
        self.port = port
        self.deviceType = deviceType
        self.id = Controller.deviceID
        Controller.deviceID += 1

    def connect(self):
       self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.socket.connect((self.addr, self.port))

    def send_command(self, command: str):
        encoded = command.encode("utf-8")
        self.socket.sendall(encoded)
        response = self.socket.recv(1024)
        print(f'Response: {response.decode('utf-8')}')

    @staticmethod
    def recieve_command(recieved: bytes):
        decoded = recieved.decode('utf-8')
        status = controls.send_cmd(decoded)
        return status

if __name__ == "__main__":
    ctl = Controller()
    ctl.connect()
    while True:
        ctl.send_command(input("Command: "))
