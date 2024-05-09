import socket
import time
from pynput import keyboard
PACKET_SIZE = 1024
FORMAT = "utf-8"
TERMINATE = False
# do we have to set timeout = the expected RTT??


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
            data, server_address = client_socket.recvfrom(PACKET_SIZE)

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

def send_data(client_socket, data, server_address):
    WINDOW_SIZE = 5
    TIMEOUT = 5 

    # divide data to segments
    segments = [data[i:i+PACKET_SIZE] for i in range(0, len(data), PACKET_SIZE)]

    # sliding window
    base = 0
    next_seq_num = 0

    # hal el seq number howa 3adad el packets wala 3adad

    while base < len(segments):
        
        # send packets within the window
        for seq_num in range(base, min(base + WINDOW_SIZE, len(segments))):
            packet = segments[seq_num].encode()
            packet_data = f"{seq_num}:{packet}"
            client_socket.sendto(packet_data.encode(), server_address)
            print("sent packet:", packet)

        # check ACKs
        for i in range(base, min(base + WINDOW_SIZE, len(segments))):
            client_socket.settimeout(TIMEOUT)

            try:
                ack, _ = client_socket.recvfrom(PACKET_SIZE)
                if ack.decode() == str(i): #if ack received increment seq num to be the 
                    next_seq_num = max(next_seq_num, i + 1)
            except socket.timeout:
                ack = None  

        # move the window
        base = next_seq_num

def Esc(key):
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k == "z":  # keys of interest
        connection_termination()
        return False

def connection_termination():
    MAX_RETRIES = 3
    RETRY_TIMEOUT = 2  # seconds

    retries = 0
    while retries < MAX_RETRIES:
        # Send FIN packet to the server
        client_socket.sendto("FIN".encode(), server_address)
        print("Sent FIN packet to terminate connection.")

        # Listen for ACK packet from the server
        client_socket.settimeout(RETRY_TIMEOUT)
        try:
            data, server_address = client_socket.recvfrom(PACKET_SIZE)

            # Check for ACK packet
            if data.decode() == "ACK":
                # Listen for ACK packet from the server
                client_socket.settimeout(RETRY_TIMEOUT)
                try:
                    # Listen for FIN packet from the server
                    data, server_address = client_socket.recvfrom(PACKET_SIZE)

                    # Check for FIN packet
                    if data.decode() == "FIN":
                        client_socket.sendto("ACK".encode(), server_address)
                        print("Connection terminated successfully.")
                        TERMINATE = True
                except socket.timeout:
                    # Timeout occurred, retry
                    print("Timeout waiting for FIN packet form Server. Retrying...")
                    retries += 1
                    continue

        except socket.timeout:
            # Timeout occurred, retry
            print("Timeout waiting for ACK packet form Server. Retrying...")
            retries += 1
            continue

    print("Connection termination failed after {} retries.".format(MAX_RETRIES))
    return

PORT = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host_ip = socket.gethostbyname(socket.gethostname())
server_address = (host_ip, PORT)
connect = establish_connection(client_socket, host_ip, PORT)
# listener = keyboard.Listener(on_press=Esc)
# listener.start()  # start to listen on a separate thread
# listener.join()  # remove if main thread is polling self.keys

def main():
    # PORT = 5000
    # client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # host_ip = socket.gethostbyname(socket.gethostname())
    # server_address = (host_ip, PORT)
    # connect = establish_connection(client_socket, host_ip, PORT)
    # listener = keyboard.Listener(on_press=connection_termination)
    # listener.start()  # start to listen on a separate thread
    # listener.join()  # remove if main thread is polling self.keys
    while not TERMINATE:

        if connect:
            data = "Hello, server!"
            server_address = (host_ip, PORT)
            send_data(client_socket, data ,server_address)
        time.sleep(1)
        if input() == 'c':
            continue
        else :
            connection_termination()


            

if __name__ == '__main__':
    main()


    