import socket
from src.media.Controller import Controller

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(1024)
            print(data.decode("utf-8"))
            if not data:
                print("data bad")
                break
            conn.sendall(data)
            temp = Controller()
            temp.recieve(data)
