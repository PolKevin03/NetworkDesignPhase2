import sys
import random
import struct
import zlib

# packet type constants
DATA = 0
ACK = 1
END = 2

# header format: type(1), seq(1), length(2), checksum(4)
HEADER_FMT = "!BBHI"
HEADER_LEN = struct.calcsize(HEADER_FMT)

def compute_checksum(data_bytes):
    return zlib.crc32(data_bytes) & 0xffffffff  # crc32 checksum

def make_packet(ptype, seq, payload=b""):
    length = len(payload)  # payload size
    checksum = 0  # temporary checksum
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
    checksum = compute_checksum(header + payload)  # compute checksum
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)
    return header + payload  # full packet

def parse_packet(packet_bytes):
    if len(packet_bytes) < HEADER_LEN:
        return None, None, b"", True  # invalid packet

    header = packet_bytes[:HEADER_LEN]
    payload = packet_bytes[HEADER_LEN:]

    ptype, seq, length, checksum = struct.unpack(HEADER_FMT, header)

    header_zero = struct.pack(HEADER_FMT, ptype, seq, length, 0)
    calc_checksum = compute_checksum(header_zero + payload)

    corrupt = (calc_checksum != checksum)
    return ptype, seq, payload, corrupt

def corrupt_one_bit(packet_bytes):
    """flip exactly one random bit in the ack packet"""
    if not packet_bytes:
        return packet_bytes
    ba = bytearray(packet_bytes)
    i = random.randrange(len(ba))
    ba[i] ^= (1 << random.randrange(8))  # flip 1 bit
    return bytes(ba)

def maybe_corrupt_ack_at_sender(ack_packet, ack_error_rate):
    """option 2: sender corrupts ack after recv"""
    injected = False
    if ack_error_rate > 0 and random.random() < ack_error_rate:
        ack_packet = corrupt_one_bit(ack_packet)
        injected = True
    return ack_packet, injected

# usage: python client_rdt22_option2.py file.bmp [ack_error_rate 0..1] [seed]
if len(sys.argv) < 2:
    print("Usage: python client_rdt22_option2.py file.bmp [ack_error_rate 0..1] [seed]")
    sys.exit(1)

file_path = sys.argv[1]
ack_error_rate = float(sys.argv[2]) if len(sys.argv) >= 3 else 0.0
seed = int(sys.argv[3]) if len(sys.argv) >= 4 else None

if seed is not None:
    random.seed(seed)  # set seed for repeatable tests

serverName = "localhost"
serverPort = 13000
CHUNK = 1024

clientSocket = socket(AF_INET, SOCK_DGRAM)  # create udp socket
clientSocket.settimeout(1)  # timeout for resend

seq = 0  # start sequence number

acks_injected = 0
retransmissions = 0
chunks_sent = 0

with open(file_path, "rb") as f:
    while True:
        data = f.read(CHUNK)  # read file chunk
        if not data:
            break

        packet = make_packet(DATA, seq, data)
        chunks_sent += 1

        while True:
            clientSocket.sendto(packet, (serverName, serverPort))  # send packet

            try:
                ack_packet, _ = clientSocket.recvfrom(2048)

                # option 2 injection happens here
                ack_packet, injected = maybe_corrupt_ack_at_sender(ack_packet, ack_error_rate)
                if injected:
                    acks_injected += 1

                ptype, ack_seq, _, corrupt = parse_packet(ack_packet)

                # correct ack
                if not corrupt and ptype == ACK and ack_seq == seq:
                    seq = 1 - seq  # toggle sequence
                    break

                retransmissions += 1  # resend

            except timeout:
                retransmissions += 1
                continue

# send end packet
endpkt = make_packet(END, seq, b"")

while True:
    clientSocket.sendto(endpkt, (serverName, serverPort))

    try:
        ack_packet, _ = clientSocket.recvfrom(2048)

        ack_packet, injected = maybe_corrupt_ack_at_sender(ack_packet, ack_error_rate)
        if injected:
            acks_injected += 1

        ptype, ack_seq, _, corrupt = parse_packet(ack_packet)

        if not corrupt and ptype == ACK and ack_seq == seq:
            break

        retransmissions += 1

    except timeout:
        retransmissions += 1
        continue

clientSocket.close()

print("Done sending.")
print(f"ack_error_rate: {ack_error_rate}")
print(f"chunks_sent: {chunks_sent}")
print(f"injected_corrupted_acks: {acks_injected}")
print(f"retransmissions: {retransmissions}")
