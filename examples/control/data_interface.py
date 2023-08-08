import csv

# define two structure 
class RadarData:
    def __init__(self, timestamp, peak_power, est_snr, est_range, est_angle):
        self.timestamp  = timestamp
        self.peak_power = float(peak_power)
        self.est_snr    = float(est_snr)
        self.est_range  = float(est_range)
        self.est_angle  = float(est_angle)

class CommData:
    def __init__(self, timestamp, CRC, packet_type, est_snr, rx_snr, reward, per_val,throughput):
        self.timestamp = timestamp
        self.CRC = int(CRC)
        self.packet_type = int(packet_type)
        self.est_snr = float(est_snr)
        self.rx_snr = float(rx_snr)
        self.reward = float(reward)
        self.per_val = float(per_val)
        self.throughput = float(throughput)

class PacketData:
    def __init__(self, timestamp, packet_type, packet_size):
        self.timestamp = timestamp
        self.packet_type =   int(packet_type)
        self.packet_size =   int(packet_size)


def load_radar_data(radar_log_path):
    with open(radar_log_path,'r') as radar_file:
        radar_log = radar_file.readlines()
    last_line_data = radar_log[-1]
    curr_radar_data = last_line_data.split(",")
    curr_radar_data = [data.strip() for data in curr_radar_data]
    radar_data = RadarData(*curr_radar_data)
    return radar_data

def load_comm_data(comm_log_path):
    with open(comm_log_path,'r') as comm_file:
        comm_log = comm_file.readlines()
    last_line_comm = comm_log[-1]
    curr_comm_data = last_line_comm.split(",")
    curr_comm_data = [data.strip() for data in curr_comm_data]
    comm_data = CommData(*curr_comm_data[:8]) #load first 8 comm data
    return comm_data

def load_packet_data(packet_log_path):
    with open(packet_log_path,'r') as packet_file:
        packet_log = packet_file.readlines()
    last_line_data = packet_log[-1]
    curr_packet_data = last_line_data.split(",")
    curr_packet_data = [data.strip() for data in curr_packet_data]
    packet_data = PacketData(*curr_packet_data)
    return packet_data


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





   


