from socket import *  #udp socket functions
import struct  
import zlib  #used checksum

DATA =0  #data packet type
ACK =1   
END =2   

HEADER_FMT ="!BBHI"  
HEADER_LEN =struct.calcsize(HEADER_FMT)  #header size in bytes

def compute_checksum(data_bytes):
    return zlib.crc32(data_bytes) & 0xffffffff  #crc32 checksum

def make_packet(ptype, seq, payload=b""):
    length =len(payload)  #payload size
    checksum =0  #checksum
    header =struct.pack(HEADER_FMT, ptype, seq, length, checksum) 
    checksum = compute_checksum(header + payload)  #compute checksum
    header =struct.pack(HEADER_FMT, ptype, seq, length, checksum)  #rebuild header with checksum
    return header + payload  #return full packet

def parse_packet(packet_bytes):
    if len(packet_bytes) < HEADER_LEN:
        return None, None, b"", True  #wrong packet

    header = packet_bytes[:HEADER_LEN] 
    payload = packet_bytes[HEADER_LEN:]  

    ptype, seq, length, checksum = struct.unpack(HEADER_FMT, header)  #open header

    header_zero = struct.pack(HEADER_FMT, ptype, seq, length, 0)  #zero checksum header
    calc_checksum = compute_checksum(header_zero + payload)  #checksum

    corrupt = (calc_checksum != checksum)  #check 
    return ptype, seq, payload, corrupt  #return values

serverPort = 13000  #udp port number
serverSocket = socket(AF_INET, SOCK_DGRAM)  #create udp socket
serverSocket.bind(("", serverPort))  

print("RDT 2.2 Server Ready (Option 2)")  #server start message

outfile = open("received.bmp", "wb")  #open output file
expected_seq = 0  #expect sequence 0 first

while True:  
    packet, clientAddress = serverSocket.recvfrom(2048)  #receive packet

    ptype, seq, payload, corrupt = parse_packet(packet)  #check packet and checksum

    if ptype == END:  #if end packet
        serverSocket.sendto(make_packet(ACK, seq, b""), clientAddress)  #send final ack
        break  

    if not corrupt and ptype == DATA and seq == expected_seq:  #correct packet
        outfile.write(payload)  #write data to file
        serverSocket.sendto(make_packet(ACK, seq, b""), clientAddress)  #send ack
        expected_seq = 1 - expected_seq  #seq
    else:
        last_good = 1 - expected_seq  #last correct seq
        serverSocket.sendto(make_packet(ACK, last_good, b""), clientAddress)  #resend last ack

outfile.close()  #close file
serverSocket.close()  #close socket
print("File saved.")  #done message
