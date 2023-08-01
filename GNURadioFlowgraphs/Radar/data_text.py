import time
import random
import data_exchange

# Testing
current_date_time2 = '22:10:39.001'
peak_power = 0.0239202
snr_est = 23
range_val = 5.10998
angle_val = -46.599
radar_file = '/home/haocheng/temp/radar_log.csv'
comm_file = '/home/haocheng/temp/comm_stats.csv'
radar_write_file = '/home/haocheng/temp/radar_read.csv'

#load data from radar_data
test_data = data_exchange.RadarData(current_date_time2, peak_power, snr_est, range_val, angle_val)
test_data = data_exchange.load_from_radar_file(radar_file)
print(test_data.est_angle)

# load data from comm_data
test_comm = data_exchange.CommData(current_date_time2, 0, 1, snr_est, snr_est, 34.3, 2.3)
test_comm = data_exchange.load_from_comm_file(comm_file)
print(test_comm.per_val)

# write data to radar_read
value = random.uniform(-60,60)
while True:
    for _ in range(1):
        time.sleep(1.5)
    value = random.uniform(-60,60)
    print(value)
    test_data.est_angle = value
    data_exchange.write_to_radar_file(test_data,radar_write_file)


 
