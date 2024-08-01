from datetime import datetime
import numpy as np
import time
import os

def write_sivers_log(sivers_angle,sivers_log_path):
   current_time = datetime.now()
   timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
   line = f"{timestamp}, \t{sivers_angle}\n"
   with open(sivers_log_path, 'a') as file:
      file.write(line)


parent_dir = '/home/haocheng/O-JRC/examples'
print(parent_dir)
sivers_angle_path  = os.path.join(parent_dir, 'data', 'sivers_angle_log.csv')

# Sivers angle resolution
sivers_angles = np.arange(-40,41,10)
#every angle maps to 7 index (Sivers beambook setup)
angle_list = np.repeat(sivers_angles,7)

def get_angle_from_index(index):
   if index < 0 or index >= len(angle_list):
        print("invalid index")   
   return angle_list[index]

beam_index = 0
time.sleep(2)

while beam_index < 63:
    # inject command to subprocess
    sivers_angle = get_angle_from_index(beam_index)
    write_sivers_log(sivers_angle, sivers_angle_path)
    time.sleep(0.3)  # Sleep to allow processing time between commands
    beam_index += 1
    print(f'Config TX beam index: {beam_index}')
    print(f'beam angle: {sivers_angle}')