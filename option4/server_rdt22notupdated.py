from socket import *
import struct
import zlib

DATA = 0
ACK = 1
END = 2

HEADER_FMT = "!BBHI"
HEADER_LEN = struct.calcsize(HEADER_FMT)

def compute_checksum(data_bytes):
    return zlib.crc32(data_bytes) & 0xffffffff

def make_packet(ptype, seq, payload=b""):
    length = len(payload)
    header = struct.pack(HEADER_FMT, ptype, seq, length, 0)
    checksum = compute_checksum(header + payload)
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
    return header + payload

def parse_packet(packet_bytes):
    if len(packet_bytes) < HEADER_LEN:
        return None, None, b"", True

    header = packet_bytes[:HEADER_LEN]
    payload = packet_bytes[HEADER_LEN:]

    ptype, seq, length, checksum = struct.unpack(HEADER_FMT, header)

    header_zero = struct.pack(HEADER_FMT, ptype, seq, length, 0)
    calc = compute_checksum(header_zero + payload)

    return ptype, seq, payload, calc != checksum


serverPort = 13000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", serverPort))

print("Server Ready (Option 4)")

outfile = open("received.bmp", "wb")
expected_seq = 0

while True:
    packet, clientAddress = serverSocket.recvfrom(2048)

    ptype, seq, payload, corrupt = parse_packet(packet)

    if ptype == END:
        serverSocket.sendto(make_packet(ACK, seq), clientAddress)
        break

    if not corrupt and ptype == DATA and seq == expected_seq:
        outfile.write(payload)
        serverSocket.sendto(make_packet(ACK, seq), clientAddress)
        expected_seq ^= 1
    else:
        serverSocket.sendto(make_packet(ACK, 1 - expected_seq), clientAddress)

outfile.close()
serverSocket.close()

print("File saved.")