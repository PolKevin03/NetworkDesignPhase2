from socket import *  # udp socket functions
import struct
import zlib

# packet types
DATA = 0
ACK = 1
END = 2

HEADER_FMT = "!BBHI"
HEADER_LEN = struct.calcsize(HEADER_FMT)

def compute_checksum(data_bytes):
    return zlib.crc32(data_bytes) & 0xffffffff

def make_packet(ptype, seq, payload=b""):
    length = len(payload)
    checksum = 0
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
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
    calc_checksum = compute_checksum(header_zero + payload)

    corrupt = (calc_checksum != checksum)
    return ptype, seq, payload, corrupt

serverPort = 13000
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(("", serverPort))

print("RDT 2.2 Server Ready (Option 2)")

outfile = open("received.bmp", "wb")
expected_seq = 0

while True:
    packet, clientAddress = serverSocket.recvfrom(2048)

    ptype, seq, payload, corrupt = parse_packet(packet)

    if ptype == END:
        serverSocket.sendto(make_packet(ACK, seq, b""), clientAddress)
        break

    if not corrupt and ptype == DATA and seq == expected_seq:
        outfile.write(payload)
        serverSocket.sendto(make_packet(ACK, seq, b""), clientAddress)
        expected_seq = 1 - expected_seq
    else:
        last_good = 1 - expected_seq
        serverSocket.sendto(make_packet(ACK, last_good, b""), clientAddress)

outfile.close()
serverSocket.close()
print("File saved.")
