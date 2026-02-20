import struct
import zlib

DATA = 0  #data packet type
ACK = 1   #ack packet type
END = 2   #end transfer packet type

HEADER_FMT = "!BBHI"  
HEADER_LEN = struct.calcsize(HEADER_FMT) #header size

def compute_checksum(data_bytes):
    return zlib.crc32(data_bytes) & 0xffffffff #crc32 checksum

def make_packet(ptype, seq, payload=b""):
    length = len(payload)  #payload size
    checksum = 0  #start up checksum
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)  #build header
    checksum = compute_checksum(header + payload)  #compute checksum
    header = struct.pack(HEADER_FMT, ptype, seq, length, checksum)  #makes header with checksum
    return header + payload  #return full packet

def parse_packet(packet_bytes):
    header = packet_bytes[:HEADER_LEN]#takes header
    payload = packet_bytes[HEADER_LEN:] #takes payload

    ptype, seq, length, checksum = struct.unpack(HEADER_FMT, header) #open header

    header_zero = struct.pack(HEADER_FMT, ptype, seq, length, 0) #zero checksum
    calc_checksum = compute_checksum(header_zero + payload)  #check the checksum

    corrupt = (calc_checksum != checksum)#check corruption

    return ptype, seq, payload, corrupt #return values