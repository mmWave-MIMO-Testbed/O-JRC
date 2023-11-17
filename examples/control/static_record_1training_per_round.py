import os
import time
import numpy as np
from scipy import stats
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
plot_log_path_DB     = os.path.join(parent_dir, 'data', 'plot_log_DB.csv')
raw_data_DB = os.path.join(parent_dir, 'data', 'raw_data_DB.csv')
plot_log_path_ES = os.path.join(parent_dir, 'data', 'plot_log_ES.csv')
raw_data_ES = os.path.join(parent_dir, 'data', 'raw_data_ES.csv')
plot_log_path_MAB = os.path.join(parent_dir, 'data', 'plot_log_MAB.csv')
raw_data_MAB = os.path.join(parent_dir, 'data', 'raw_data_MAB.csv')

radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')

X_data_path    = os.path.join(parent_dir, 'data', 'X_data.csv')
Y_data_path    = os.path.join(parent_dir, 'data', 'Y_data.csv')
mean_data_path    = os.path.join(parent_dir, 'data', 'mean_data.csv')
variance_data_path    = os.path.join(parent_dir, 'data', 'variance_data.csv')


# Testing
current_time = '22:10:39.001'
peak_power = 0.0239202
snr_est = 23
range_val = 5.10998
angle_val = -55.599
packet_type = 1 # 1 for NDP, 2 for Data
packet_size = 100
test_packet_type = 1


#create radar_data
test_radar = data_interface.RadarData(current_time, peak_power, snr_est, range_val, angle_val)

#create comm_data
test_comm = data_interface.CommData(current_time, 0, packet_type, snr_est, snr_est, 1, 0,0)

#create packet_data
test_packet = data_interface.PacketData(current_time, packet_type, packet_size)


last_timestamp = None
last_data_timestamp = None
radar_data_array = []
snr_array = []
data_array = []
mode_variable = None
ave_snr = None
ndp_flag = 0
data_flag = 0
round_flag = 0

# Start NDP for radar position
print("Start recording")    
time.sleep(10)
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

current_time = datetime.now()
test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]  

while ndp_flag <= 30:
    test_packet.packet_type = 1
    test_packet.packet_size = 7
    test_radar = data_interface.load_radar_data(radar_log_path)

    if test_radar == None:
        data_interface.write_packet_data(test_packet,packet_data_path)
        continue

    current_time = datetime.now()
    #last_timestamp = datetime.now() # self-test
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]

    if last_timestamp != test_radar.timestamp: # record radar angle
        ndp_flag += 1
        last_timestamp = test_radar.timestamp
        radar_data_array.append(test_radar.est_angle)

    data_interface.write_radar_data(test_radar, radar_data_path)  
    data_interface.write_packet_data(test_packet,packet_data_path)
    time.sleep(0.01)

mode_variable = stats.mode(radar_data_array)[0]

# If given angle
# 0, 4.573, 9.134, 13.675, 18.189, 22.667, 27.1, 31.471, 35.761
#mode_variable = -35.761

print(f"the mode of the angle is: {mode_variable}")
# training the model

n_radar_angle = 181 # one degree resolution
n_beamforming_angle = 121 # one degree resolution
agent = CMAB_algorithm.ContextualUCB(n_radar_angle,n_beamforming_angle)
pre_comm_time = 0
curr_radar_angle = int(np.round(mode_variable))
curr_beamforming_angle = -60
training_flag = 0
previous_time = time.time()

