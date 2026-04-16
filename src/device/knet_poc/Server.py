#!/usr/bin/python           # This is server.py file                                                                                                                                                                           

import socket               # Import socket module
import threading

def on_new_client(clientsocket,addr):
    while True:
        msg = clientsocket.recv(1024)
        if msg == 'close':
            break
        print(addr, ' >> ', msg)
        msg = input('SERVER >> ').encode()
        clientsocket.send(msg)
    clientsocket.close()

s = socket.socket()         
host = socket.gethostname() 
port = 22022                

print('Waiting for clients...')

s.bind((host, port))       
print(f'Server started! on port {port}')
s.listen(5)                 

while True:
    c, addr = s.accept()     # Establish connection with client.
    t = threading.Thread(target=on_new_client, args = (c,addr))
    t.start()
