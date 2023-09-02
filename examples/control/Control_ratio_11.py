import os
import time
import random
from datetime import datetime
import data_interface

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)


radar_log_path      = os.path.join(parent_dir, 'data', 'radar_log.csv')
comm_log_path       = os.path.join(parent_dir, 'data', 'comm_log.csv')
packet_log_path     = os.path.join(parent_dir, 'data', 'packet_log.csv')
plot_log_path     = os.path.join(parent_dir, 'data', 'plot_log.csv')

radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')


# Testing
current_time = '22:10:39.001'
peak_power = 0.0239202
snr_est = 23
range_val = 5.10998
angle_val = -55.599
packet_type = 1 # 1 for NDP, 2 for Data
packet_size = 400
test_packet_type = 1


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


while True:

    time.sleep(0.005)

    current_time = datetime.now()
    pre_test_radar = test_radar
    pre_test_comm = test_comm
    test_radar = data_interface.load_radar_data(radar_log_path) # update radar info
    test_comm = data_interface.load_comm_data(comm_log_path) # update comm info
    if test_radar == None:
        test_radar = pre_test_radar
    else:
        pre_test_radar = test_radar

    if test_comm == None:
        test_comm = pre_test_comm
    else:
        pre_test_comm = test_comm
    
    #test_radar_angle = random.uniform(-60,60)
    #test_packet_type = random.randint(1, 2)
    # test_packet_type = 2
    if test_packet_type == 1:
        test_packet_type = 2
    else:
        test_packet_type = 1
    
    test_packet_size = 300
    #test_packet_size = random.randint(10, 300)
    # print(test_radar_angle)
    #print(test_packet_type, test_packet_size,test_radar.est_angle)
    print(test_radar.est_angle)
    #test_radar.est_angle = test_radar_angle
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    test_packet.packet_type = test_packet_type
    test_packet.packet_size = test_packet_size

    data_interface.write_radar_data(test_radar, radar_data_path)
    data_interface.write_radar_log(test_radar, radar_log_path)
    data_interface.write_plot_log(test_comm.packet_type, test_radar.est_angle, test_radar.est_angle, test_comm.data_snr, test_comm.CRC, test_comm.throughput, plot_log_path)

    data_interface.write_packet_data(test_packet, packet_data_path)
    data_interface.write_packet_log(test_packet, packet_log_path)

    #test_comm = data_interface.load_comm_data(comm_log_path)
    #print(test_comm.rx_snr)


 
