
from gnuradio import uhd as gnu_uhd
import uhd
import time

import logging


from distutils.version import StrictVersion



def uhd_builder(args="",gain=55,rate=500e3,otw="sc16",cpu="fc32"):
    # init usrp
    usrp=uhd.usrp.MultiUSRP(",".join(("serial=32A036E", "dboard_clock_rate=20e6")))

    print("USRP Creating .... ")
    usrp.set_clock_source("internal")
    usrp.set_time_source("internal")
    print("Setting device timestamp to 0...")
    usrp.set_time_now(uhd.types.TimeSpec(0.0))
 
    ## configure RF
    usrp.set_tx_rate(rate)
    usrp.set_tx_gain(0)
    usrp.set_tx_antenna("TX/RX")
    usrp.set_tx_bandwidth(rate)    
    usrp.set_tx_freq(uhd.libpyuhd.types.tune_request(480e6), 0)


    usrp.set_rx_rate(rate)
    usrp.set_rx_gain(0)
    usrp.set_rx_antenna("RX2")
    usrp.set_rx_bandwidth(rate)
    usrp.set_rx_freq(uhd.libpyuhd.types.tune_request(480e6), 0)

    ## extract streamer
    st_args = uhd.usrp.StreamArgs(cpu, otw)
    st_args.channels=[0]
    
    tx_streamer = usrp.get_tx_stream(st_args)
    rx_streamer = usrp.get_rx_stream(st_args)

    print("")
    print(" USRP created .... ")
    return[tx_streamer,rx_streamer,usrp]
