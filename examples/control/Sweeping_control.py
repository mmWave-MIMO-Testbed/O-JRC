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
#arc_length = 10  # setting for moving
#speed_user = 0.1
start_time = time.time()
total_time = time.time()
#end_time = arc_length / speed_user *10
end_time = 600
record_flag = 0
crc_flag = 0
test_packet.packet_type = 1   # 1 for NDP 2 for data
test_packet.packet_size = 100
test_radar.est_angle = 0      # beamforming angle of DATA packet
test_radar.est_range = 5        # beamforming range of DATA packet
data_interface.write_radar_data(test_radar, radar_data_path)

while total_time-start_time <= end_time:

     # ES algorithm
    current_time = datetime.now()
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    now_time = time.time()
    #last_data_timestamp = datetime.now() #Self-test
    test_comm = data_interface.load_comm_data(comm_log_path) # Load updated comm data
    #test_radar = data_interface.load_radar_data(radar_log_path) # update radar info
    time_diff = now_time - previous_time

    if test_comm == None: # solve incomplete-writing issue
        #data_interface.write_radar_data(test_radar,radar_data_path)
        data_interface.write_packet_data(test_packet,packet_data_path)
        previous_time = now_time
        print("Loading communication data failed")
        continue

    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]

    if last_data_timestamp != test_comm.timestamp: # record comm SNR
        last_data_timestamp = test_comm.timestamp
        curr_beamforming_angle = test_radar.est_angle
        previous_time = time.time()
        data_interface.write_plot_log(test_packet.packet_type, test_radar.est_angle, curr_beamforming_angle, test_comm.data_snr, test_comm.CRC, test_comm.throughput, plot_log_path)
    elif time_diff >= 0.2:  # Communication time-out
        #last_data_timestamp = current_time
        curr_beamforming_angle = test_radar.est_angle
        previous_time = time.time()
        data_interface.write_plot_log(test_packet.packet_type, test_radar.est_angle, curr_beamforming_angle, -20, 0, test_comm.throughput, plot_log_path)
        previous_time = now_time
        #print("Comm time-out")

    #data_interface.write_radar_data(test_radar, radar_data_path)
    data_interface.write_packet_data(test_packet,packet_data_path)
    time.sleep(0.05)
    total_time = time.time()

# Sweeping algorithm