import struct
import socket
from enum import Enum

# Define PACKET_TYPE 
class PACKET_TYPE(Enum):
    NDP = 1  # 1 for NDP
    DATA = 2  # 2 for DATS

# Define MAC header structure
def create_mac_header(frame_control, duration, addr1, addr2, addr3, seq_control, beamforming_control):
    addr1_bytes = bytes(addr1)
    addr2_bytes = bytes(addr2)
    addr3_bytes = bytes(addr3)
    mac_header = struct.pack(
        'HH6s6s6sH4s',
        frame_control, 
        duration, 
        addr1_bytes, 
        addr2_bytes, 
        addr3_bytes, 
        seq_control, 
        beamforming_control
    )
    return mac_header

# Create NDP packet，1 for NDP， 3*X for data payload
def create_ndp_packet(mac_header):
    ndp_type = struct.pack('B', PACKET_TYPE.NDP.value)  # First bytpe set as NDP 
    ndp_data = b'X' * 3  # 3 bytes data payload
    return ndp_type + mac_header + ndp_data

# Create DATA packet，2 for DATA， 1024*X for data payload
def create_data_packet(mac_header, data_size=1024):
    data_type = struct.pack('B', PACKET_TYPE.DATA.value)  
    data_packet = b'X' * data_size  # 1024 bytes Data 
    return data_type + mac_header + data_packet

# Send and save packet, convert to char
def send_and_save_packet(packet, udp_port, file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, ("127.0.0.1", udp_port))

    # Save as Hex formate
    file.write(f"Sent packet (hex): {packet.hex()}\n")
    print(f"Sent packet (hex): {packet.hex()}")

    #MAC header (if 30 bytes total)
    payload = packet[30:].decode('utf-8', errors='ignore')  # payload after 30 bytes
    file.write(f"Sent packet (payload as chars): {payload}\n")
    print(f"Sent packet (payload as chars): {payload}")

    sock.close()

# main
if __name__ == "__main__":
    frame_control = 0x0801
    duration = 0x003c
    addr1 = [0x00, 0x11, 0x22, 0x33, 0x44, 0x55]
    addr2 = [0x66, 0x77, 0x88, 0x99, 0xAA, 0xBB]
    addr3 = [0xCC, 0xDD, 0xEE, 0xFF, 0x00, 0x11]
    data_size = 1024
    
    sequence_number = 0
    beamforming_value = 0
    udp_port = 9000

    # Open the file and send out data
    with open('sent_packets.txt', 'w') as file:
        for i in range(5):  # play 5 times
            beamforming_control = struct.pack('4B', beamforming_value, 0, 0, 0)
            mac_header = create_mac_header(frame_control, duration, addr1, addr2, addr3, sequence_number, beamforming_control)

            # NDP packet
            ndp_packet = create_ndp_packet(mac_header)
            send_and_save_packet(ndp_packet, udp_port, file)

            # DATA packet
            data_packet = create_data_packet(mac_header, data_size)
            send_and_save_packet(data_packet, udp_port, file)

            # update sequence number and beamforming control
            sequence_number = (sequence_number + 1) % 65536  # sequence number 2 bytes
            beamforming_value = (beamforming_value + 1) % 64
