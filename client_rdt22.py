from socket import *
import sys
import random
from rdt_utils import *  # packet built

serverName = "localhost"  # IP
serverPort = 13000
CHUNK = 1024  # Max bytes per packet


def corrupt_one_bit(packet_bytes):
    """Flip exactly one random bit in the received ACK packet bytes."""
    if not packet_bytes:
        return packet_bytes
    ba = bytearray(packet_bytes)
    i = random.randrange(len(ba))
    bit = 1 << random.randrange(8)
    ba[i] ^= bit
    return bytes(ba)


def maybe_corrupt_ack_at_sender(ack_packet, ack_error_rate):
    """Option 2 injection point: sender corrupts the ACK after recvfrom()."""
    injected = False
    if ack_error_rate > 0 and random.random() < ack_error_rate:
        ack_packet = corrupt_one_bit(ack_packet)
        injected = True
    return ack_packet, injected


# Check args
# Usage: python client_rdt22.py file.bmp [ack_error_rate] [seed]
if len(sys.argv) < 2:
    print("Usage: python client_rdt22.py file.bmp [ack_error_rate 0..1] [seed]")
    sys.exit()

file_path = sys.argv[1]
ack_error_rate = float(sys.argv[2]) if len(sys.argv) >= 3 else 0.0
seed = int(sys.argv[3]) if len(sys.argv) >= 4 else None

if ack_error_rate < 0 or ack_error_rate > 1:
    print("ack_error_rate must be between 0 and 1")
    sys.exit(1)

if seed is not None:
    random.seed(seed)

clientSocket = socket(AF_INET, SOCK_DGRAM)  # Create UDP socket
clientSocket.settimeout(1)  # Timeout for resend

seq = 0  # Start with sequence 0

# Stats (useful for demo/debug)
acks_injected = 0
retransmissions = 0
chunks_sent = 0

with open(file_path, "rb") as f:  # open file in binary mode
    while True:
        data = f.read(CHUNK)  # Read file chunk
        if not data:
            break  # Stop at end of file

        packet = make_packet(DATA, seq, data)  # Create DATA packet
        chunks_sent += 1

        while True:
            clientSocket.sendto(packet, (serverName, serverPort))  # Send packet / resend same packet
            try:
                ack_packet, _ = clientSocket.recvfrom(2048)  # Wait for ACK

                # OPTION 2: intentionally corrupt received ACK at sender-side receive path
                ack_packet, injected = maybe_corrupt_ack_at_sender(ack_packet, ack_error_rate)
                if injected:
                    acks_injected += 1

                ptype, ack_seq, _, corrupt = parse_packet(ack_packet)  # analyze ACK

                # if correct ACK received
                if not corrupt and ptype == ACK and ack_seq == seq:
                    seq = 1 - seq  # sequence number toggle
                    break

                # Bad/corrupt/wrong ACK -> resend same DATA packet (RDT 2.2 recovery behavior)
                retransmissions += 1

            except timeout:
                retransmissions += 1
                continue  # resend on timeout

# END packet
endpkt = make_packet(END, seq, b"")

# Send END until correct ACK received
while True:
    clientSocket.sendto(endpkt, (serverName, serverPort))
    try:
        ack_packet, _ = clientSocket.recvfrom(2048)

        # Option 2 injection can also affect ACK for END
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

clientSocket.close()  # close socket
print("Done sending.")
print(f"ACK error rate (sender-side injected): {ack_error_rate}")
print(f"Chunks sent: {chunks_sent}")
print(f"Injected corrupted ACKs: {acks_injected}")
print(f"Retransmissions (bad ACK/wrong ACK/timeout): {retransmissions}")
