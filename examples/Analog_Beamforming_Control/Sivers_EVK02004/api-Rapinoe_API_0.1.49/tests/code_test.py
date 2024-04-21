import time
import threading
import numpy as np
import matplotlib.pyplot as plt
import multiprocessing as mp
import uhd
import os
import Sivers_Plot_Tx_Rx_Heatmaps as heatmap

# Create a directory to store the plots
os.makedirs('beam_plots', exist_ok=True)

child_rx = None
child_tx = None

sample_size=3928   ## 3328 is for one preamble, 600 zero padding, 500-{3328}-100
CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking
INIT_DELAY = 0.08  # 1S initial delay before transmit

recv_signal = np.zeros(sample_size, dtype=np.complex64)  # Received signal buffer


#This function calculates the power metrics for the received signal and returns the IQ power in dBm, 
#average power in dBm and maximum power in dBm
def calculate_power_metrics(complex_signal):
    # Extract the I and Q components from the complex signal
    I = complex_signal.real
    Q = complex_signal.imag
    
    # Calculate IQ magnitude for each sample in millivolts (mV) for each sample
    IQ_magnitude = np.sqrt(I**2 + Q**2)
    
    # Calculate IQ power for each sample in milliwatts (mW) for each sample
    IQ_power_mW = (IQ_magnitude**2) / 50.0
    
    # Convert the power values to dBm for each sample
    IQ_power_dBm = 10 * np.log10(IQ_power_mW) + 7 # 7 is the calibration value
    
    # Calculate average and maximum power in dBm for the whole complex signal
    avg_power_dBm = np.mean(IQ_power_dBm)
    max_power_dBm = np.max(IQ_power_dBm)
    
    return IQ_power_dBm,avg_power_dBm, max_power_dBm


#This is a fancy write data that writes for every Tx Angle
def writeData(fname, recv_queue):
    with open(fname, "wb") as f:  # Ensure file is opened in binary write mode ("wb")
        while recv_queue.qsize() > 0:
            recv_packet = recv_queue.get(True)
            np.array(recv_packet).tofile(f)  # Ensure recv_packet is a NumPy array before writing to file


# Receiver setting
def rx_host(usrp, rx_streamer, event_queue, start_time, recv_queue, child_rx, child_tx):
    metadata = uhd.types.RXMetadata()

    # Craft and send the Stream Command
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.stream_now = False
    stream_cmd.time_spec = uhd.types.TimeSpec(start_time)
    rx_streamer.issue_stream_cmd(stream_cmd)

    sectorNum = 63  # Set to the number of beam angles (0 to 63)

    for tx_beam in range(sectorNum + 1):  # Iterate over tx_beam from 0 to 63
        # Set the tx_beam angle
        host.chip.tx.beam(child_tx, tx_beam, tpol) # Switch the TX beam to index: tx_beam
        tic = time.time()  # Record start time for data acquisition

        # Iterate the sivers Rx beams for each angle :
        for rx_beam in range(sectorNum + 1):  # Iterate over rx_beam from 0 to 63
            # Set the rx_beam angle
            host.chip.rx.beam(child_rx,rx_beam, rpol) # Switch the RX beam to index: rx_beam

            for i in range(30):  # Allow beam to stabilize
                rx_streamer.recv(recv_signal, metadata)

            recv_pkt = recv_signal[0:3928] + 0.000
            IQ_power_dBm,avg_power_dBm, max_power_dBm = calculate_power_metrics(recv_pkt) 
            print(max_power_dBm)
            # Enqueue received signal data for each Rx angle
            recv_queue.put(recv_pkt)  


        toc = time.time()  # Record end time for data acquisition
        print('data duration:' + str((toc - tic)))

        # Save the data from recv_queue to a file
        filename = 'tx_beam_angle_{}.dat'.format(tx_beam)
        writeData(filename, recv_queue)


        print("--------- Plotting and Saving for Tx Beam ------------------  ")
        print(" ")
        print("Setting Next Tx Beam ..... ", tx_beam+1)

    event_queue.put(0)
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))




