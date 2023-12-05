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
peak_power = 0.01
snr_est = 0
range_val = 3
angle_val = 60
packet_type = 1 # 1 for NDP, 2 for Data
packet_size = 300
test_packet_type = 1
last_data_timestamp = None
CRC_flag = 0

#load data from radar_data
test_radar = data_interface.RadarData(current_time, peak_power, snr_est, range_val, angle_val)
# test_radar = data_interface.load_radar_data(radar_log_path)
# print(test_radar.est_angle)


# load data from comm_data
test_comm = data_interface.CommData(current_time, 0, packet_type, snr_est, snr_est, 1, 0,0)
# test_comm = data_interface.load_comm_data(comm_log_path)
# print(test_comm.per_val)

# load data from packet_data
test_packet = data_interface.PacketData(current_time, packet_type, packet_size)
# test_packet = data_interface.load_packet_data(packet_log_path)
# print(test_packet.packet_size)

print("Start recording")    
time.sleep(10)
previous_time = time.time()
arc_length = 3.5
speed_user = 0.01
start_time = time.time()
total_time = time.time()
end_time = arc_length / speed_user *10

while total_time-start_time <= end_time:

    time.sleep(0.01)
    current_time = datetime.now()
    now_time = time.time()
    pre_test_radar = test_radar
    pre_test_comm = test_comm
    test_radar = data_interface.load_radar_data(radar_log_path) # update radar info
    test_comm = data_interface.load_comm_data(comm_log_path) # update comm info
    time_diff = now_time - previous_time
    if test_radar == None:
        test_radar = pre_test_radar
    else:
        pre_test_radar = test_radar


    if test_comm == None:
        test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
        test_packet.packet_size = packet_size
        data_interface.write_radar_data(test_radar,radar_data_path)
        data_interface.write_packet_data(test_packet,packet_data_path)
        previous_time = now_time
        continue
    
    if test_packet_type == 2 and test_comm.CRC == 0:
        test_packet_type = 1
        CRC_flag += 1

    #print(test_radar.est_angle)
    #test_radar.est_angle = test_radar_angle
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    test_packet.packet_type = test_packet_type
    test_packet.packet_size = packet_size

    if last_data_timestamp != test_comm.timestamp: # record comm SNR
        last_data_timestamp = test_comm.timestamp
        data_interface.write_plot_log(test_comm.packet_type, test_radar.est_angle, test_radar.est_angle, test_comm.data_snr, test_comm.CRC, test_comm.throughput, plot_log_path)
        previous_time = now_time
        
        if test_packet_type == 1:
            test_packet_type = 2

        #print(f"the average SNR of DB is: {test_comm.data_snr}, beamforming angle is: {test_radar.est_angle}")
    elif time_diff >= 0.2: # 1 second time out
        #last_data_timestamp = current_time
        data_interface.write_plot_log(test_comm.packet_type, test_radar.est_angle, test_radar.est_angle, 0, 0, test_comm.throughput, plot_log_path)
        previous_time = now_time
        print("Comm time-out")
        print(f"the average SNR of DB is: 0, beamforming angle is: {test_radar.est_angle}")

    data_interface.write_radar_data(test_radar, radar_data_path)
    #data_interface.write_radar_log(test_radar, radar_log_path)
    data_interface.write_packet_data(test_packet, packet_data_path)
    #data_interface.write_packet_log(test_packet, packet_log_path)
    total_time = time.time()

print(f"The CRC flag:{CRC_flag}")
# DB algorithm