import socket
import time
import random
# implement packet loss we packket corruption
class client:
    def __init__(self,PACKET_SIZE = 100,FORMAT = "utf-8",PORT = 5000):
        self.seq_num = 90
        self.ack_num = 0
        self.PACKET_SIZE = PACKET_SIZE
        self.FORMAT = FORMAT
        self.PORT = PORT
        self.IP = socket.gethostbyname(socket.gethostname())
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self.establish_connection():
            self.send_request("GET","/path/to/resource","1.0")
            #self.send_request("POST","/path/to/resource","1.0","helloooo how are you")
            self.connection_termination()
    
    def establish_connection(self):
        seq_num = self.seq_num
        ack_num = self.ack_num
        MAX_RETRIES = 3
        RETRY_TIMEOUT = 2  # seconds
        retries = 0
        server_address = (self.IP,self.PORT)
        PACKET_SIZE = self.PACKET_SIZE
        while retries < MAX_RETRIES:
            # Send SYN packet to the server
            # f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
            data = "SYN" 
            checksum = udp_checksum(seq_num,ack_num,0,data)
            packet = f"{seq_num}:{ack_num}:{data}:{checksum}:{0}"
            self.client_socket.sendto(packet.encode(),server_address)
            print("Sent SYN packet to the server.")

            # Listen for SYN-ACK packet from the server
            self.client_socket.settimeout(RETRY_TIMEOUT)
            try:
                data, server_address = self.client_socket.recvfrom(PACKET_SIZE)
                data = data.decode()
                r_seq_num = int(data.split(":")[0])
                ack_num = int(data.split(":")[1])
                packet = data.split(":")[2]
                received_checksum = int(data.split(":")[3])
                calculated_checksum = udp_checksum(r_seq_num,ack_num,0,packet)
                # Check for SYN-ACK packet
                if packet == "SYN-ACK" and received_checksum == calculated_checksum and ack_num == seq_num+len("SYN"):
                    # Send ACK packet to the server
                    ack_num = r_seq_num+len("SYN-ACK")
                    seq_num = seq_num+len("SYN")
                    data = "ACK"
                    checksum = udp_checksum(seq_num,ack_num,0,data)
                    packet = f"{seq_num}:{ack_num}:{data}:{checksum}:{0}"
                    self.client_socket.sendto(packet.encode(), server_address)

                    print("Connection established successfully.")
                    self.seq_num = seq_num + len("ACK")
                    self.ack_num = ack_num
                    print(self.seq_num,self.ack_num)
                    # keda el seq number el hanebda2 beeh howa
                    return True
                else :
                    # 
                    break
            except socket.timeout:
                # Timeout occurred, retry
                print("Timeout occurred. Retrying...")
                retries += 1
                continue

        print("Connection establishment failed after {} retries.".format(MAX_RETRIES))
        return False
    
    def connection_termination(self):
        MAX_RETRIES = 5
        RETRY_TIMEOUT = 5  # seconds

        retries = 0
        server_address = (self.IP,self.PORT)
        PACKET_SIZE = self.PACKET_SIZE
        while retries < MAX_RETRIES:
            # Send FIN packet to the server
            # f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
            data = "FIN"
            checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
            packet_data = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
            self.client_socket.sendto(packet_data.encode(), server_address)
            print("Sent FIN packet to terminate connection.")
            time.sleep(1)
            # Listen for ACK packet from the server
            self.client_socket.settimeout(RETRY_TIMEOUT)
            try:
                data_received, server_address = self.client_socket.recvfrom(PACKET_SIZE)
                data_received = data_received.decode()
                #f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
                r_seq_num = int(data_received.split(":")[0])
                r_ack_num = int(data_received.split(":")[1])
                ack = data_received.split(":")[2]
                r_checksum = int(data_received.split(":")[3])
                recv_window = int(data_received.split(":")[4])
                calc_checksum = udp_checksum(r_seq_num,r_ack_num,recv_window,ack)
                if r_checksum == calc_checksum:
                    if (r_ack_num == self.seq_num + len(data)) and ack == "ACK":
                        self.seq_num = r_ack_num
                        self.ack_num = r_seq_num + len(ack)
                        print("Received ACK packet from server.")
                        # Listen for ACK packet from the server
                        self.client_socket.settimeout(RETRY_TIMEOUT)
                        try:
                            # Listen for FIN packet from the server
                            data_received, server_address = self.client_socket.recvfrom(PACKET_SIZE)
                            data_received = data_received.decode()
                            #f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
                            r_seq_num = int(data_received.split(":")[0])
                            r_ack_num = int(data_received.split(":")[1])
                            fin = data_received.split(":")[2]
                            r_checksum = int(data_received.split(":")[3])
                            recv_window = int(data_received.split(":")[4])
                            calc_checksum = udp_checksum(r_seq_num,r_ack_num,recv_window,ack)
                            # Check for FIN packet
                            if r_checksum == calc_checksum:
                                if fin == "FIN":
                                    print("Received FIN packet from server.")
                                    self.client_socket.sendto("ACK".encode(), server_address)
                                    print("Sent ACK packet to terminate connection.")
                                    print("Connection terminated successfully.")
                                    return True
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
        return False

    
    
    def send_request(self,method,path,version,body=""):
        PACKET_SIZE = self.PACKET_SIZE
        server_address = (self.IP,self.PORT)
        if method == "GET":
            data = f"{method} {path} HTTP/{version}\r\n"
        elif method == "POST":
            data = f"{method} {path} HTTP/{version}\r\n {body} \r\n"
        TIMEOUT = 5
        if random.randint(0,9) == 0:
            # corrupt data
            checksum = 0
        else:
            checksum = udp_checksum(self.seq_num,self.ack_num,0,data)
        # packing data with its checksum
        packet_data = f"{self.seq_num}:{self.ack_num}:{data}:{checksum}:{0}"
        self.client_socket.sendto(packet_data.encode(), server_address)

        while True:
            self.client_socket.settimeout(TIMEOUT)

            try:
                data_received, _ = self.client_socket.recvfrom(PACKET_SIZE)
                data_received = data_received.decode()
                # feh moshkilla fel response
                #f"{seq_num}:{ack_num}:{packet}:{checksum}:{recv_window}"
                r_seq_num = int(data_received.split(":")[0])
                r_ack_num = int(data_received.split(":")[1])
                response = data_received.split(":")[2]
                r_checksum = int(data_received.split(":")[3])
                #recv_window = int(data_received.split(":")[4])
                calc_checksum = udp_checksum(r_seq_num,r_ack_num,0,response)
                # no error in checksum
                if r_checksum == calc_checksum:
                    # ack or negative ack
                    if r_ack_num == (self.seq_num + len(data)):
                        print(response)
                        # SEND ACK
                        self.seq_num = self.seq_num + len(data)
                        self.ack_num = r_seq_num + len(response)
                        checksum = udp_checksum(self.seq_num,self.ack_num,0,'ACK')
                        packet_data = f"{self.seq_num}:{self.ack_num}:{'ACK'}:{checksum}:{0}"
                        self.client_socket.sendto(packet_data.encode(), server_address)
                        return
                    else:
                        print("Negative ack received") 
                        print("Retrying..")
                        self.send_request(method,path,version,body)
                        return
                else:
                    # drop
                    print("Corrupted message!!")
                    #negative ack
                    checksum = udp_checksum(0,self.ack_num,0,"")
                    packet_data = f"{0}:{self.ack_num}:{''}:{checksum}:{0}"
                    self.client_socket.sendto(packet_data.encode(), server_address)
                    time.sleep(1)
                    # hane3mil ehh?? 
            # implement paccket loss in the serever hena implement packet corruption
            # el3ab fel checksum beta3et wa7da minhom
            # packet loss   
            except socket.timeout:
                print("Time out waiting for http response") 
                print("Retrying..")
                self.send_request(method,path,version,body)
                return


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
    cl = client()
if __name__ == "__main__":
    main()
      