print("Start training")
while training_flag < 1000: # train the model for 1000 times
    test_packet.packet_type = 2
    test_packet.packet_size = 300
    #print(f"current beamforming angle is: {curr_beamforming_angle}")
    current_time = datetime.now()
    now_time = time.time()
    #last_data_timestamp = datetime.now() # self test
    test_comm = data_interface.load_comm_data(comm_log_path)
    time_diff = now_time - previous_time

    if test_comm == None:
        data_interface.write_radar_data(test_radar,radar_data_path)
        data_interface.write_packet_data(test_packet,packet_data_path)
        previous_time = time.time()
        continue

    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]

        
    if pre_comm_time != test_comm.timestamp: #new and comm information updated     
        # udpate PER throughput reward data
        curr_comm_reward = test_comm.reward_val
        curr_comm_per = test_comm.per_val
        curr_comm_throughput = test_comm.throughput
        curr_comm_snr = test_comm.data_snr
        reward = curr_comm_reward * (1/(1+(np.exp(-0.9*(curr_comm_snr-17)))))
        #print(f"reward: {reward},beamforming angle: {curr_beamforming_angle}")
            
        agent.update(curr_radar_angle+90,curr_beamforming_angle+60,reward) # update reward for last decision
        curr_beamforming_angle = int(agent.angle_selection(curr_radar_angle + 90))
        test_radar.est_angle = curr_beamforming_angle
        pre_comm_time = test_comm.timestamp
        previous_time = time.time()
        training_flag += 1
                
        #if ucb_count == 100: # save ucb every 100 round
        #    agent.save_ucb_info()
        #    agent.save_mean_info()
        #    agent.save_trained_model()
        #    ucb_count = 0

    elif time_diff >= 0.1:
        agent.update(curr_radar_angle+90,curr_beamforming_angle+60,0)
        curr_beamforming_angle = int(agent.angle_selection(curr_radar_angle + 90))
        test_radar.est_angle = curr_beamforming_angle
        pre_comm_time = time.time()
        previous_time = time.time()
        training_flag += 1

    data_interface.write_radar_data(test_radar,radar_data_path)
    data_interface.write_packet_data(test_packet,packet_data_path)
    time.sleep(0.01)

print("Finish Training")



