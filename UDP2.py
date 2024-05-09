import socket

HEADER = 1024
FORMAT = "utf-8"
HOST = socket.gethostbyname(socket.gethostname())
#HOST = "172.20.10.2"
PORT = 5000
ADDR = (HOST,PORT)
def send_request(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
        soc.connect(ADDR)
        soc.sendall(data.encode(FORMAT))
        data_rec = soc.recv(HEADER).decode(FORMAT)
while True:
    send_request("HII")
    for i in range(1000000):
        x = 0 