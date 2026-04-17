import socket

host = socket.gethostname()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, 22022))

while True:
    msg = input('Message:')
    sock.sendall(msg.encode('utf-8'))
    response = sock.recv(1024).decode()
    print(f'Response: {response}')
    if response == 'break':
        print('server sent break code')
        sock.close()
        break