#---------------------------------------------------------------------
# TO-DO: modify this part, init RX and Tx devices.
#---------------------------------------------------------------------

def main(tx_streamer,rx_streamer):
    recv_queue = mp.Queue()
    event_queue = mp.Queue()
    quit_event = threading.Event()

    '''
    Start the sivers Transmitter
    '''
    print("Sivers Transmitter Initializing .....")
    # Spawn the interactive command
    child_tx = pexpect.spawn('sh ../start.sh')

    # Open a log file in binary write mode
    logfile_tx = open("logfile_tx.txt", "wb")

    # Set the logfile attribute of the child object
    child_tx.logfile = logfile_tx

    # Wait for the mode selection
    child_tx.expect('Enter mode (TX/RX): ')
    child_tx.sendline('TX')

    # Wait for the password prompt, and send the password
    child_tx.expect('\[sudo\] password for cpn: ')
    child_tx.sendline('1221')
    print('Sent password.')
    tx_gain = 'tx_bb_gain'
    # # Enable the transmitter
    # run_interactive_command(child_tx, 'eder.tx.init(0x1fffff)')
    # run_interactive_command(child_tx, 'eder.tx.setup(60.48e9, beam=32, trx_tx_on=0x1fffff)')
    # run_interactive_command(child_tx, 'eder.tx.enable()')
    # run_interactive_command(child_tx, 'eder.regs.wr(\'tx_bb_gain\',0x03)')
    # run_interactive_command(child_tx, 'eder.regs.wr(\'tx_bb_iq_gain\',0xFF)')
    # run_interactive_command(child_tx, 'eder.regs.wr(\'tx_bfrf_gain\',0xFF)')

    run_interactive_command(child_tx, 'eder.init()')
    run_interactive_command(child_tx, 'eder.tx_setup(60.48e9)')
    run_interactive_command(child_tx, 'eder.tx_enable()')
    run_interactive_command(child_tx, 'eder.regs.wr(\'tx_bb_gain\',0x03)')
    run_interactive_command(child_tx, 'eder.regs.wr(\'tx_bb_iq_gain\',0xFF)')
    run_interactive_command(child_tx, 'eder.regs.wr(\'tx_bfrf_gain\',0xFF)')


    print(" ")
    print("Sivers Transmitter device started .....")
    print(" ")
    
    time.sleep(1)

    
    '''
    Start the sivers Reciever
    '''
    print("Sivers Reciever Initializing .....")
    # Spawn the interactive command
    child_rx = pexpect.spawn('./start.sh SNSP210141')

    # Open a log file in binary write mode
    logfile_rx = open("logfile_rx.txt", "wb")

    # Set the logfile attribute of the child object
    child_rx.logfile = logfile_rx

    # Wait for the password prompt, and send the password
    child_rx.expect('\[sudo\] password for cpn: ')
    child_rx.sendline('vuran0909')
    print('Sent password.')

    # Enable the receiver

    run_interactive_command(child_rx, 'eder.init()')
    run_interactive_command(child_rx, 'eder.rx_setup(60.48e9)')
    run_interactive_command(child_rx, 'eder.rx_enable()')
    run_interactive_command(child_rx, 'eder.regs.wr(\'rx_gain_ctrl_bfrf\',0xFF)')
    # run_interactive_command(child_rx, 'eder.regs.wr(\'rx_gain_ctrl_bb1\',0xFF)')
    # run_interactive_command(child_rx, 'eder.regs.wr(\'rx_gain_ctrl_bb2\',0x77)')
    # run_interactive_command(child_rx, 'eder.regs.wr(\'rx_gain_ctrl_bb3\',0xFF)')
    # run_interactive_command(child_rx, 'eder.regs.wr(\'agc_int_bfrf_gain_lvl\',0xFFFFFFFF)')
    # run_interactive_command(child_rx, 'eder.regs.wr(\'agc_int_bb3_gain_lvl\',0xFFFFFF)')

    print(" ")
    print("Sivers Reciever device started .....")
    print(" ")
    
    time.sleep(2)
    


    start_time =  usrp.get_time_now().get_real_secs() + INIT_DELAY


    ## start RX thread
    rx_process = threading.Thread(target=rx_host,args=(usrp,rx_streamer, event_queue, start_time, recv_queue,child_rx, child_tx))
   

    rx_process.start()

    event = event_queue.get(block=True,timeout=None)   # Rx done event      
    quit_event.set()
    print("Sending signal to stop! ........ ")

    rx_process.join()
    

    # writeData(fname,recv_queue)

    print('Data Receiving Done ..... ')
    
    recv_queue.close()
    recv_queue.join_thread()
    event_queue.close()
    event_queue.join_thread()

    # Disable the receiver and the transmitter
    print(" ")
    print(" Disabling the sivers reciever and the transmitter.....")
    run_interactive_command(child_rx, 'eder.rx_disable()')
    run_interactive_command(child_tx, 'eder.tx_disable()')
    print(" ")

    # Close the log file
    logfile_rx.close()
    logfile_tx.close()
    print('Log files closed.')    

    return True









