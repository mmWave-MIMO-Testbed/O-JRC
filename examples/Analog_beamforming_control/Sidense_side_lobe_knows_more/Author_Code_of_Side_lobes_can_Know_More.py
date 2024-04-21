"""
File Name: Author_Code_of_Side_lobes_can_Know_More.py
Author: Authors of 'Side lobes can Know More' paper
Date: 01/26/2024

Description:
- This code starts with sivers as a Tx and another as a Rx and beamsweep through all the beams and for each Tx beam it receives all the Rx beams and saves the data in a file with the names of the Tx beam angle.
- Configures the USRP device for reception.
- Configures the sivers receiver and stores the received signals in 'output.dat'.
- Uses multi-threading to connect to the USRP receiver and sivers.


Usage:
- This is the code recieved from the authors of 'Side lobes can Know More' paper.
"""

import argparse
import sys
import time
import threading
import numpy as np
import uhd
import matplotlib.pyplot as pl
import multiprocessing as mp


import uhd_conf as ucf


sample_size=3928   ## 3328 is for one preamble, 600 zero padding, 500-{3328}-100
CLOCK_TIMEOUT = 1000  # 1000mS timeout for external clock locking
INIT_DELAY = 0.08  # 1S initial delay before transmit
# sweep_num = 10 # beam sweep round


fname='test.dat' # Output file

##load payload from file 
filename="11ad_preamble_1frame_500delay.dat"
#specify tx waveform type
with open(filename,"rb") as f:
    transmit_buffer=np.fromfile(f,dtype=np.complex64)
print("Transmit buffer shape: " + str(np.shape(transmit_buffer)))

recv_buffer = np.zeros(sample_size, dtype=np.complex64) 


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("-a", "--args", default="RIO0", type=str, help="single uhd device address args")
    parser.add_argument("--rate", type=float, default=100e6,help="IQ rate(sps) ") 
    parser.add_argument("--gain", type=float, default=0,help="gain") 
    
    return parser.parse_args()

def tx_host(tx_streamer, timer_elapsed_event,transmit_buffer, start_time):
    ## specify the time the tx begin to work.
    metadata = uhd.types.TXMetadata()
    metadata.time_spec  =  uhd.types.TimeSpec(start_time)
    metadata.has_time_spec = True
    while not timer_elapsed_event.is_set():
        tx_streamer.send(transmit_buffer, metadata)    
    # Send a mini EOB packet
    metadata.end_of_burst = True
    tx_streamer.send(np.zeros((1,0), dtype=np.complex64), metadata)


def rx_host(usrp,rx_streamer, event_queue, start_time, recv_queue):
    metadata = uhd.types.RXMetadata()
    # Craft and send the Stream Command
    stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.start_cont)
    stream_cmd.stream_now = False
    stream_cmd.time_spec  =  uhd.types.TimeSpec(start_time)    
    rx_streamer.issue_stream_cmd(stream_cmd)  

    sectorNum = 63 
    tic = time.time()
    for beamID  in range(sectorNum):   # rx beam: tx beam +- 10 entry    
        for i in range(30):        
            rx_streamer.recv(recv_buffer, metadata)   # Wait for beam stablize
        recv_pkt = recv_buffer[0:3928]+0.000
        recv_queue.put(recv_pkt) 
        usrp.set_gpio_attr("FP0", "OUT", BF_INC_rx, BF_INC_rx)     #Point to Tx Rx Next entry                
        usrp.set_gpio_attr("FP0", "OUT", 0, BF_INC_rx)   # The GPIO control nead at least 10ns
    toc = time.time()
    print('data duration:'+str((toc-tic)))
                             
    event_queue.put(0)  
    rx_streamer.issue_stream_cmd(uhd.types.StreamCMD(uhd.types.StreamMode.stop_cont))



## several range bin
def writeData(fname,recv_queue):
    with open(fname,"w") as f:
        while recv_queue.qsize()>0:        
            recv_packet = recv_queue.get(True)      
            recv_packet.tofile(f)
           

def FPGPIO_BIT(x):
    return 1 << x


