"""
File Name: Sivers_Run_Tx_Rx_All_BeamSweep.py
Author: Avhishek Biswas
Date: 01/26/2024

Description:
- This code starts with sivers as a Tx and another as a Rx and beamsweep through all the beams and for each Tx beam it receives all the Rx beams and saves the data in a file with the names of the Tx beam angle.
- Configures the USRP device for reception.
- Configures the sivers receiver and stores the received signals in 'output.dat'.
- Uses multi-threading to connect to the USRP receiver and sivers.

Dependencies:
- argparse: Provides options for command-line arguments.
- sys: Access to some variables used or maintained by the interpreter.
- time: Access to time-related functions.
- threading: Higher-level threading interface.
- numpy: Fundamental package for scientific computing.
- uhd: USRP Hardware Driver for interfacing with the device.
- matplotlib: Plotting library (used for displaying signals).
- multiprocessing: Process-based parallelism.
- pexpect: Controlling and automating applications and launch the sivers reciever with password.
- uhd_conf: Custom module for USRP configuration.

Usage:
- Ensure that the sivers Tx is runnning and it set to a specific beam 
- Run the script with Python 3.7 or later. The script takes no command-line arguments but reads 'input.dat' for the transmit signal and writes the received signal to   'output.dat'.

Notes:
- Modify 'uhd_conf.py' for specific USRP configurations.
- The script assumes the presence of 'start.sh' for Sivers IMA interactions.
- The script assumes the presence of 'selected_beams_single_line.txt' for beam angle selection.

Current Status:
- Tested - works.
"""

import time
import threading
import numpy as np
import uhd
import matplotlib.pyplot as plt
import multiprocessing as mp
import pexpect
import os
import uhd_conf as ucf # import the USRP configuration to start the USRP

import Sivers_Plot_Tx_Rx_Heatmaps as heatmap

# Create a directory to store the plots
os.makedirs('beam_plots', exist_ok=True)

child_rx = None
child_tx = None


sample_size=3928   ## 3328 is for one preamble, 600 zero padding, 500-{3328}-100
CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking
INIT_DELAY = 0.08  # 1S initial delay before transmit


recv_signal = np.zeros(sample_size, dtype=np.complex64)  # Received signal buffer

'''
This function calculates the power metrics for the received signal and returns the IQ power in dBm, average power in dBm and maximum power in dBm
'''
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

'''
This is a fancy write data that writes for every Tx Angle
'''
def writeData(fname, recv_queue):
    with open(fname, "wb") as f:  # Ensure file is opened in binary write mode ("wb")
        while recv_queue.qsize() > 0:
            recv_packet = recv_queue.get(True)
            np.array(recv_packet).tofile(f)  # Ensure recv_packet is a NumPy array before writing to file

def run_interactive_command(child, command):
    try:
        # Wait for the interactive prompt, and send the command
        child.expect('>>>')
        child.sendline(command)
        print('Sending command: {}'.format(command))
    except pexpect.ExceptionPexpect as e:
        print('Failed to run command "{}": {}'.format(command, e))


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
        tx_command = 'eder.tx.set_beam({})'.format(tx_beam)
        print("")
        run_interactive_command(child_tx, tx_command)
        print("")
        tic = time.time()  # Record start time for data acquisition

        # Iterate the sivers Rx beams for each angle :
        for rx_beam in range(sectorNum + 1):  # Iterate over rx_beam from 0 to 63
            # Set the rx_beam angle
            rx_command = 'eder.rx.set_beam({})'.format(rx_beam)
            run_interactive_command(child_rx, rx_command)

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


if __name__ == "__main__":
    # Getting the usrp ready first
    tx_streamer,rx_streamer, usrp = ucf.uhd_builder(args="", gain=76, rate=500e3)

    time.sleep(1)

    # Launching the sivers and the communication process
    main(tx_streamer,rx_streamer)

    '''
    This will plot the heatmap and return the best beam in dBm
    '''
    heatmap.plotheatmap_and_return_best_beam_in_dbm_selected_beam()