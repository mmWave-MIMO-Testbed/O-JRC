import csv
import torch
import torch.nn as nn
import torch.nn.functional as F

# define two structure 
class RadarData:
    def __init__(self, timestamp, peak_power, est_snr, est_range, est_angle):
        self.timestamp  = timestamp
        self.peak_power = float(peak_power)
        self.est_snr    = float(est_snr)
        self.est_range  = float(est_range)
        self.est_angle  = float(est_angle)

class CommData:
    def __init__(self, timestamp, CRC, packet_type, est_snr, data_snr, reward_val, per_val,throughput):
        self.timestamp = timestamp
        self.CRC = int(CRC)
        self.packet_type = int(packet_type)
        self.est_snr = float(est_snr)
        self.data_snr = float(data_snr)
        self.reward_val = float(reward_val)
        self.per_val = float(per_val)
        self.throughput = float(throughput)

class PacketData:
    def __init__(self, timestamp, packet_type, packet_size):
        self.timestamp = timestamp
        self.packet_type =   int(packet_type)
        self.packet_size =   int(packet_size)


class CSIClassifier(nn.Module):
    def __init__(self):
        super(CSIClassifier, self).__init__()
        # 输入通道为2，即相位和幅度
        self.conv1 = nn.Conv2d(2, 16, (3, 5), padding=(1, 2))  # 考虑到高度较小，使用更大的宽度卷积核
        self.pool1 = nn.MaxPool2d((2, 1))  # 针对高度进行池化，不改变宽度
        self.conv2 = nn.Conv2d(16, 32, (3, 5), padding=(1, 2))
        self.pool2 = nn.MaxPool2d((2, 1))
        self.conv3 = nn.Conv2d(32, 64, (3, 5), padding=(1, 2))
        self.pool3 = nn.MaxPool2d((2, 1))
        
        # 计算池化后的尺寸，假设每次池化后高度减半
        # 假设经过三次池化，高度变为1，宽度保持64
        self.to_linear = 64 * 64  # 更新全连接层的输入尺寸
        self.fc1 = nn.Linear(self.to_linear, 128)
        self.fc2 = nn.Linear(128, 64)  # 输出层：64种标签

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool1(x)
        x = F.relu(self.conv2(x))
        x = self.pool2(x)
        x = F.relu(self.conv3(x))
        x = self.pool3(x)
        x = x.view(-1, self.to_linear)  # 展平
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

def load_radar_data(radar_log_path):
    with open(radar_log_path,'r') as radar_file:
        radar_log = radar_file.readlines()
    last_line_data = radar_log[-1]
    curr_radar_data = last_line_data.split(",")
    curr_radar_data = [data.strip() for data in curr_radar_data]
    if len(curr_radar_data) >= 5:  # check curr_radar_data length
        radar_data = RadarData(*curr_radar_data)
        return radar_data
    else:
        print("Warning: No enough data to update RadarData")
        return None  

def load_comm_data(comm_log_path):
    with open(comm_log_path,'r') as comm_file:
        comm_log = comm_file.readlines()
    last_line_comm = comm_log[-1]
    curr_comm_data = last_line_comm.split(",")
    curr_comm_data = [data.strip() for data in curr_comm_data]
    if len(curr_comm_data) >= 8:
        comm_data = CommData(*curr_comm_data[:8]) #load first 8 comm data
        return comm_data
    else:
        print("Warning: No enough data to update CommData")
        return None

def load_packet_data(packet_log_path):
    with open(packet_log_path,'r') as packet_file:
        packet_log = packet_file.readlines()
    last_line_data = packet_log[-1]
    curr_packet_data = last_line_data.split(",")
    curr_packet_data = [data.strip() for data in curr_packet_data]
    if len(curr_packet_data >=3 ):
        packet_data = PacketData(*curr_packet_data)
        return packet_data
    else:
        print("Warning: No enough data to update PacketData")
        return None


def write_packet_data(packet_data, packet_data_path):
    line = f"{packet_data.timestamp}, \t{packet_data.packet_type}, \t{packet_data.packet_size}\n"
    with open(packet_data_path, 'w') as file:
        file.write(line)    

def write_packet_log(packet_data,packet_log_path):
    line = f"{packet_data.timestamp}, \t{packet_data.packet_type}, \t{packet_data.packet_size}\n"
    with open(packet_log_path, 'a') as file:
        file.write(line)
                

def write_radar_data(radar_data,radar_data_path):
    line =f"{radar_data.timestamp}, \t{radar_data.peak_power}, \t{radar_data.est_snr}, \t{radar_data.est_range}, \t{radar_data.est_angle}\n"
    with open(radar_data_path, 'w') as file:
        file.write(line)    


def write_radar_log(radar_data,radar_log_path):
    line = f"{radar_data.timestamp}, \t{radar_data.peak_power}, \t{radar_data.est_snr}, \t{radar_data.est_range}, \t{radar_data.est_angle}\n"
    with open(radar_log_path, 'a') as file:
        file.write(line)

def write_plot_log(packet_type, radar_angle, beamforming_angle, data_snr, CRC, throughput, plot_log_path):
    line = f"{packet_type}, \t{radar_angle}, \t{beamforming_angle}, \t{data_snr}, \t{CRC}, \t{throughput}\n"
    with open(plot_log_path,'a') as file:
        file.write(line)



   


