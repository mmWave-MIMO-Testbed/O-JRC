import sys
import time
from datetime import datetime
import beamSweep
import os
import numpy as np
import hunter 
#hunter.trace(module='posixpath', action=hunter.CallPrinter)

def write_sivers_log(sivers_angle,sivers_log_path):
   current_time = datetime.now()
   timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
   line = f"{timestamp}, \t{sivers_angle}\n"
   with open(sivers_log_path, 'a') as file:
      file.write(line)

parent_dir = '/home/host-pc/O-JRC/examples'
print(parent_dir)
sivers_angle_path  = os.path.join(parent_dir, 'data', 'sivers_angle_log.csv')

# Sivers angle resolution
sivers_angles = np.arange(-40,41,10)
#every angle maps to 7 index
angle_list = np.repeat(sivers_angles,7)

def get_angle_from_index(index):
   if index < 0 or index >= len(angle_list):
        print("invalid index")   
   return angle_list[index]

process_tx = beamSweep.beamSweep_start(1, "T582306548", "rapvalbsp", None, None, None, None, None, None, "tx_setup_25Ghz")
process_rx = beamSweep.beamSweep_start(2, "T582306549", "rapvalbsp", None, None, None, None, None, None, "rx_setup_25Ghz")
   
if process_tx  is None:
   sys.exit(1)  # Exeit the program if initialization failed

if process_rx is None:
   sys.exit(1)  # Exeit the program if initialization failed

start_beam_index = 4
beam_index = 1
tpol = 'th'
rpol = 'rh'

while beam_index < 63:
    # Format the command string with the current beam_index and tpol
    command_tx = f"host.chip.tx.beam(rap0, {beam_index}, '{tpol}')"
    command_rx = f"host.chip.rx.beam(rap0, {beam_index}, '{rpol}')"
    # inject command to subprocess
    process_tx.update_cmd(command_tx)
    process_rx.update_cmd(command_rx)
    sivers_angle = get_angle_from_index(beam_index)
    write_sivers_log(sivers_angle, sivers_angle_path)
    time.sleep(0.3)  # Sleep to allow processing time between commands
    beam_index += 1
    print(f'Config TX beam index: {beam_index}')
    print(f'beam angle: {sivers_angle}')

ii = 0
loop_index = int(input("Please enter the number of looping"))
beam_index = start_beam_index

while ii < loop_index:
    # Format the command string with the current beam_index and tpol
    command_tx = f"host.chip.tx.beam(rap0, {beam_index}, '{tpol}')"
    command_rx = f"host.chip.rx.beam(rap0, {beam_index}, '{rpol}')"
    # inject command to subprocess
    process_tx.update_cmd(command_tx)
    process_rx.update_cmd(command_rx)
    sivers_angle = get_angle_from_index(beam_index)
    write_sivers_log(sivers_angle, sivers_angle_path)
    time.sleep(0.4)  # Sleep to allow processing time between commands
    beam_index += 7
    print(f'Config TX beam index: {beam_index}')
    print(f'beam angle: {sivers_angle}')
    if beam_index >= 63:
        ii += 1
        beam_index = start_beam_index

beam_index = start_beam_index

while beam_index < 100:
   print('The beam index:',beam_index)
   command_tx = f"host.chip.tx.beam(rap0, {beam_index}, '{tpol}')"
   command_rx = f"host.chip.rx.beam(rap0, {beam_index}, '{rpol}')"
   process_tx.update_cmd(command_tx)
   process_rx.update_cmd(command_rx)
   sivers_angle = get_angle_from_index(beam_index)
   write_sivers_log(sivers_angle, sivers_angle_path)
   print(f'beam angle: {sivers_angle}')
   beam_index = int(input("Please enter the beam index: (100 for exit)"))

process_tx.stop()
process_rx.stop()


