from socket import *
from rdt_utils import *
import random, sys

PORT = 13000
BUF = 2048
#udp network 

def maybe_corrupt(packet, rate):
    if rate <= 0 or len(packet) <= HEADER_LEN:
        return packet, False
    if packet[0] != DATA or random.random() >= rate:
        return packet, False

    ba = bytearray(packet)
    i = random.randrange(HEADER_LEN, len(ba))     # payload only
    ba[i] ^= (1 << random.randrange(8))           # flip 1 bit
    return bytes(ba), True
#corrupts the packets



rate = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
seed = int(sys.argv[2]) if len(sys.argv) > 2 else None
out_name = sys.argv[3] if len(sys.argv) > 3 else "received.bmp"
# choose the rate of corruption when running



if not (0.0 <= rate <= 1.0):
    print("data_error_rate must be 0..1")
    sys.exit(1)
if seed is not None:
    random.seed(seed)

#creates a random seed to choose corruption
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind(("", PORT))
print(f"RDT 2.2 Server Ready | option 3 rate={rate}")
#creates socket

expected = 0
accepted = injected = dupacks = 0
#how many times we purposely corrupt the data

out = open(out_name, "wb")

while True:
    pkt, addr = sock.recvfrom(BUF)
#where to receive packets
    pkt, did = maybe_corrupt(pkt, rate)
    if did:
        injected += 1
#Randomly corrupts packets, counts how many were corrupted
    if len(pkt) < HEADER_LEN:
        sock.sendto(make_packet(ACK, 1 - expected), addr)
        dupacks += 1
        continue
#if header isnt full, the packet is invalid
    ptype, seq, payload, corrupt = parse_packet(pkt)
#detects corruption
    if ptype == END:
        sock.sendto(make_packet(ACK, seq), addr)
        break

    if not corrupt and ptype == DATA and seq == expected:
        out.write(payload)
        sock.sendto(make_packet(ACK, seq), addr)
        expected ^= 1
        accepted += 1
    else:
        sock.sendto(make_packet(ACK, 1 - expected), addr)
        dupacks += 1
#if the packets are good it keeps the data otherwise it rejects and resends
out.close()
sock.close()
print(f"saved: {out_name} | accepted={accepted} injected={injected} dupacks={dupacks}")