import socket 
 
def main(): 
    # Create a UDP socket 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
 
    # ipconfig getifaddr en0
    # Bind the socket to a specific IP address and port 
    #server_address = ('192.168.1.7', 5000)  # Use an empty string for the IP address to listen on all available network interfaces
    local_ip = socket.gethostbyname(socket.gethostname())
    server_address = (local_ip, 5000) 
    server_socket.bind(server_address) 
 
    print('UDP server is running on {}:{}'.format(*server_address)) 
 
    while True: 
        # Receive data from a client 
        data, client_address = server_socket.recvfrom(1024)  # Buffer size is 1024 bytes 
 
        # Process the received data 
        print('Received data from {}: {}'.format(client_address, data.decode())) 
 
        # Send a response back to the client 
        response = 'Hello, client!' 
        server_socket.sendto(response.encode(), client_address) 
 
    # Close the socket 
    server_socket.close() 
 
if __name__ == '__main__': 
    main() 