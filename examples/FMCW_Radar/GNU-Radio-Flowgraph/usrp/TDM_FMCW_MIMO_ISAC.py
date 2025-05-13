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

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import gr
import sys
import signal
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
        self.tx_gain = tx_gain = 42
        self.samp_rate = samp_rate = int(125e6)
        self.rx_gain = rx_gain = 41
        self.delay_samp = delay_samp = 187+5
        self.chirp_duration = chirp_duration = 1e-3
        self.bandwidth = bandwidth = 125e6
        self.USRP_frequency = USRP_frequency = 4e9
        self.N_tx = N_tx = 4
        self.N_rx = N_rx = 2
        self.N_USRP = N_USRP = 2
        self.FMCW_Generation = FMCW_Generation = True

        ##################################################
        # Blocks
        ##################################################
        self._tx_gain_range = Range(0, 60, 1, 42, 200)
        self._tx_gain_win = RangeWidget(self._tx_gain_range, self.set_tx_gain, 'TX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_gain_win, 0, 0, 1, 3)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = Range(0, 60, 1, 41, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, 'RX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 3, 1, 3)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._delay_samp_range = Range(0, 500, 1, 187+5, 200)
        self._delay_samp_win = RangeWidget(self._delay_samp_range, self.set_delay_samp, 'TX/RX Sync', "counter_slider", float)
        self.top_grid_layout.addWidget(self._delay_samp_win, 8, 0, 1, 8)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            firdes.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            bandwidth, #bw
            "FFT", #name
            1
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.5)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(True)
        self.qtgui_freq_sink_x_0.enable_grid(True)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/host-pc/O-JRC/examples/FMCW_Radar/GNU-Radio-Flowgraph/saved_data/saved_fmcw_io_sample_rx2.dat', False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/host-pc/O-JRC/examples/FMCW_Radar/GNU-Radio-Flowgraph/saved_data/saved_fmcw_io_sample_rx1.dat', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.FMCW_MIMO_TDM_FMCW_Generator_0 = FMCW_MIMO.TDM_FMCW_Generator(samp_rate, bandwidth, chirp_duration, 0.01, N_tx, "packet_len")
        self.FMCW_MIMO_FMCW_MIMO_USRP_0 = FMCW_MIMO.FMCW_MIMO_USRP(N_USRP, N_tx, N_rx, samp_rate, USRP_frequency, delay_samp, False, 0.04, "addr0=192.168.120.2, addr1=192.168.101.2, master_clock_rate=250e6", "external,external", "external,external", "TX/RX,TX/RX,TX/RX,TX/RX", tx_gain, 0.5, 0.01, "", "RX2,RX2", rx_gain, 0.5, 0.01, 0, "", "packet_len")
        # Create the options list
        self._FMCW_Generation_options = [True, False]
        # Create the labels list
        self._FMCW_Generation_labels = ['On', 'OFF']
        # Create the combo box
        self._FMCW_Generation_tool_bar = Qt.QToolBar(self)
        self._FMCW_Generation_tool_bar.addWidget(Qt.QLabel('FMCW_Generation)Switch' + ": "))
        self._FMCW_Generation_combo_box = Qt.QComboBox()
        self._FMCW_Generation_tool_bar.addWidget(self._FMCW_Generation_combo_box)
        for _label in self._FMCW_Generation_labels: self._FMCW_Generation_combo_box.addItem(_label)
        self._FMCW_Generation_callback = lambda i: Qt.QMetaObject.invokeMethod(self._FMCW_Generation_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._FMCW_Generation_options.index(i)))
        self._FMCW_Generation_callback(self.FMCW_Generation)
        self._FMCW_Generation_combo_box.currentIndexChanged.connect(
            lambda i: self.set_FMCW_Generation(self._FMCW_Generation_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._FMCW_Generation_tool_bar)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 1), (self.blocks_file_sink_0_0, 0))
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 3), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 3))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 1), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 1))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 2), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 2))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 0), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0))
        self.connect((self.FMCW_MIMO_TDM_FMCW_Generator_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.qtgui_freq_sink_x_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "TDM_FMCW_MIMO_ISAC")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.FMCW_MIMO_FMCW_MIMO_USRP_0.set_tx_gain(self.tx_gain)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.FMCW_MIMO_FMCW_MIMO_USRP_0.set_rx_gain(self.rx_gain)

    def get_delay_samp(self):
        return self.delay_samp

    def set_delay_samp(self, delay_samp):
        self.delay_samp = delay_samp
        self.FMCW_MIMO_FMCW_MIMO_USRP_0.set_num_delay_samps(self.delay_samp)

    def get_chirp_duration(self):
        return self.chirp_duration

    def set_chirp_duration(self, chirp_duration):
        self.chirp_duration = chirp_duration

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.bandwidth)

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

    def get_FMCW_Generation(self):
        return self.FMCW_Generation

    def set_FMCW_Generation(self, FMCW_Generation):
        self.FMCW_Generation = FMCW_Generation
        self._FMCW_Generation_callback(self.FMCW_Generation)
        self.FMCW_MIMO_TDM_FMCW_Generator_0.set_enabled(self.FMCW_Generation)





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
