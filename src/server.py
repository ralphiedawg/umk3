import socket
from src.media.Controller import Controller

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 2202  # Port to listen on (non-privileged ports are > 1023)
try: 
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                try:
                    data = conn.recv(1024)
                    print(data.decode("utf-8"))
                    if not data:
                        print("Failed to Receive Data")
                        break
                    temp = Controller()
                    response = temp.recieve_command(data)
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
