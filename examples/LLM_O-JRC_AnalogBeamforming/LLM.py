import os
import time
import numpy as np
from datetime import datetime
import data_interface

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)


radar_log_path      = os.path.join(parent_dir, 'data', 'radar_log.csv')
comm_log_path       = os.path.join(parent_dir, 'data', 'comm_log.csv')
packet_log_path     = os.path.join(parent_dir, 'data', 'packet_log.csv')
plot_log_path     = os.path.join(parent_dir, 'data', 'plot_log_Dynamic.csv')

radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')


# Testing
current_time = '22:10:39.001'
packet_type = 1 # 1 for NDP, 2 for Data
packet_size = 300


# load data from packet_data
test_packet = data_interface.PacketData(current_time, packet_type, packet_size)
# test_packet = data_interface.load_packet_data(packet_log_path)
# print(test_packet.packet_size)


time.sleep(5)

while 1:

    current_time = datetime.now()
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    test_packet.packet_type = 1   # 1 for NDP 2 for data
    test_packet.packet_size = 300

    data_interface.write_packet_data(test_packet,packet_data_path)

    time.sleep(0.005)




