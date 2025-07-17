import os
import time
import numpy as np
from datetime import datetime
import data_interface
from collections import deque

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)


radar_log_path      = os.path.join(parent_dir, 'data', 'radar_log.csv')
comm_log_path       = os.path.join(parent_dir, 'data', 'comm_log.csv')
radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')
mcs_data_path       = os.path.join(parent_dir, 'data', 'mcs_ctrl.csv')


# Testing
current_time = '22:10:39.001'
peak_power = 0.01
snr_est = 0
range_val = 3
angle_val = 0 # beamforming angle
packet_type = 2 # 1 for NDP, 2 for Data
packet_size = 300
test_packet_type = 2
last_data_timestamp = None
CRC_flag = 0
mcs_modulation = 1 # 0 and 1for BPSK, 2 and 3 for QPSK, 4 and 5 for 16QAM, start from BPSK

WINDOW_SIZE           = 20
LOWER_THRESH          = 16
UPPER_THRESH          = 18
crc_window = deque(maxlen=WINDOW_SIZE)

#load data from radar_data
test_radar = data_interface.RadarData(current_time, peak_power, snr_est, range_val, angle_val)

# load data from comm_data
test_comm = data_interface.CommData(current_time, 0, packet_type, snr_est, snr_est, 1, 0,0)

# load data from packet_data
test_packet = data_interface.PacketData(current_time, packet_type, packet_size)

# initialize the mcs control
test_mcs = data_interface.MCS_ctrl_data(mcs_modulation)
data_interface.write_mcs_ctrl_data(test_mcs,mcs_data_path)
print(f"[Init] MCS = {mcs_modulation}")

# Fix beamforming angle
data_interface.write_radar_data(test_radar,radar_data_path)

print("Start recording")    
time.sleep(10)
previous_time = time.time()
start_time = time.time()
total_time = time.time()
end_time = 1000 # 1000 seconds for testing

while total_time-start_time <= end_time:

    time.sleep(0.01)
    current_time = datetime.now()
    now_time = time.time()
    test_comm = data_interface.load_comm_data(comm_log_path) # update comm info
    # test_comm.timestamp = current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3] # update timestamp for test
    time_diff = now_time - previous_time

    if test_comm == None:
        test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
        test_packet.packet_size = packet_size
        data_interface.write_packet_data(test_packet,packet_data_path)
        previous_time = now_time
        continue
    
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    test_packet.packet_type = test_packet_type
    test_packet.packet_size = packet_size

    if last_data_timestamp != test_comm.timestamp: # record comm data only when timestamp changes
        last_data_timestamp = test_comm.timestamp
        crc_window.append(test_comm.CRC)
        # mcs_modulation check（when window is full）
        if len(crc_window) == WINDOW_SIZE:
            success_cnt = crc_window.count(1) # count successful packets
            old_mcs = mcs_modulation

            if success_cnt > UPPER_THRESH and mcs_modulation < 5:
                mcs_modulation += 2
            elif success_cnt < LOWER_THRESH and mcs_modulation > 1:
                mcs_modulation -= 2

            if mcs_modulation != old_mcs:
                test_mcs.mcs_type = mcs_modulation
                data_interface.write_mcs_ctrl_data(test_mcs, mcs_data_path)
                print(f"[{datetime.now().isoformat()}] "
                      f"window success={success_cnt}/{WINDOW_SIZE} → "
                      f"MCS {old_mcs}→{mcs_modulation}")
                crc_window.clear()

        previous_time = now_time

    elif time_diff >= 0.2: # 0.2 second time out
        previous_time = now_time
        crc_window.append(0)
        print("Comm time-out")

    data_interface.write_packet_data(test_packet, packet_data_path)
    total_time = time.time()
    time.sleep(0.01)

# mcs_modulation adjustment algorithm