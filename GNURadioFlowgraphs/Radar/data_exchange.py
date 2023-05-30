import csv

# define two structure 
class RadarData:
    def __init__(self, timestamp, peak_power, est_snr, est_range, est_angle):
        self.timestamp = timestamp
        self.peak_power = float(peak_power)
        self.est_snr = float(est_snr)
        self.est_range = float(est_range)
        self.est_angle = float(est_angle)


class CommData:
    def __init__(self, timestamp, CRC, packet_type, est_snr, data_snr, snr_val, per_val):
        self.timestamp = timestamp
        self.CRC = int(CRC)
        self.packet_type = int(packet_type)
        self.est_snr = float(est_snr)
        self.data_snr = float(data_snr)
        self.snr_val = float(snr_val)
        self.per_val = float(per_val)

def write_to_radar_file(radar_data,radar_write_filename):
    line = f"{radar_data.timestamp}, \t{radar_data.peak_power}, \t{radar_data.est_snr}, \t{radar_data.est_range}, \t{radar_data.est_angle}\n"
    with open(radar_write_filename, 'a') as file:
        file.write(line)

def load_from_radar_file(radar_load_filename):
    with open(radar_load_filename,'r') as radar_file:
        read_radar_log = radar_file.readlines()
    last_line_data = read_radar_log[-1]
    curr_radar_data = last_line_data.split(",")
    curr_radar_data = [data.strip() for data in curr_radar_data]
    radar_data = RadarData(*curr_radar_data)
    return radar_data
   
def load_from_comm_file(comm_load_filename):
    with open(comm_load_filename,'r') as comm_file:
        read_comm_log = comm_file.readlines()
    last_line_comm = read_comm_log[-1]
    curr_comm_data = last_line_comm.split(",")
    curr_comm_data = [data.strip() for data in curr_comm_data]
    comm_data = CommData(*curr_comm_data[:7]) #load first 7 comm data
    return comm_data