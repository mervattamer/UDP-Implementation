import time
import socket
import random
# 3and el server 5aleeh mayeb3atsh el response 1 time out of 10
class server:
    def __init__(self,PACKET_SIZE = 100,FORMAT = "utf-8",PORT = 5000):
        self.seq_num = 10
        self.ack_num = 0
        self.PACKET_SIZE = PACKET_SIZE
        self.FORMAT = FORMAT
        self.PORT = PORT
        self.IP = socket.gethostbyname(socket.gethostname())
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
        self.server_address = (self.IP,self.PORT)
        self.server_socket.bind(self.server_address) 
        print('UDP server is running on {}:{}'.format(*self.server_address))
        self.running()
    
    def running(self):
        self.server_socket.settimeout(1000)
        if self.establish_connection():
            self.check_received()

    def establish_connection(self):
        MAX_RETRIES = 3
        RETRY_TIMEOUT = 2  # seconds
        retries = 0

        # wait for SYN packet
        while retries < MAX_RETRIES:
            # Listen for incoming SYN packets
            data, client_address = self.server_socket.recvfrom(self.PACKET_SIZE)
            data = data.decode()

            # f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
            seq_num = int(data.split(":")[0])
            packet = data.split(":")[2]
            received_checksum = int(data.split(":")[3])
            calculated_checksum = udp_checksum(seq_num,0,0,packet)

            # Check for SYN packet
            if packet == "SYN" and received_checksum == calculated_checksum:
                # Send SYN-ACK packet if SYN received
                print("Received SYN from client.")
                ack_num = seq_num+len(packet)
                seq_num = self.seq_num
                data = "SYN-ACK"
                checksum = udp_checksum(seq_num,ack_num,0,data)

                packet = f"{seq_num}:{ack_num}:{data}:{checksum}:{0}"
                self.server_socket.sendto(packet.encode(), client_address)

                print("Sent SYN-ACK to client.")

                # Listen for ACK packet from the client
                self.server_socket.settimeout(RETRY_TIMEOUT)
                try:
                    r_data, client_address = self.server_socket.recvfrom(self.PACKET_SIZE)
                    r_data = r_data.decode()

                    ack_num = int(r_data.split(":")[1])
                    r_seq_num = int(r_data.split(":")[0])
                    packet = r_data.split(":")[2]
                    received_checksum = int(r_data.split(":")[3])
                    calculated_checksum = udp_checksum(r_seq_num,ack_num,0,packet)

                    # Check if the received packet is an ACK packet
                    if packet == "ACK" and ack_num == seq_num+len(data) and calculated_checksum == received_checksum:
                        self.seq_num = ack_num
                        self.ack_num = r_seq_num+len("ACK")
                        print("Received ACK from server.")
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

        print("")
        print("")
        RETRY_TIMEOUT = 15
        self.server_socket.settimeout(RETRY_TIMEOUT)
        data, client_address = self.server_socket.recvfrom(self.PACKET_SIZE)
        data = data.decode()

        seq_num = int(data.split(":")[0])
        ack_num = int(data.split(":")[1])
        request = data.split(':')[2]
        received_checksum = int(data.split(':')[3])
        calc_checksum = udp_checksum(seq_num,ack_num,0,request)

        # check if this message is sent to Finish the connection
        if calc_checksum == received_checksum and request == "FIN":
            self.seq_num = ack_num
            self.ack_num = seq_num+len("FIN")
            self.connection_termination(client_address)
        
        else:


            # packet loss implementation
            if random.randint(0,1) == 0:
                print("Losing data on purpose")
                self.check_received()
                return


            else :
                # check if data is corrupted here and send neg ack
                if calc_checksum == received_checksum:


                    # GET Request 
                    if request.split()[0] == "GET":
                        print("Received GET request")
                        path = request.split()[1]
                        self.seq_num = ack_num
                        self.ack_num = seq_num+len(request)
                        # to resend if negative ack
                        while True:
                            # Send response
                            if path == "/path/to/resource": 
                                data = "HTTP/1.0 200 OK\r\nSuccessful GET Request"
                                checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                                packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                                self.server_socket.sendto(packet.encode(), client_address)
                            else :
                                data = "HTTP/1.0 404 Not Found\r\nPath Not Found"
                                checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                                packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                                self.server_socket.sendto(packet.encode(), client_address)
                            print("Response sent!")
                            
                            # Listen for ACK packet from the client
                            self.server_socket.settimeout(RETRY_TIMEOUT)
                            try:
                                r_data, client_address = self.server_socket.recvfrom(self.PACKET_SIZE)
                                r_data = r_data.decode()
                                ack_num = int(r_data.split(":")[1])
                                r_seq_num = int(r_data.split(":")[0])
                                packet = r_data.split(":")[2]
                                received_checksum = int(r_data.split(":")[3])
                                calc_checksum = udp_checksum(r_seq_num,ack_num,0,packet)

                                # check if ACK from client is corrupted
                                if calc_checksum==received_checksum:
                                    if ack_num == self.seq_num + len(data):
                                        print("Positive ACK received")
                                        break

                                    # response sent to client was corrupted
                                    else :
                                        print("Negative ACK received. Retrying...")
                                        continue # Resend it
                                    
                            except socket.timeout:
                            # Timeout occurred, retry
                                print("Timeout waiting for ACK packet form Client. Retrying...")
                            
                    # POST Request        
                    elif request.split()[0] == "POST":
                        body = " ".join(request.split()[3:])
                        print(f"body of POST request : {body}")
                        self.seq_num = ack_num
                        self.ack_num = seq_num+len(request)

                        # to resend if negative ack
                        while True:
                            data = "HTTP/1.0 200 OK\r\nSuccessful POST Request"
                            checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                            packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                            self.server_socket.sendto(packet.encode(), client_address)
                            print("Response sent!")
                            # Listen for ACK packet from the client
                            self.server_socket.settimeout(RETRY_TIMEOUT)
                            try:
                                r_data, client_address = self.server_socket.recvfrom(self.PACKET_SIZE)
                                r_data = r_data.decode()

                                ack_num = int(r_data.split(":")[1])
                                r_seq_num = int(r_data.split(":")[0])
                                packet = r_data.split(":")[2]
                                received_checksum = int(r_data.split(":")[3])
                                calc_checksum = udp_checksum(r_seq_num,ack_num,0,packet)

                                if calc_checksum==received_checksum:
                                    if ack_num == self.seq_num + len(data):
                                        print("Positive ACK received")
                                        break
                                    else :
                                        print("Negative ACK received. Retrying...")
                                        continue
                            except socket.timeout:
                                # Timeout occurred, retry
                                print("Timeout waiting for ACK packet form Client. Retrying...")
                            
                    # BAD request
                    else:
                        self.seq_num = ack_num
                        self.ack_num = seq_num+len(request)
                        while True:
                            data = "HTTP/1.0 400 Bad Request\r\n"
                            checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
                            packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
                            self.server_socket.sendto(packet.encode(), client_address)
                            # Listen for ACK packet from the client
                            self.server_socket.settimeout(RETRY_TIMEOUT)
                            try:
                                r_data, client_address = self.server_socket.recvfrom(self.PACKET_SIZE)
                                r_data = r_data.decode()
                                ack_num = int(r_data.split(":")[1])
                                r_seq_num = int(r_data.split(":")[0])
                                packet = r_data.split(":")[2]
                                received_checksum = int(r_data.split(":")[3])
                                calc_checksum = udp_checksum(r_seq_num,ack_num,0,packet)
                                if calc_checksum==received_checksum:
                                    if ack_num == self.seq_num + len(data):
                                        print("Positive ACK received")
                                        break
                                    else :
                                        print("Negative ACK received. Retrying...")
                                        continue
                            except socket.timeout:
                                # Timeout occurred, retry
                                print("Timeout waiting for ACK packet form Client. Retrying...")
                            
                else:
                    # if packet sent is corrupted 
                    print("Packet is Corrupted")
                self.check_received()
                return
                                           
        
    # connection terminate 
    def connection_termination(self,client_address):
        print("Received FIN packet from client.")
        RETRY_TIMEOUT = 20
        data = "ACK"
        checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
        packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"

        # Send ACK packet to the client
        self.server_socket.sendto(packet.encode(), client_address)
        print("Sent ACK packet to client.")
        self.seq_num += len(data) 


        data = "FIN"
        checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
        packet = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
        self.server_socket.sendto(packet.encode(), client_address)
        print("Sent FIN packet to client.")

        # if ack wasnt sent will wait for it again
        while True : 
            # Listen for ACK packet from the server
            self.server_socket.settimeout(RETRY_TIMEOUT)
            try:
                data, server_address = self.server_socket.recvfrom(self.PACKET_SIZE)
                data = data.decode()
                seq_num = int(data.split(":")[0])
                ack_num = int(data.split(":")[1])
                packet = data.split(":")[2]
                received_checksum = int(data.split(":")[3])
                calc_checksum = udp_checksum(seq_num,ack_num,0,packet)
                # Check for ACK packet
                if packet == "ACK" and (received_checksum == calc_checksum):
                    print("Received ACK packet from client.")
                    self.running()
                    #exit(0)
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