#---------------------------------------------
#--------Start the sivers Receiver------------
#---------------------------------------------


#---------------------------------------------
#-----------Choose Low IF or BB mode----------
#---------------------------------------------

mode   = 'BB' # IF = Low IF mode, BB = baseband/zero IF mode
pol1    = 'V'
pol2    = 'H'
rpol   = 'rh' #rv = vertical pol, rh = horizontal pol, rvrh = dual pol

#---------------------------------------------
#-----------Initialize EVK device-------------
#---------------------------------------------

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
host.chip.init(rap0, 'RX', printit=False)

#---------------------------------------------
#------Synth setup with freq_rff--------------
#---------------------------------------------

freq_rff = 24e9 # LO frequency. The script is for IF mode. So RF will be IF freq + freq_rff
host.chip.synth.setup(rap0)
host.chip.synth.set(rap0,freq_rff, frac_mode=True, sd_order=2, printit=True)
host.chip.ram.fill(rap0, '24GHz') # Loads beam for 24GHz from file to RAM. Depending on the RF value a different beambook should be loaded

#---------------------------------------------
#------Beamforming Configuration--------------
#---------------------------------------------

#Enabling 16 elements on V pol
host.chip.rx.setup(rap0, mode, rpol, ant_en_v=0x0000, ant_en_h=0xFFFF)# for H pol or dual pol write appropriate values for ant_en_h. 0xFFFF is for all 16 paths (each bit is for one path). for ex, if you want just one path write 0x0001.

#setting up the RFIC in Rx mode and choosing the required gain and beam indices. Check the 'ram.xml' file @C:\Sivers Semiconductors\Rapinoe\API\config\ram for more details
host.chip.trx.mode(rap0,rpol)
host.chip.rx.beam(rap0, 5, rpol)
host.chip.rx.gain(rap0, 0, rpol)

#calibrating for H and V pol separately
#host.chip.rx.dco.calibrate(rap0, pol1, 0) # calibrating the V pol.
host.chip.rx.dco.calibrate(rap0, pol2, 0)# uncomment this cmd and comment the line above if H pol is used or uncomment both lines if dual pol is used (two DCO calibrations are needed then)

time.sleep(5)  # Wait for sometime to complete RX setting
#------------------------------------------
#---------------------test-----------------
#------------------------------------------
print('Set the rx gain')
#settings for Rx gain
# H pol
lna_gain_h = 12
bf_gain_h = 54
com_gain_h = 54
host.chip.ram.wr(rap0, 'rx_ram_h', 0, (lna_gain_h<<61)+(bf_gain_h<<55)+(com_gain_h<<49))
host.chip.rx.gain(rap0, 0, 'rh')
host.chip.rx.dco.calibrate(rap0, pol2, 0)
print('Complete setting rx gain')
