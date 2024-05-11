import time
import socket
class server:
    def __init__(self,PACKET_SIZE = 100,FORMAT = "utf-8",PORT = 5000):
        self.seq_num = 10
        self.ack_num = 0
        self.PACKET_SIZE = PACKET_SIZE
        self.FORMAT = FORMAT
        self.PORT = PORT
        self.IP = socket.gethostbyname(socket.gethostname())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        server_address = (self.IP,self.PORT)
        self.server_socket.bind(server_address) 
        print('UDP server is running on {}:{}'.format(*server_address))
        
        if self.establish_connection():
            self.check_received()
    def establish_connection(self):
        MAX_RETRIES = 3
        RETRY_TIMEOUT = 2  # seconds

        retries = 0
        PACKET_SIZE = self.PACKET_SIZE
        while retries < MAX_RETRIES:
            # Listen for incoming SYN packets
            data, client_address = self.server_socket.recvfrom(PACKET_SIZE)
            data = data.decode()
            # f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
            seq_num = int(data.split(":")[0])
            packet = data.split(":")[2]
            received_checksum = int(data.split(":")[3])
            calculated_checksum = udp_checksum(seq_num,0,0,packet)

            # Check for SYN packet
            if packet == "SYN" and received_checksum == calculated_checksum:
                # Send SYN-ACK packet if SYN received
                ack_num = seq_num+len(packet)
                seq_num = self.seq_num
                data = "SYN-ACK"
                checksum = udp_checksum(seq_num,ack_num,0,data)

                packet = f"{seq_num}:{ack_num}:{data}:{checksum}:{0}"
                self.server_socket.sendto(packet.encode(), client_address)

                # Listen for ACK packet from the client
                self.server_socket.settimeout(RETRY_TIMEOUT)
                try:
                    r_data, client_address = self.server_socket.recvfrom(PACKET_SIZE)
                    r_data = r_data.decode()
                    ack_num = int(r_data.split(":")[1])
                    r_seq_num = int(r_data.split(":")[0])
                    packet = r_data.split(":")[2]
                    received_checksum = int(r_data.split(":")[3])
                    calculated_checksum = udp_checksum(r_seq_num,ack_num,0,packet)
                    # Check if the received packet is an ACK packet
                    if packet == "ACK" and ack_num == seq_num+len(data) and calculated_checksum == received_checksum:
                        # da el haneshta8al beeh ba3d keda
                        self.seq_num = ack_num
                        self.ack_num = r_seq_num+len("ACK")
                        print("Connection established successfully.")
                        print(self.seq_num,self.ack_num)
                        return True
                except socket.timeout:
                    # Timeout occurred, retry
                    print("Timeout occurred. Retrying...")
                    retries += 1
                    continue
            else :
                print("Error in the message")

        print("Connection establishment failed after {} retries.".format(MAX_RETRIES))
        return False
    def check_received(self):

        # f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
        PACKET_SIZE = self.PACKET_SIZE
        RETRY_TIMEOUT = 10
        data, client_address = self.server_socket.recvfrom(PACKET_SIZE)
        data = data.decode()
        seq_num = int(data.split(":")[0])
        ack_num = int(data.split(":")[1])
        request = data.split(':')[2]
        received_checksum = int(data.split(':')[3])
        calc_checksum = udp_checksum(seq_num,ack_num,0,request)
        if calc_checksum == received_checksum and request == "FIN":
            self.seq_num = ack_num
            self.ack_num = seq_num+len("FIN")
            self.connection_termination()
        else:
            # check if data is corrupted here and send neg ack
            if calc_checksum == received_checksum:
                if request.split()[0] == "GET":
                    path = request.split()[1]
                    self.seq_num = ack_num
                    self.ack_num = seq_num+len(request)
                    # to resend if negative ack
                    while True:
                        if path == "/path/to/resource": 
                            data = "HTTP/1.1 200 OK\r\nSuccessful GET Request"
                            checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                            packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                            self.server_socket.sendto(packet.encode(), client_address)
                        else :
                            data = "HTTP/1.1 404 Not Found\r\nPath Not Found"
                            checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                            packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                            self.server_socket.sendto(packet.encode(), client_address)
                            # Listen for ACK packet from the client
                        self.server_socket.settimeout(RETRY_TIMEOUT)
                        try:
                            r_data, client_address = self.server_socket.recvfrom(PACKET_SIZE)
                            r_data = r_data.decode()
                            ack_num = int(r_data.split(":")[1])
                            r_seq_num = int(r_data.split(":")[0])
                            packet = r_data.split(":")[2]
                            received_checksum = int(r_data.split(":")[3])
                            calculated_checksum = udp_checksum(r_seq_num,ack_num,0,packet)
                            if calc_checksum==received_checksum:
                                if ack_num == self.seq_num + len(data):
                                    print("Positive ACK received")
                                    return
                            # negative ack
                            # ya3ni el reponse kanet corrupted
                                else :
                                    print("Negative ACK received. Retrying...")
                                    continue
                                # resend
                        except socket.timeout:
                        # Timeout occurred, retry
                            print("Timeout waiting for ACK packet form Client. Retrying...")
                            break
                            
                elif request.split()[0] == "POST":
                    body = request.split()[-1]
                    print(f"body of POST request {body}")
                    self.seq_num = ack_num
                    self.ack_num = seq_num+len(request)
                    while True:
                        data = "HTTP/1.1 200 OK\r\nSuccessful POST Request"
                        checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                        packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                        server_socket.sendto(packet.encode(), client_address)
                        # Listen for ACK packet from the client
                        self.server_socket.settimeout(RETRY_TIMEOUT)
                        try:
                            r_data, client_address = self.server_socket.recvfrom(PACKET_SIZE)
                            r_data = r_data.decode()
                            ack_num = int(r_data.split(":")[1])
                            r_seq_num = int(r_data.split(":")[0])
                            packet = r_data.split(":")[2]
                            received_checksum = int(r_data.split(":")[3])
                            calculated_checksum = udp_checksum(r_seq_num,ack_num,0,packet)
                            if calc_checksum==received_checksum:
                                if ack_num == self.seq_num + len(data):
                                    print("Positive ACK received")
                                    return
                                # negative ack
                                # ya3ni el reponse kanet corrupted
                                else :
                                    print("Negative ACK received. Retrying...")
                                    continue
                                # resend
                        except socket.timeout:
                            # Timeout occurred, retry
                            print("Timeout waiting for ACK packet form Client. Retrying...")
                            break
                
                else:
                    self.seq_num = ack_num
                    self.ack_num = seq_num+len(request)
                    while True:
                        data = "HTTP/1.1 400 Bad Request\r\n"
                        checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                        packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                        self.server_socket.sendto(packet.encode(), client_address)
                        # Listen for ACK packet from the client
                        self.server_socket.settimeout(RETRY_TIMEOUT)
                        try:
                            r_data, client_address = self.server_socket.recvfrom(PACKET_SIZE)
                            r_data = r_data.decode()
                            ack_num = int(r_data.split(":")[1])
                            r_seq_num = int(r_data.split(":")[0])
                            packet = r_data.split(":")[2]
                            received_checksum = int(r_data.split(":")[3])
                            calculated_checksum = udp_checksum(r_seq_num,ack_num,0,packet)
                            if calc_checksum==received_checksum:
                                if ack_num == self.seq_num + len(data):
                                    print("Positive ACK received")
                                    return
                            # negative ack
                            # ya3ni el reponse kanet corrupted
                                else :
                                    print("Negative ACK received. Retrying...")
                                    continue
                                # resend
                        except socket.timeout:
                            # Timeout occurred, retry
                            print("Timeout waiting for ACK packet form Client. Retrying...")
                            break
            else:
                # if packet sent is corrupted 
                print("Packet is Corrupted")
            self.check_received()
            return
                                       
                                       
        
    # connection terminate 
    def connection_termination(self):
        PACKET_SIZE = self.PACKET_SIZE
        print("Received FIN packet from client.")
        RETRY_TIMEOUT = 20
        data = "ACK"
        checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
        packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
        # Send ACK packet to the client
        server_socket.sendto(packet.encode(), client_address)
        print("Sent ACK packet to client.")
        self.seq_num += len(data) 
        
        data = "FIN"
        checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
        packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
        server_socket.sendto(packet.encode(), client_address)
        print("Sent FIN packet to client.")


        while True : 
            # Listen for ACK packet from the server
            server_socket.settimeout(RETRY_TIMEOUT)
            try:
                data, server_address = server_socket.recvfrom(PACKET_SIZE)
                data = data.decode()
                seq_num = int(data.split(":")[0])
                ack_num = int(data.split(":")[1])
                packet = data.split(":")[2]
                received_checksum = data.split(":")[3]
                calc_checksum = udp_checksum(seq_num,ack_num,0,packet)
                # Check for ACK packet
                if received_checksum == calc_checksum:
                    print("Received ACK packet from client.")
                    exit(0)
                    return True
                # duplicate FIN
                if packet == "FIN":
                    print("FIN duplicate")
                    continue
            except socket.timeout:
                # Timeout occurred, retry
                print("Timeout waiting for ACK packet form Client. Retrying...")

        return False

def udp_checksum(seq_num,ack_num,recv_window,data):
    data = data.encode("utf-8")
    # Pad data if the length is odd
    if len(data) % 2 == 1:
        data += b'\0'

    # add seq number and ack number and recv window and flag
    # Calculate the checksum using the same algorithm as used in the IP header
    sum = 0

    seq1 = (seq_num >> 16) & 0xFFFF # msb 16 bits of seq num
    seq2 = seq_num & 0xFFFF # lsb 16 bits of seq num
    ack1 = (ack_num >> 16) & 0xFFFF
    ack2 = ack_num & 0xFFFF

    sum += seq1
    sum += seq2
    if sum >> 16:
        sum = (sum & 0xFFFF) + 1
    sum += ack1
    if sum >> 16:
        sum = (sum & 0xFFFF) + 1
    sum += ack2
    if sum >> 16:
        sum = (sum & 0xFFFF) + 1
    sum += recv_window
    if sum >> 16:
        sum = (sum & 0xFFFF) + 1
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + (data[i+1])
        sum += word
        
        if sum >> 16:
            sum = (sum & 0xFFFF) + 1
    sum = ~sum & 0xFFFF
    return sum

def main():
    serv = server()
if __name__ == "__main__":
    main()