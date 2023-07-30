import os
import time
import random
from datetime import datetime
import data_interface

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)

# Testing
current_time = '22:10:39.001'
peak_power = 0.0239202
snr_est = 23
range_val = 5.10998
angle_val = -55.599
packet_type = 1 # 0 for NDP, 1 for Data
packet_size = 100

radar_log_path      = os.path.join(parent_dir, 'data', 'radar_log.csv')
comm_log_path       = os.path.join(parent_dir, 'data', 'comm_log.csv')
packet_log_path     = os.path.join(parent_dir, 'data', 'packet_log.csv')

radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')

#load data from radar_data
test_radar = data_interface.RadarData(current_time, peak_power, snr_est, range_val, angle_val)
# test_radar = data_interface.load_radar_data(radar_log_path)
# print(test_radar.est_angle)


# load data from comm_data
test_comm = data_interface.CommData(current_time, 0, packet_type, snr_est, snr_est, 34.3, 2.3)
test_comm = data_interface.load_comm_data(comm_log_path)
print(test_comm.per_val)

# load data from packet_data
test_packet = data_interface.PacketData(current_time, packet_type, packet_size)
# test_packet = data_interface.load_packet_data(packet_log_path)
# print(test_packet.packet_size)


while True:
    for _ in range(10):
        time.sleep(0.01)
    current_time = datetime.now()
    test_radar_angle = random.uniform(-60,60)
    test_packet_type = random.randint(1, 2)
    test_packet_size = random.randint(100, 500)
    print(test_radar_angle)
    print(test_packet_type)
    print(test_packet_size)
    test_radar.est_angle = test_radar_angle
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    test_packet.packet_type = test_packet_type
    test_packet.packet_size = test_packet_size

    data_interface.write_radar_data(test_radar, radar_data_path)
    data_interface.write_radar_log(test_radar, radar_log_path)

    data_interface.write_packet_data(test_packet, packet_data_path)
    data_interface.write_packet_log(test_packet, packet_log_path)


 
