import socket 
PACKET_SIZE = 1024

def establish_connection(server_socket):
    MAX_RETRIES = 3
    RETRY_TIMEOUT = 2  # seconds

    retries = 0
    while retries < MAX_RETRIES:
        # Listen for incoming SYN packets
        data, client_address = server_socket.recvfrom(PACKET_SIZE)

        # Check for SYN packet
        if data.decode() == "SYN":
            # Send SYN-ACK packet if SYN received
            server_socket.sendto("SYN-ACK".encode(), client_address)

            # Listen for ACK packet from the client
            server_socket.settimeout(RETRY_TIMEOUT)
            try:
                data, client_address = server_socket.recvfrom(PACKET_SIZE)

                # Check if the received packet is an ACK packet
                if data.decode() == "ACK":
                    print("Connection established successfully.")
                    return True
            except socket.timeout:
                # Timeout occurred, retry
                print("Timeout occurred. Retrying...")
                retries += 1
                continue

    print("Connection establishment failed after {} retries.".format(MAX_RETRIES))
    return False

def check_received(server_socket):
    # Buffer to store received packets
    received_packets = [None] * 1000  # Assuming maximum 1000 packets
    terminate = False 
    while not terminate:
        # Receive packet from client
        packet, client_address = server_socket.recvfrom(PACKET_SIZE)


        #extract sequence number
        packet_data = packet.decode()
        if packet_data == "FIN":
            terminate = connection_termination(server_socket, client_address)
            continue
        seq_num = int(packet_data.split(':')[0])
        packet_data = packet_data.split(':')[1]

        # store packet in buffer
        received_packets[seq_num] = packet_data

        # send ACK
        ack = str(seq_num).encode()
        server_socket.sendto(ack, client_address)
        
        # Check if all previous packets have been received
        while received_packets[0]:
            # Print and remove the packet from the buffer
            print("Received packet:", received_packets.pop(0))
    server_socket.close()
    exit(0)


def connection_termination(server_socket, client_address):
    print("Received FIN packet from client.")
    RETRY_TIMEOUT = 20

    # Send ACK packet to the client
    server_socket.sendto("ACK".encode(), client_address)
    print("Sent ACK packet to client.")

    server_socket.sendto("FIN".encode(), client_address)
    print("Sent FIN packet to client.")


    while True : 
        # Listen for ACK packet from the server
        server_socket.settimeout(RETRY_TIMEOUT)
        try:
            data, server_address = server_socket.recvfrom(PACKET_SIZE)

            # Check for ACK packet
            if data.decode() == "ACK":
                print("Received ACK packet from client.")
                return True
            # duplicate FIN
            if data.decode() == "FIN":
                print("FIN duplicate")
                continue
        except socket.timeout:
            # Timeout occurred, retry
            print("Timeout waiting for ACK packet form Client. Retrying...")

    return False
    
    


def main(): 
    # Create a UDP socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
 
    # Bind the socket to a specific IP address and port 
    # Use an empty string for the IP address to listen on all available network interfaces
    local_ip = socket.gethostbyname(socket.gethostname())
    server_address = (local_ip, 5000) 
    server_socket.bind(server_address) 
 
    print('UDP server is running on {}:{}'.format(*server_address)) 
    connect = establish_connection(server_socket)
 
    if connect:
        check_received(server_socket)

    # Close the socket 
    server_socket.close() 
 
if __name__ == '__main__': 
    main() 