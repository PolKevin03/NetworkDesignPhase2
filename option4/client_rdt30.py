from socket import *
import sys
import random
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

def maybe_drop_ack(pkt, rate):
    if rate > 0 and random.random() < rate:
        return None, True
    return pkt, False

if len(sys.argv) < 2:
    print("Usage: python client_rdt30.py file.bmp [ack_loss 0..1] [seed]")
    sys.exit()

file_path = sys.argv[1]
loss = float(sys.argv[2]) if len(sys.argv) >= 3 else 0.0
seed = int(sys.argv[3]) if len(sys.argv) >= 4 else None

if seed is not None:
    random.seed(seed)

serverName = "localhost"
serverPort = 13000
CHUNK = 1024

sock = socket(AF_INET, SOCK_DGRAM)
sock.settimeout(1)

seq = 0
dropped = 0
retrans = 0
sent = 0

with open(file_path, "rb") as f:
    while True:
        data = f.read(CHUNK)
        if not data:
            break

        pkt = make_packet(DATA, seq, data)
        sent += 1

        while True:
            sock.sendto(pkt, (serverName, serverPort))
            try:
                ack, _ = sock.recvfrom(2048)
                ack, d = maybe_drop_ack(ack, loss)
                if d:
                    dropped += 1
                    retrans += 1
                    continue

                t, s, _, bad = parse_packet(ack)
                if not bad and t == ACK and s == seq:
                    seq = 1 - seq
                    break
                else:
                    retrans += 1
            except timeout:
                retrans += 1

endpkt = make_packet(END, seq, b"")

while True:
    sock.sendto(endpkt, (serverName, serverPort))
    try:
        ack, _ = sock.recvfrom(2048)
        ack, d = maybe_drop_ack(ack, loss)
        if d:
            dropped += 1
            retrans += 1
            continue

        t, s, _, bad = parse_packet(ack)
        if not bad and t == ACK and s == seq:
            break
        else:
            retrans += 1
    except timeout:
        retrans += 1

sock.close()

print("Done sending.")
print(f"ack_loss_rate: {loss}")
print(f"chunks_sent: {sent}")
print(f"dropped_acks: {dropped}")
print(f"retransmissions: {retrans}")