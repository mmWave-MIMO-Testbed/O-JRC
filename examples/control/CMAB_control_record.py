import os
import time
import numpy as np
from datetime import datetime
import data_interface
import CMAB_algorithm

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


n_radar_angle = 181 # one degree resolution
n_beamforming_angle = 121 # one degree resolution
agent = CMAB_algorithm.ContextualUCB(n_radar_angle,n_beamforming_angle)

#Load trained model if needed
trained_model_mean = np.load('estimated_mean.npy')
trained_total_play = np.load('total_play.npy')
trained_action_play = np.load('context_action_play.npy')
agent.load_trained_model(trained_model_mean, trained_total_play, trained_action_play)
curr_beamforming_angle = -60
curr_radar_angle = -60

print("Start recording")    
time.sleep(10)
previous_time = time.time()
arc_length = 2 * np.pi
speed_user = 0.5
start_time = time.time()
total_time = time.time()
end_time = arc_length / speed_user

while total_time-start_time <= end_time:

    time.sleep(0.015)
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

    if test_packet_type == 1:
        test_packet_type = 2

    if test_packet_type == 2 and test_comm.CRC == 0:
        test_packet_type = 1

    if test_comm == None:
        test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
        test_packet.packet_size = packet_size
        data_interface.write_radar_data(test_radar,radar_data_path)
        data_interface.write_packet_data(test_packet,packet_data_path)
        continue
    
    #print(test_radar.est_angle)
    #test_radar.est_angle = test_radar_angle
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    test_packet.packet_type = test_packet_type
    test_packet.packet_size = packet_size

    if last_data_timestamp != test_comm.timestamp: # record comm SNR
        
        last_data_timestamp = test_comm.timestamp
        curr_comm_reward = test_comm.reward_val
        curr_comm_snr = test_comm.data_snr
        reward = curr_comm_reward * (1 / (1 + (np.exp(-0.8 * (curr_comm_snr - 20)))))
        #print(f"reward: {reward}")
        if test_comm.packet_type == 2: # update only for data packet
            agent.update(curr_radar_angle+90,curr_beamforming_angle+90,reward) # update reward for last decision

        data_interface.write_plot_log(test_comm.packet_type, test_radar.est_angle, curr_beamforming_angle, test_comm.data_snr, test_comm.CRC, test_comm.throughput, plot_log_path)
        previous_time = now_time
        #print(f"the average SNR of DB is: {test_comm.data_snr}, beamforming angle is: {test_radar.est_angle}")
    elif time_diff >= 0.02: # 1 second time out
        #last_data_timestamp = current_time
        if test_comm.packet_type == 2: # update only for data packet
            agent.update(curr_radar_angle+90,curr_beamforming_angle+90,0) # update reward for last decision
        data_interface.write_plot_log(test_comm.packet_type, test_radar.est_angle, curr_beamforming_angle, 0, 0, test_comm.throughput, plot_log_path)
        previous_time = now_time
        print("Comm time-out")
        print(f"the average SNR of DB is: 0, beamforming angle is: {test_radar.est_angle}")

    curr_radar_angle = int(np.round(test_radar.est_angle)) #angle input for C-MAB
    curr_beamforming_angle = int(agent.angle_selection(curr_radar_angle + 90)) # beamforming angle decision from MAB
    test_radar.est_angle = curr_beamforming_angle

    data_interface.write_radar_data(test_radar, radar_data_path)
    #data_interface.write_radar_log(test_radar, radar_log_path)
    data_interface.write_packet_data(test_packet, packet_data_path)
    #data_interface.write_packet_log(test_packet, packet_log_path)
    total_time = time.time()

# DB algorithm
print("Finish")
agent.save_trained_model()
trained_model_mean = np.load('estimated_mean.npy')
print(f"Trained model: {trained_model_mean}")