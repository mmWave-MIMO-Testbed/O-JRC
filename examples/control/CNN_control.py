import os
import time
import numpy as np
from datetime import datetime
import data_interface
import torch
import re

current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
parent_dir = os.path.dirname(current_dir)
print(parent_dir)


radar_log_path      = os.path.join(parent_dir, 'data', 'radar_log.csv')
comm_log_path       = os.path.join(parent_dir, 'data', 'comm_log.csv')
plot_log_path     = os.path.join(parent_dir, 'data', 'plot_log_Dynamic.csv')

radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')
radar_csi_path      = os.path.join(parent_dir,'data','radar_chan.csv')


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

#load CNN model
model = data_interface.CSIClassifier()
state_dict = torch.load(os.path.join(parent_dir,'control','OJRC_CNN_trained_model.pth'))
model.load_state_dict(state_dict)
model = model.to('cuda')
model.eval() # evaluation mode

def online_decision_making(model, input_data):
    with torch.no_grad(): # disable GD
        input_data = input_data.to('cuda')
        output = model(input_data)
        _,predicted = torch.max(output,1)
    return predicted.item() # return the number of labels


def load_cs_data(full_filename):
    # load the lastline data
    data = np.genfromtxt(full_filename, delimiter=',', dtype=str, skip_header=1, skip_footer=0)

    last_row = data[-1, :]  # get the last line
    num_txrx = 2 
    num_subcarriers = int((len(last_row) / (num_txrx * 2)))
    complex_responses = np.zeros((num_subcarriers, num_txrx), dtype=complex)

    column_index = 0
    for j in range(num_txrx):
        for k in range(num_subcarriers):
            real_part_index = column_index
            imag_part_index = column_index + 1

            if imag_part_index >= last_row.size:
                print(f"Index out of range in file: {full_filename}, row: {len(data)-1}, column: {imag_part_index}")
                continue 

            real_part_match = re.findall(r'[-\d\.]+', last_row[real_part_index])
            imag_part_match = re.findall(r'[-\d\.]+', last_row[imag_part_index])

            if real_part_match and imag_part_match:
                real_part = float(real_part_match[0])
                imag_part = float(imag_part_match[0])
            else:
                continue

            complex_responses[k, j] = complex(real_part, imag_part)
            column_index += 2
    return complex_responses

def preprocess_single_sample(single_sample, transform=None):
    """
    处理单个样本数据，将其转换为 CNN 模型可以使用的输入格式
    """
    # 获取幅度和相位
    magnitude = np.abs(single_sample)
    phase = np.angle(single_sample)
    
    # 如果有需要，可以使用transform进行归一化等处理
    if transform:
        magnitude, phase = transform(magnitude, phase)
    
    # 堆叠形成CNN输入的两个通道
    sample = np.stack([magnitude, phase], axis=0)
    
    # 转换为PyTorch张量，并添加一个batch维度
    sample_tensor = torch.tensor(sample, dtype=torch.float32).unsqueeze(0).to('cuda')  # [1, 2, H, W]
    
    return sample_tensor

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
time.sleep(1)
previous_time = time.time()
arc_length = 3.5
speed_user = 0.01
data_flag = 0
ndp_flag = 0
ndp_count = 0
start_time = time.time()
total_time = time.time()
end_time = arc_length / speed_user *10
end_time = 90

while total_time-start_time <= end_time:

    time.sleep(0.01)
    current_time = datetime.now()
    now_time = time.time()
    pre_test_comm = test_comm
    #test_radar = data_interface.load_radar_data(radar_log_path) # update radar info
    test_comm = data_interface.load_comm_data(comm_log_path) # update comm info
    time_diff = now_time - previous_time

    if test_comm == None: # solve incomplete-writing issue
        test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
        #data_interface.write_radar_data(test_radar,radar_data_path)
        data_interface.write_packet_data(test_packet,packet_data_path)
        previous_time = now_time
        print("Loading communication data failed")
        continue

    #test_radar.est_angle = test_radar_angle
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    test_packet.packet_type = test_packet_type
    test_packet.packet_size = packet_size

    if last_data_timestamp != test_comm.timestamp: # record comm SNR
        last_data_timestamp = test_comm.timestamp
        previous_time = now_time
        
        if ndp_flag == 1 and data_flag <= 20:
            if data_flag == 0: # update every 10 packets
                csi_data = load_cs_data(radar_csi_path)
                input_csi_data = preprocess_single_sample(csi_data)
                predict_angle = online_decision_making(model, input_data=input_csi_data)
                mapping_points = np.linspace(60,-60,28)
                test_radar.est_angle = mapping_points[predict_angle] # map index to angle
                print(f"Send Data packet with angle:{test_radar.est_angle}")
                data_flag += 1
                ndp_count = 0
                test_packet_type = 2
            else:
                test_packet_type = 2
            data_flag += 1
        else:
            if ndp_count == 20:
                test_packet_type = 2
                ndp_flag = 1
                data_flag = 0
            else:
                test_packet_type = 1
                ndp_flag = 0
                ndp_count += 1
            #print("Send NDP")
        data_interface.write_plot_log(test_comm.packet_type, test_radar.est_angle, test_radar.est_angle, test_comm.data_snr, test_comm.CRC, test_comm.throughput, plot_log_path)
       
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

# DB algorithm