import socket
from src.media.Controller import Controller

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
try: 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(10)
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(1024)
                    print(data.decode("utf-8"))
                    if not data:
                        print("data bad")
                        break
                    conn.sendall(data)
                    temp = Controller()
                    response = temp.recieve(data)
                    print(response)
                    conn.sendall(response.encode('utf-8'))
                except socket.timeout:
                    continue
except KeyboardInterrupt:
    print('Process Exited by User, shutting down')
    if not conn:
        exit()
    else:
        conn.close()
        exit()
