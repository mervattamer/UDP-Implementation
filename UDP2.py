import socket
import time
HEADER = 1024
FORMAT = "utf-8"

def establish_connection(client_socket, HOST, PORT):
    MAX_RETRIES = 3
    RETRY_TIMEOUT = 2  # seconds

    retries = 0
    while retries < MAX_RETRIES:
        # Send SYN packet to the server
        client_socket.sendto("SYN".encode(), (HOST, PORT))
        print("Sent SYN packet to the server.")

        # Listen for SYN-ACK packet from the server
        client_socket.settimeout(RETRY_TIMEOUT)
        try:
            data, server_address = client_socket.recvfrom(1024)

            # Check for SYN-ACK packet
            if data.decode() == "SYN-ACK":
                # Send ACK packet to the server
                client_socket.sendto("ACK".encode(), server_address)
                print("Connection established successfully.")
                return True
        except socket.timeout:
            # Timeout occurred, retry
            print("Timeout occurred. Retrying...")
            retries += 1
            continue

    print("Connection establishment failed after {} retries.".format(MAX_RETRIES))
    return False


def main():
    PORT = 5000
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    local_ip = socket.gethostbyname(socket.gethostname())
    server_address = (local_ip, PORT)
    while True:
        connect = establish_connection(client_socket, local_ip, PORT)
        send_request("HII")
        time.sleep(1)


ADDR = (HOST,PORT)
def send_request(data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as soc:
        soc.connect(ADDR)
        soc.sendall(data.encode(FORMAT))
        data_rec = soc.recv(HEADER).decode(FORMAT)

        # Process the response
        print('Received response from server:',data_rec)

        # Send ACK to server
        soc.sendall(b'ACK')
