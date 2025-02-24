#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: FMCW_Simulation
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
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
import pmt
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import cmath

from gnuradio import qtgui

class FMCW_Sim(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "FMCW_Simulation")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("FMCW_Simulation")
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

        self.settings = Qt.QSettings("GNU Radio", "FMCW_Sim")

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
        self.bandwidth = bandwidth = 125e6
        self.amplitude = amplitude = 2
        self.USRP_frequency = USRP_frequency = 4e9
        self.SweepTime = SweepTime = 1e-5

        ##################################################
        # Blocks
        ##################################################
        self.uhd_usrp_source_0_0 = uhd.usrp_source(
            ",".join(("addr=192.168.120.2,master_clock_rate=250e6", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0_0.set_subdev_spec("A:0", 0)
        self.uhd_usrp_source_0_0.set_time_source('external', 0)
        self.uhd_usrp_source_0_0.set_clock_source('external', 0)
        self.uhd_usrp_source_0_0.set_center_freq(USRP_frequency, 0)
        self.uhd_usrp_source_0_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0_0.set_bandwidth(bandwidth, 0)
        self.uhd_usrp_source_0_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.uhd_usrp_source_0_0.set_min_output_buffer(24000)
        self.uhd_usrp_sink_1 = uhd.usrp_sink(
            ",".join(("addr0=192.168.120.2, master_clock_rate=250e6", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.uhd_usrp_sink_1.set_subdev_spec("A:0 B:0", 0)
        self.uhd_usrp_sink_1.set_time_source('external', 0)
        self.uhd_usrp_sink_1.set_clock_source('external', 0)
        self.uhd_usrp_sink_1.set_center_freq(USRP_frequency, 0)
        self.uhd_usrp_sink_1.set_gain(tx_gain, 0)
        self.uhd_usrp_sink_1.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_1.set_bandwidth(bandwidth, 0)
        self.uhd_usrp_sink_1.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.uhd_usrp_sink_1.set_min_output_buffer(24000)
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
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/host-pc/O-JRC/examples/simulation/radar/fmcw_chirp.dat', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0.set_min_output_buffer(24000)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_file_source_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.uhd_usrp_sink_1, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "FMCW_Sim")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.uhd_usrp_sink_1.set_gain(self.tx_gain, 0)
        self.uhd_usrp_sink_1.set_gain(self.tx_gain, 1)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.uhd_usrp_sink_1.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0_0.set_gain(self.rx_gain, 0)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.bandwidth)
        self.uhd_usrp_sink_1.set_bandwidth(self.bandwidth, 0)
        self.uhd_usrp_sink_1.set_bandwidth(self.bandwidth, 1)
        self.uhd_usrp_source_0_0.set_bandwidth(self.bandwidth, 0)

    def get_amplitude(self):
        return self.amplitude

    def set_amplitude(self, amplitude):
        self.amplitude = amplitude

    def get_USRP_frequency(self):
        return self.USRP_frequency

    def set_USRP_frequency(self, USRP_frequency):
        self.USRP_frequency = USRP_frequency
        self.uhd_usrp_sink_1.set_center_freq(self.USRP_frequency, 0)
        self.uhd_usrp_sink_1.set_center_freq(self.USRP_frequency, 1)
        self.uhd_usrp_source_0_0.set_center_freq(self.USRP_frequency, 0)

    def get_SweepTime(self):
        return self.SweepTime

    def set_SweepTime(self, SweepTime):
        self.SweepTime = SweepTime





def main(top_block_cls=FMCW_Sim, options=None):

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