def main(tx_streamer,rx_streamer):
    recv_queue = mp.Queue()
    event_queue = mp.Queue()
    quit_event = threading.Event()
    # Initialize GPIO control
    usrp.set_gpio_attr("FP0", "CTRL", 1<<0, ATR_MASKS)
    usrp.set_gpio_attr("FP0", "DDR", GPIO_DDR,ATR_MASKS)
    # usrp.set_gpio_attr("FP0", "OUT", BF_RST_tx, BF_RST_tx)
    # usrp.set_gpio_attr("FP0", "OUT", 0, BF_RST_tx)
    usrp.set_gpio_attr("FP0", "OUT", BF_RST_rx, BF_RST_rx)
    usrp.set_gpio_attr("FP0", "OUT", 0, BF_RST_rx)
    time.sleep(0.05)

    start_time =  usrp.get_time_now().get_real_secs() + INIT_DELAY

    ## start tx thread
    tx_process = threading.Thread(target=tx_host,
                                args=(tx_streamer, quit_event, transmit_buffer, start_time))    
    ## start RX thread
    rx_process = threading.Thread(target=rx_host,args=(usrp,rx_streamer, event_queue, start_time, recv_queue))
   
    tx_process.start()
    rx_process.start()

    event = event_queue.get(block=True,timeout=None)   # Rx done event      
    quit_event.set()
    print("Sending signal to stop!")
    tx_process.join()
    rx_process.join()
        
    print("Sending signal to stop!")

    writeData(fname,recv_queue)

    print('Data Processsed')
    recv_queue.close()
    recv_queue.join_thread()
    event_queue.close()
    event_queue.join_thread()
    return True

if __name__ == "__main__":
    BF_RST_rx =FPGPIO_BIT(1)
    BF_RST_tx =FPGPIO_BIT(2)
    BF_INC_rx = FPGPIO_BIT(4)
    BF_INC_tx = FPGPIO_BIT(5)

    ATR_MASKS = (BF_RST_tx|BF_INC_tx|BF_RST_rx|BF_INC_rx)
    GPIO_DDR = (BF_RST_tx|BF_INC_tx|BF_RST_rx|BF_INC_rx)

    args = parse_args()    
    print("..........build......\n")
    tx_streamer,rx_streamer,usrp=ucf.uhd_builder(args.args,args.gain,args.rate)

    print("TX freq:%.3f GHz, IQ rate %.3f Msps, gain:%.1f, ant: %s, bandwidth:%.3f MHz,spb:%d" %(
                usrp.get_tx_freq()/1e9,usrp.get_tx_rate() / 1e6,usrp.get_tx_gain(),usrp.get_tx_antenna(),usrp.get_tx_bandwidth()/1e6,tx_streamer.get_max_num_samps()))
    print("RX freq:%.3f GHz, IQ rate %.3f Msps, gain:%.1f, ant: %s, bandwidth:%.3f MHz,spb:%d" %(
    usrp.get_rx_freq()/1e9,usrp.get_rx_rate() / 1e6,usrp.get_rx_gain(),usrp.get_rx_antenna(),usrp.get_rx_bandwidth()/1e6,rx_streamer.get_max_num_samps()))
    
    
    main(tx_streamer,rx_streamer)

    with open(fname,"rb") as f:
        b=np.fromfile(f,dtype=np.complex64)
    Sabs = np.abs(b)
    pl.figure(figsize=(13,4.5))
    pl.plot(Sabs)
    # pl.plot(b.imag)
    pl.title('Received Signal Strength under different patterns')
    pl.xlabel('Samples')
    pl.ylabel('Amplitude')

    seg_length = 3928
    pattern_num = 63

    x=0
    theta = np.linspace(-45,45,num=pattern_num)
    lineH = np.max(Sabs)+ 0.01  

    for i in range(pattern_num): 
        pl.vlines(x,0,lineH,linestyles = "dashed")
        mark = str('%.1f' % theta[i]) + u"\N{DEGREE SIGN}"
        # mark = str(i)
        # mark = str('%.1f' % theta[pattern_idx[i]]) + u"\N{DEGREE SIGN}"
        # pl.text(x-3828,lineH,mark)
        pl.text(x+100,lineH,mark, rotation = 90)
        x += seg_length -1


    pl.grid(True)
    pl.tight_layout()
    pl.show()

   