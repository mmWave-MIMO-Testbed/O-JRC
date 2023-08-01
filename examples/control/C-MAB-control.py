#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv
import numpy as np
import os
import time
import random
from datetime import datetime
import data_interface
#import matplotlib as plt

# In[26]:

class ContextualUCB:
    def __init__(self, n_radar_angle, n_beamforming_angle):
        # n_radar_angle: is the total number of angles which can be read from radar (depend on resolution)
        # n_beamformnig_angle: is the total number of angles which will apply to stream encoder  
        self.n_contexts = n_radar_angle
        self.n_actions = n_beamforming_angle
        self.total_plays = 1
        self.context_action_counts = np.ones((n_radar_angle, n_beamforming_angle))
        self.context_action_estimates = np.zeros((n_radar_angle, n_beamforming_angle))

    def get_ucb_value(self, radar_angle):
        ucb_value = self.context_action_estimates[radar_angle, :] + \
                        np.sqrt(2 * np.log(self.total_plays) / (1 + self.context_action_counts[radar_angle, :]))
        return ucb_value
    
    def get_mean_value(self,radar_angle):
        mean_value = self.context_action_estimates[radar_angle,:]
        return mean_value

    def angle_selection(self, radar_angle):
        ucb_value = self.get_ucb_value(radar_angle)
        return np.argmax(ucb_value) - 90 # - 90 to change the range of angle to (-90,90) 

    def update(self, radar_angle, beamforming_angle, reward):
        self.total_plays += 1
        self.context_action_counts[radar_angle, beamforming_angle] += 1 # increment the time of plays
        q_n = self.context_action_estimates[radar_angle, beamforming_angle] # calculate Q(t)value
        n = self.context_action_counts[radar_angle, beamforming_angle] # calculate number of times the arm is played
        self.context_action_estimates[radar_angle, beamforming_angle] += (reward - q_n) / n # update the UCB value
        
    def save_ucb_info(self):
        np.savetxt("ucb_info.csv",self.context_action_estimates,delimiter=',')


# Testing
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)

current_date_time2 = '22:10:39.001'
peak_power = 0.0239202
snr_est = 23
range_val = 5.10998
angle_val = -46.599
radar_log_path = os.path.join(parent_dir, 'data', 'radar_log.csv')
comm_log_path = os.path.join(parent_dir, 'data', 'comm_log.csv')
radar_data_path = os.path.join(parent_dir, 'data','radar_data.csv')
packet_log_path = os.path.join(parent_dir,'data','packet_log.csv')
packet_data_path = os.path.join(parent_dir,'data','packet_data.csv')

test_radar = data_interface.RadarData(current_date_time2, peak_power, snr_est, range_val, angle_val)
test_radar = data_interface.load_radar_data(radar_log_path)
test_packet = data_interface.PacketData(current_date_time2,1,10)
print(test_radar.est_angle)

test_comm = data_interface.CommData(current_date_time2, 0, 1, snr_est, snr_est, 34.3, 2.3,10.0)
test_comm = data_interface.load_comm_data(comm_log_path)
print(test_comm.per_val)

data_interface.write_radar_log(test_radar,radar_log_path)


# In[27]:

# Control algorithm for C-UCB
n_radar_angle = 181 # one degree resolution
n_beamforming_angle = 181 # one degree resolution
agent = ContextualUCB(n_radar_angle,n_beamforming_angle)
pre_radar_time = 0
pre_comm_time = 0
curr_radar_angle = int(np.round(test_radar.est_angle))
curr_beamforming_angle = int(np.round(test_radar.est_angle))
pre_sys_time = time.time()
ucb_count = 0

while True:
        time.sleep(0.1)
        current_sys_time = time.time()
        if current_sys_time - pre_sys_time >= 2: # regular NDP packet
            # Send out NDP
            test_packet.packet_type = 1
            test_packet.packet_size = 10
            current_time = datetime.now()
            test_packet.timestamp = current_time.strftime("%H:%M:%S") + ':'+current_time.strftime("%f")[:3]
            data_interface.write_packet_data(test_packet, packet_data_path)
            data_interface.write_packet_log(test_packet,packet_log_path)
            pre_sys_time = current_sys_time
            print('regular NDP')
            continue
            
        test_radar = data_interface.load_radar_data(radar_log_path) # update radar info
        test_comm = data_interface.load_comm_data(comm_log_path) # update comm info
        
        if pre_radar_time != test_radar.timestamp and pre_comm_time != test_comm.timestamp: #new radar and comm information updated     
            # udpate SNR PER data
            curr_comm_snr = test_comm.snr_val
            curr_comm_per = test_comm.per_val
            reward = curr_comm_snr * (1 - curr_comm_per)
            agent.update(curr_radar_angle+90,curr_beamforming_angle+90,reward) # update reward for last decision
            
            ucb_count += 1
            if ucb_count >= 1000: # save ucb every 1000 round
                agent.save_ucb_info()
                ucb_count = 0
            
            if curr_comm_snr <= 15 or curr_comm_per >= 0.05: # send NDP if lower than threshold
                test_packet.packet_type = 1
                test_packet.packet_size = 10
                current_time = datetime.now()
                test_packet.timestamp = current_time.strftime("%H:%M:%S") + ':'+current_time.strftime("%f")[:3]
                data_interface.write_packet_data(test_packet, packet_data_path)
                data_interface.write_packet_log(test_packet,packet_log_path)
                print("Lower than threshold, send NDP")
                continue
            
            # Send data
            curr_radar_angle = int(np.round(test_radar.est_angle)) #angle input for C-MAB
            pre_radar_time = test_radar.timestamp
            pre_comm_time = test_comm.timestamp
            curr_beamforming_angle = int(agent.angle_selection(curr_radar_angle + 90)) # beamforming angle decision from MAB
            print(f"beamforming angle by C-UCB:{curr_beamforming_angle}")
            # Write to interface
            test_radar.est_angle = curr_beamforming_angle
            current_time = datetime.now()
            test_packet.timestamp = current_time.strftime("%H:%M:%S") + ':'+current_time.strftime("%f")[:3]
            test_radar.timestamp = current_time.strftime("%H:%M:%S") + ':'+current_time.strftime("%f")[:3]
            test_packet.packet_type = 2
            test_packet.packet_size = 300
            data_interface.write_packet_data(test_packet, packet_data_path)
            data_interface.write_packet_log(test_packet,packet_log_path)
            data_interface.write_radar_data(test_radar, radar_data_path)
            data_interface.write_radar_log(test_radar, radar_log_path)
        else: # repeat previous decision
            current_time = datetime.now()
            test_packet.timestamp = current_time.strftime("%H:%M:%S") + ':'+current_time.strftime("%f")[:3]
            data_interface.write_packet_data(test_packet, packet_data_path)
            data_interface.write_packet_log(test_packet,packet_log_path)
            print('repeat previous setting')



# In[29]:

ucb_info = np.loadtxt("ucb_info.csv", delimiter=",")
context_values = np.arange(-90,90,20)
for context in context_values:
    ucb_estimates = ucn_info[context,:]
    plt.plot(range(-90, 91), ucb_estimates, label=f'radar angle{context}')

plt.xlabel('Beamforming angle')
plt.ylabel('UCB Estimate')
plt.title('UCB Estimates for Different Radar angle')
plt.legend()
plt.show()