while round_flag < 10:

    # ES algorithm
    if round_flag < 2:
        print("Start record ES method")
        test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
        angle_bin = -60 # from -60 to 60 degree
        previous_time = time.time()

        while angle_bin <= 60:
            while data_flag < 10:
                test_packet.packet_type = 2
                test_packet.packet_size = 300
                current_time = datetime.now()
                now_time = time.time()
                #last_data_timestamp = datetime.now() #Self-test
                test_comm = data_interface.load_comm_data(comm_log_path)
                time_diff = now_time - previous_time

                if test_comm == None:
                    data_interface.write_radar_data(test_radar,radar_data_path)
                    data_interface.write_packet_data(test_packet,packet_data_path)
                    previous_time = time.time()
                    continue

                test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]

                if last_data_timestamp != test_comm.timestamp and test_comm.CRC == 1: # record comm SNR
                    data_flag += 1
                    last_data_timestamp = test_comm.timestamp
                    snr_array.append(test_comm.data_snr)

                    curr_comm_reward = test_comm.reward_val
                    curr_comm_per = test_comm.per_val
                    curr_comm_throughput = test_comm.throughput
                    curr_comm_snr = test_comm.data_snr
                    reward = curr_comm_reward * (1/(1+(np.exp(-0.9*(curr_comm_snr-17)))))
                    curr_beamforming_angle = angle_bin
                    agent.update(curr_radar_angle+90,curr_beamforming_angle+60,reward) # update reward for last decision
                    
                    data_interface.write_plot_log(2, mode_variable, angle_bin, test_comm.data_snr, test_comm.CRC, test_comm.throughput, raw_data_ES)
                    previous_time = time.time()
                elif time_diff >= 0.1:
                    data_flag += 1
                    #last_data_timestamp = current_time
                    snr_array.append(0) # SNR=0 for time-out
                    curr_beamforming_angle = angle_bin
                    agent.update(curr_radar_angle+90,curr_beamforming_angle+60,0) # update reward for last decision
                    data_interface.write_plot_log(2, mode_variable, angle_bin, 0, 1, test_comm.throughput, raw_data_ES)
                    previous_time = time.time()
                    print("Comm time-out")

                test_radar.est_angle = angle_bin
                data_interface.write_radar_data(test_radar, radar_data_path)
                data_interface.write_packet_data(test_packet,packet_data_path)
                time.sleep(0.01)
            
            ave_snr = np.mean(snr_array)
            print(f"the average SNR of ES is: {ave_snr}, beamforming angle is: {test_radar.est_angle}")
            data_interface.write_plot_log(2, mode_variable, angle_bin, ave_snr, test_comm.CRC, test_comm.throughput, plot_log_path_ES)

            data_flag = 0
            angle_bin += 1
            snr_array.clear()

    print("Finish ES algorithm, go to DB method")
    data_flag = 0
    snr_array.clear()
    previous_time = time.time()
    
    # DB algorithm

    while data_flag < 10:
        test_packet.packet_type = 2
        test_packet.packet_size = 300
        test_radar.est_angle = np.round(mode_variable)
        current_time = datetime.now()
        now_time = time.time()
        #last_data_timestamp = datetime.now() # self test
        test_comm = data_interface.load_comm_data(comm_log_path)
        time_diff = now_time - previous_time

        if test_comm == None:
            data_interface.write_radar_data(test_radar,radar_data_path)
            data_interface.write_packet_data(test_packet,packet_data_path)
            previous_time = time.time()
            continue

        test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]

        if last_data_timestamp != test_comm.timestamp and test_comm.CRC == 1: # record comm SNR
            data_flag += 1
            last_data_timestamp = test_comm.timestamp
            snr_array.append(test_comm.data_snr)
            data_interface.write_plot_log(2, mode_variable, mode_variable, test_comm.data_snr, test_comm.CRC, test_comm.throughput, raw_data_DB)
            previous_time = time.time()
        elif time_diff >= 0.2: # 1 second time out
            data_flag += 1
            #last_data_timestamp = current_time
            snr_array.append(0) # time-out for 0 SNR
            data_interface.write_plot_log(2, mode_variable, mode_variable, 0, 1, test_comm.throughput, raw_data_DB)
            previous_time = time.time()
            print("Comm time-out")

        data_interface.write_radar_data(test_radar, radar_data_path)
        data_interface.write_packet_data(test_packet,packet_data_path)
        time.sleep(0.01)
        
    ave_snr = np.mean(snr_array)
    print(f"the average SNR of DB is: {ave_snr}, beamforming angle is: {test_radar.est_angle}")
    data_interface.write_plot_log(2, mode_variable, mode_variable, ave_snr, test_comm.CRC, test_comm.throughput, plot_log_path_DB)
    data_flag = 0
    snr_array.clear()
    print("Finish DB method, go to MAB mthod")

    # MAB algorithm 

    while data_flag < 10: 
        test_packet.packet_type = 2
        test_packet.packet_size = 300
        curr_beamforming_angle = int(agent.angle_selection(curr_radar_angle + 90))
        test_radar.est_angle = curr_beamforming_angle
        current_time = datetime.now()
        now_time = time.time()
        #last_data_timestamp = datetime.now() #self test
        test_comm = data_interface.load_comm_data(comm_log_path)
        time_diff = now_time - previous_time

        if test_comm == None:
            data_interface.write_radar_data(test_radar,radar_data_path)
            data_interface.write_packet_data(test_packet,packet_data_path)
            previous_time = time.time()
            continue

        test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]

        if last_data_timestamp != test_comm.timestamp and test_comm.CRC ==1 : # record comm SNR
            data_flag += 1
            last_data_timestamp = test_comm.timestamp
            snr_array.append(test_comm.data_snr)
            # udpate PER throughput reward data
            curr_comm_reward = test_comm.reward_val
            curr_comm_per = test_comm.per_val
            curr_comm_throughput = test_comm.throughput
            curr_comm_snr = test_comm.data_snr
            reward = curr_comm_reward * (1/(1+(np.exp(-0.9*(curr_comm_snr-17)))))
            #print(f"reward: {reward}")        
            agent.update(curr_radar_angle+90,curr_beamforming_angle+60,reward) # update reward for last decision
            data_interface.write_plot_log(2, mode_variable, curr_beamforming_angle, test_comm.data_snr, test_comm.CRC, test_comm.throughput, raw_data_MAB)
            previous_time = time.time()
        elif time_diff >= 0.2: # 1 second time out
            data_flag += 1
            #last_data_timestamp = current_time
            snr_array.append(0) # time-out for 0 SNR
            agent.update(curr_radar_angle+90,curr_beamforming_angle+60,0) # update reward for last decision
            data_interface.write_plot_log(2, mode_variable, curr_beamforming_angle, 0, 1, test_comm.throughput, raw_data_MAB)
            previous_time = time.time()
            print("Comm time-out")

        data_interface.write_radar_data(test_radar, radar_data_path)
        data_interface.write_packet_data(test_packet,packet_data_path)
        time.sleep(0.01)
        
    ave_snr = np.mean(snr_array)
    print(f"the average SNR of MAB is: {ave_snr}, beamforming angle is: {test_radar.est_angle}")
    data_interface.write_plot_log(2, mode_variable, curr_beamforming_angle, ave_snr, test_comm.CRC, test_comm.throughput, plot_log_path_MAB)
    data_flag = 0
    print(f"Finish MAB method. Finish, go to next round {round_flag+1}")
    
    ndp_flag = 0
    radar_data_array.clear()
    snr_array.clear()
    round_flag += 1

agent.save_trained_model(X_data_path, Y_data_path)
agent.save_mean_variance(mean_data_path, variance_data_path)
print("This angle is finished. Go to next angle")

