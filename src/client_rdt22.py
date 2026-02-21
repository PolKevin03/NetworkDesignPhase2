from socket import *
import sys
import struct
import zlib

#packet types
DATA = 0
ACK = 1
END = 2

#header format
HEADER_FMT = "!BBHI"
HEADER_LEN = struct.calcsize(HEADER_FMT)


def compute_checksum(data_bytes):#checksum 
    return zlib.crc32(data_bytes) & 0xffffffff


def make_packet(ptype, seq, payload=b""): #build packet
    length = len(payload)
    checksum = 0
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
    checksum = compute_checksum(header + payload)
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
    return header + payload


def parse_packet(packet_bytes): #parse packet
    header = packet_bytes[:HEADER_LEN]
    payload = packet_bytes[HEADER_LEN:]

    ptype, seq, length, checksum = struct.unpack(HEADER_FMT, header)

    header_zero = struct.pack(HEADER_FMT, ptype, seq, length, 0)
    calc_checksum = compute_checksum(header_zero + payload)

    corrupt = (calc_checksum != checksum)

    return ptype, seq, payload, corrupt


serverName = "localhost" #IP
serverPort = 13000
CHUNK = 1024 #Max bytes per packet

#Check if file provided
if len(sys.argv) < 2:
    print("Usage: python client_rdt22.py file.bmp")
    sys.exit()

clientSocket = socket(AF_INET, SOCK_DGRAM)#Create UDP socket
clientSocket.settimeout(1)#Timeout for resend

seq = 0#Start with sequence 0

with open(sys.argv[1], "rb") as f: #open file in binary mode
    while True:
        data = f.read(CHUNK) #Read file chunk
        if not data:
            break  #Stop at end of file

        packet = make_packet(DATA, seq, data) #Create DATA packet

        while True:
            clientSocket.sendto(packet, (serverName, serverPort)) #Send packet
            try:
                ack_packet, _ = clientSocket.recvfrom(2048) #Wait for ACK
                ptype, ack_seq, _, corrupt = parse_packet(ack_packet)  #analyze ACK

                #if correct ACK received
                if not corrupt and ptype == ACK and ack_seq == seq:
                    seq = 1 - seq  #sequence number toggle
                    break
            except timeout:
                continue #resend on timeout

#END packet
endpkt = make_packet(END, seq, b"")

#Send END til correct ACK received
while True:
    clientSocket.sendto(endpkt, (serverName, serverPort))
    try:
        ack_packet, _ = clientSocket.recvfrom(2048)
        ptype, ack_seq, _, corrupt = parse_packet(ack_packet)

        if not corrupt and ptype == ACK and ack_seq == seq:
            break
    except timeout:
        continue

clientSocket.close()  #close socket
print("Done sending.")
