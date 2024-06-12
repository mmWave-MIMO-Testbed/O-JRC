"""
Copyright (c) 2024 The Ohio State University
All rights reserved.

This example script, Packet Generation, introduces new users to the control and management of packet type, size, and interval in the JRC system. The script demonstrates how to dynamically adjust these parameters to simulate realistic network traffic.

Packet Generation (Common):
The JRC platform accommodates data from a wide variety of applications. The data flow enters the system through a Socket / PDU (Protocol Data Unit), which converts it into UDP (User Datagram Protocol) packets, referred to as data packets. In parallel, the NDP (Null Data Packet) generator serves a similar function but generates a UDP packet without a payload.

The Packet Scheduler coordinates the scheduling of NDPs and data packets. Following instructions retrieved from the data repository, the scheduler significantly improves resource utilization and performance metrics by harmonizing three key parameters:

1. Packet Type: This parameter enables the selection of data packet or NDP for transmission.
2. Packet Length: This parameter allows the control layer to dictate data packet sizes, influencing several key performance metrics such as throughput, latency, network congestion, reliability, and power.
3. Packet Interval: This parameter allows the control layer to regulate the time interval between packet generations, impacting several performance metrics including throughput, latency, network congestion, channel utilization, and quality of service.
"""

import os
import time
from datetime import datetime
import random
import data_interface

# Get the current file path and parent directory path
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)

# Set the data file path
packet_data_path = os.path.join(parent_dir, 'data', 'packet_data.csv')
print("Packet Data File Path:", packet_data_path)

# Define initial parameters
initial_time = '22:10:39.001'
packet_type = 1  # 1 for NDP, 2 for Data
packet_length = 300

# Create a PacketData object
test_packet = data_interface.PacketData(initial_time, packet_type, packet_length)

# Define functions to generate random types, intervals and lengths
def random_type():
    return random.choice([1, 2])  # 1 for NDP, 2 for Data

def random_length(min_length=100, max_length=1000):
    return random.randint(min_length, max_length)

def random_interval(min_interval=0.5, max_interval=2.0):
    return random.uniform(min_interval, max_interval)

# Start loop to send packets
while True:
    current_time = datetime.now()
    test_packet.timestamp = current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    
    # Randomly set the packet type
    test_packet.packet_type = random_type()
    
    # Set the packet length based on the type
    if test_packet.packet_type == 1:
        test_packet.packet_length = 0  # NDP length should be 0
    else:
        test_packet.packet_length = random_length()  # Random length for Data packet


    print(f"Timestamp: {test_packet.timestamp}, Type: {'NDP' if test_packet.packet_type == 1 else 'Data'}, Length: {test_packet.packet_length}")
    
    # Write data
    data_interface.write_packet_data(test_packet, packet_data_path)
    
    # Randomly adjust the packet interval
    packet_interval = random_interval()
    time.sleep(packet_interval)