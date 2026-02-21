from socket import * #import udp socket functions
from rdt_utils import * #import packet utilities and constants

serverPort = 13000#udp port
CHUNK = 1024 #max size

serverSocket = socket(AF_INET, SOCK_DGRAM)  #udp socket
serverSocket.bind(("", serverPort)) #bind socket to port

print("RDT 2.2 Server Ready") #server message

outfile = open("received.bmp", "wb") #open output file for writing

expected_seq = 0  #seq 0 first

while True:  #receive 
    packet, clientAddress = serverSocket.recvfrom(2048) #receive packet from client

    ptype, seq, payload, corrupt = parse_packet(packet)#checks packet and check checksum

    if ptype == END:#check for end of transfer
        ackpkt = make_packet(ACK, seq, b"") #final ack
        serverSocket.sendto(ackpkt, clientAddress) #send ack
        break #stop 

    if not corrupt and seq == expected_seq:#accept only correct and packet
        outfile.write(payload)  #write to file
        ackpkt = make_packet(ACK, seq, b"")  #build ack 
        serverSocket.sendto(ackpkt, clientAddress) #send ack
        expected_seq = 1 - expected_seq #seq
    else:
        last_good = 1 - expected_seq  #last correctly received seq
        ackpkt = make_packet(ACK, last_good, b"") 
        serverSocket.sendto(ackpkt, clientAddress) #send duplicate ack

outfile.close()#close output file
serverSocket.close() #close udp socket
print("File saved.")#done message