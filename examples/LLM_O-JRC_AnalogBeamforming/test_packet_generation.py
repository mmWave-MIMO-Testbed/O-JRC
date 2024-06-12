import os
import time
from datetime import datetime
import data_interface

# Get the current file path and parent directory path
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)

# Set the data file path
packet_data_path = os.path.join(parent_dir, 'data', 'packet_data.csv')
print("Packet Data File Path:", packet_data_path)

# Create a PacketData object
test_packet = data_interface.PacketData('', 1, 0)

# Function to send packet based on current second
def send_packet():
    current_time = datetime.now()
    current_second = current_time.second
    test_packet.timestamp = current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    
    if current_second % 5 == 0:
        test_packet.packet_type = 1  # NDP
        test_packet.packet_length = 0  # NDP length should be 0
    else:
        test_packet.packet_type = 2  # Data
        test_packet.packet_length = (current_second % 5) * 100  # Data packet length
    
    print(f"Timestamp: {test_packet.timestamp}, Type: {'NDP' if test_packet.packet_type == 1 else 'Data'}, Length: {test_packet.packet_length}")
    
    # Write data
    data_interface.write_packet_data(test_packet, packet_data_path)

# Start loop to send packets
while True:
    send_packet()
    time.sleep(1)  # Wait for 1 second before sending the next packet
