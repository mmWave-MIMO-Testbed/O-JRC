#Script to setup EVK02004 in Rx Beam Sweep mode
#Author: Haocheng Zhu
#For register config, check 'test_pll_sm_28Ghz.py' for an example. 
#Example: "host.spi.rd(rap0, 'capval_0')", read the value of register "capval_0". 
#         "host.spi.wrrd(rap0, capval_0, 5)" set the value of register "capval_0" to 0x05
#Register map can be found at doc file, 'TRB02801_R5_register_map'

import os
import time
import numpy as np
from datetime import datetime
import data_interface


parent_dir = '/home/host-pc/O-JRC/examples'
print(parent_dir)

radar_log_path      = os.path.join(parent_dir, 'data', 'radar_log.csv')
comm_log_path       = os.path.join(parent_dir, 'data', 'comm_log.csv')
plot_log_path     = os.path.join(parent_dir, 'data', 'plot_log_Dynamic.csv')

radar_data_path     = os.path.join(parent_dir, 'data', 'radar_data.csv')
packet_data_path    = os.path.join(parent_dir, 'data', 'packet_data.csv')


#Choose Low IF or BB mode
mode   = 'BB' # IF = Low IF mode, BB = baseband/zero IF mode
pol1    = 'V'
pol2    = 'H'
tpol   = 'th' #tv = vertical pol, th = horizontal pol, tvth = dual pol


#switch on power domains on the motherboard
host.misc.on(['VCXO', 'PLL'])
host.pwr.on('ALL')

#setup the 245.76 MHz Ref clock on MB2
host.pll.setup()  # Lock the MB2-VCXO to 245.76 MHz
vcxo_freq=host.pll.setup()['vcxo_freq'] #Read back the exact frequency (typically 245759996.9474969 Hz)
host.chip.ref_clk.set(rap0, vcxo_freq) #Set the Rapinoe clock to vcxo_freq.

#RFIC initialisation
host.chip.init(rap0, 'CHIP')
host.chip.init(rap0, 'SYNTH')
host.chip.init(rap0, 'VALIDATION')
host.chip.init(rap0, 'ADC')
host.chip.init(rap0, 'TX', printit=False)

# Synth setup with freq_rff
freq_rff = 25e9 # LO frequency. The script is for IF mode. So RF will be IF freq + freq_rff
host.chip.synth.setup(rap0)
host.chip.synth.set(rap0,freq_rff, frac_mode=True, sd_order=2, printit=True)
host.chip.ram.fill(rap0, '25GHz') # Loads beam for 24GHz from file to RAM. Depending on the RF value a different beambook should be loaded

#Enabling 16 elements on H pol
host.chip.tx.setup(rap0, mode, tpol, ant_en_v=0x0000, ant_en_h=0xFFFF) # for H pol or dual pol write appropriate values for ant_en_h. 0xFFFF is for all 16 paths (each bit is for one path). for ex, if you want just one path write 0x0001. 

#setting up the RFIC in Tx mode and choosing the required gain and beam indices. Check the 'ram.xml' file @C:\Sivers Semiconductors\Rapinoe\API\config\ram for more details
host.chip.trx.mode(rap0,tpol)
host.chip.tx.beam(rap0, 0, tpol)  #Beam begin with index 0
host.chip.tx.gain_rf(rap0, 0, tpol)
host.chip.tx.gain_bb(rap0, 0, 0x1F) #bb_gain(self, dev, bb_v, bb_h)

#calibrating for H and V pol separately
#host.chip.tx.dco.calibrate(rap0, mode, pol1)
host.chip.tx.dco.calibrate(rap0, mode, pol2) # uncomment this cmd and comment the line above if H pol is used or uncomment both lines if dual pol is used (two DCO calibrations are needed then)
time.sleep(5) #Sleep for 5 sec after calibrate


# Begin Sweep Testing
current_time = '22:10:39.001'
peak_power = 0.01
snr_est = 0
range_val = 0
angle_val = 0
packet_type = 1 # 1 for NDP, 2 for Data
packet_size = 300
test_packet_type = 1
last_data_timestamp = None

#Init radar_data
test_radar = data_interface.RadarData(current_time, peak_power, snr_est, range_val, angle_val)

#Init comm_data
test_comm = data_interface.CommData(current_time, 0, packet_type, snr_est, snr_est, 1, 0,0)

#Init packet_data
test_packet = data_interface.PacketData(current_time, packet_type, packet_size)

RX_beam_index = int(input("Please enter the RX beam index:"))
print('The RX beam index:',RX_beam_index)

while (RX_beam_index<=63):    
    RX_beam_index = int(input("Please enter the RX beam index:"))
    print('The RX beam index:',RX_beam_index)

    print("Start recording")    
    previous_time = time.time()
    start_time = time.time()
    total_time = time.time()

    round_time = 10 # 120 sec for each beam index

    record_flag = 0
    crc_flag = 0
    beam_index = 0
    test_packet.packet_type = 1   # 1 for NDP 2 for data
    test_packet.packet_size = 100
    current_time = datetime.now()
    test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
    data_interface.write_radar_data(test_radar, radar_data_path)

    for i in range (64):

        host.chip.tx.beam(rap0, beam_index, tpol)  #Beam begin with index 0
        print('Doing communication with TX beam index: {}, RX beam index:{}'.format(i,RX_beam_index))
        time.sleep(3) # sleep 3 sec for beam switching
        start_time = time.time()
        total_time = time.time()
        previous_time = time.time()
        data_interface.write_packet_data(test_packet,packet_data_path)

        while total_time-start_time <= round_time:

            current_time = datetime.now()
            test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]
            now_time = time.time()
            #last_data_timestamp = datetime.now() #Self-test
            test_comm = data_interface.load_comm_data(comm_log_path) # Load updated comm data
            time_diff = now_time - previous_time

            if test_comm == None: # solve incomplete-writing issue
                data_interface.write_packet_data(test_packet,packet_data_path)
                previous_time = now_time
                print("Loading communication data failed")
                continue

            test_packet.timestamp =  current_time.strftime("%H:%M:%S") + ':' + current_time.strftime("%f")[:3]

            if last_data_timestamp != test_comm.timestamp: # record comm SNR
                last_data_timestamp = test_comm.timestamp
                curr_beamforming_angle = beam_index
                previous_time = time.time()
                data_interface.write_packet_data(test_packet,packet_data_path)
                data_interface.write_plot_log(test_packet.packet_type, RX_beam_index, curr_beamforming_angle, test_comm.data_snr, test_comm.CRC, test_comm.throughput, plot_log_path)
            elif time_diff >= 0.1:  # Communication time-out
                #last_data_timestamp = current_time #self-test
                curr_beamforming_angle = beam_index
                data_interface.write_packet_data(test_packet,packet_data_path)
                data_interface.write_plot_log(test_packet.packet_type, RX_beam_index, curr_beamforming_angle, -10, 0, test_comm.throughput, plot_log_path)
                previous_time = time.time()
                #print("Comm time-out")
            time.sleep(0.001)
            total_time = time.time()
        beam_index += 1
        print('Done with current beam, go next')
print('Sweeping Done')

# Sweeping algorithm
