#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: haocheng
# GNU Radio version: v3.8.5.0-6-g57bd109d

from distutils.version import StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import FMCW_MIMO
import cmath

from gnuradio import qtgui

class TDM_FMCW_MIMO_ISAC(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "TDM_FMCW_MIMO_ISAC")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.tx_gain = tx_gain = 50
        self.samp_rate = samp_rate = int(125e6)
        self.rx_gain = rx_gain = 50
        self.delay_samp = delay_samp = 187+5
        self.bandwidth = bandwidth = 125e6
        self.USRP_frequency = USRP_frequency = 4e9
        self.N_tx = N_tx = 4
        self.N_rx = N_rx = 2
        self.N_USRP = N_USRP = 2

        ##################################################
        # Blocks
        ##################################################
        self._delay_samp_range = Range(0, 500, 1, 187+5, 200)
        self._delay_samp_win = RangeWidget(self._delay_samp_range, self.set_delay_samp, 'TX/RX Sync', "counter_slider", float)
        self.top_grid_layout.addWidget(self._delay_samp_win, 8, 0, 1, 8)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/haocheng/O-JRC/examples/FMCW_Radar/GNU-Radio-Flowgraph/saved_data/saved_fmcw_io_sample_rx2.dat', False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/haocheng/O-JRC/examples/FMCW_Radar/GNU-Radio-Flowgraph/saved_data/saved_fmcw_io_sample_rx1.dat', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.FMCW_MIMO_TDM_FMCW_Generator_0 = FMCW_MIMO.TDM_FMCW_Generator(125e6, 125e6, 0.001, 0.005, 4)
        self.FMCW_MIMO_FMCW_MIMO_USRP_0 = FMCW_MIMO.FMCW_MIMO_USRP(N_USRP, N_tx, N_rx, samp_rate, USRP_frequency, delay_samp, False, , "addr0=192.168.1xx.2, addr1=192.168.1xx.2, master_clock_rate=xxxe6", "external,external", "external,external", "TX/RX,TX/RX", , 0.5, 0.01, "", "RX2,RX2", , 0.5, 0.01, 0, "", "packet_len")


        ##################################################
        # Connections
        ##################################################
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 1), (self.blocks_file_sink_0_0, 0))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 1), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 1))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 0), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 3), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 3))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 2), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 2))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "TDM_FMCW_MIMO_ISAC")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain

    def get_delay_samp(self):
        return self.delay_samp

    def set_delay_samp(self, delay_samp):
        self.delay_samp = delay_samp
        self.FMCW_MIMO_FMCW_MIMO_USRP_0.set_num_delay_samps(self.delay_samp)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth

    def get_USRP_frequency(self):
        return self.USRP_frequency

    def set_USRP_frequency(self, USRP_frequency):
        self.USRP_frequency = USRP_frequency

    def get_N_tx(self):
        return self.N_tx

    def set_N_tx(self, N_tx):
        self.N_tx = N_tx

    def get_N_rx(self):
        return self.N_rx

    def set_N_rx(self, N_rx):
        self.N_rx = N_rx

    def get_N_USRP(self):
        return self.N_USRP

    def set_N_USRP(self, N_USRP):
        self.N_USRP = N_USRP





def main(top_block_cls=TDM_FMCW_MIMO_ISAC, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    def quitting():
        tb.stop()
        tb.wait()

    qapp.aboutToQuit.connect(quitting)
    qapp.exec_()

if __name__ == '__main__':
    main()
