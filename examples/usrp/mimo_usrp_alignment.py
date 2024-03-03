#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: MIMO USRP Alignment
# Author: Ceyhun D. Ozkaptan
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
from gnuradio import analog
from gnuradio import blocks
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import cmath
import foo
import mimo_ofdm_jrc
import radar

from gnuradio import qtgui

class mimo_usrp_alignment(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "MIMO USRP Alignment ")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("MIMO USRP Alignment ")
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

        self.settings = Qt.QSettings("GNU Radio", "mimo_usrp_alignment")

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
        self.sine_freq = sine_freq = 100e3
        self.samp_rate = samp_rate = int(125e6)
        self.wait_to_start = wait_to_start = 0.01
        self.usrp_freq = usrp_freq = 5e9
        self.tx_gain = tx_gain = 1
        self.rx_gain = rx_gain = 50
        self.phase_tx4 = phase_tx4 = 0
        self.phase_tx3 = phase_tx3 = 0
        self.phase_tx2 = phase_tx2 = 0
        self.phase_rx2 = phase_rx2 = 0
        self.n_samples = n_samples = int(samp_rate/sine_freq)*4
        self.fft_interp = fft_interp = 8
        self.delay_samp = delay_samp = 100
        self.amp_tx4 = amp_tx4 = 1
        self.amp_tx3 = amp_tx3 = 1
        self.amp_tx2 = amp_tx2 = 1
        self.amp_rx2 = amp_rx2 = 1

        ##################################################
        # Blocks
        ##################################################
        self._tx_gain_range = Range(0, 60, 1, 1, 200)
        self._tx_gain_win = RangeWidget(self._tx_gain_range, self.set_tx_gain, 'TX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_gain_win, 0, 0, 1, 3)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = Range(0, 60, 1, 50, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, 'RX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 3, 1, 3)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_tx4_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, 0, 200)
        self._phase_tx4_win = RangeWidget(self._phase_tx4_range, self.set_phase_tx4, 'TX4 - Phase ', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_tx4_win, 7, 4, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_tx3_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, 0, 200)
        self._phase_tx3_win = RangeWidget(self._phase_tx3_range, self.set_phase_tx3, 'TX3 - Phase ', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_tx3_win, 7, 2, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_tx2_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, 0, 200)
        self._phase_tx2_win = RangeWidget(self._phase_tx2_range, self.set_phase_tx2, 'TX2 - Phase ', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_tx2_win, 7, 0, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_rx2_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, 0, 200)
        self._phase_rx2_win = RangeWidget(self._phase_rx2_range, self.set_phase_rx2, 'RX2 - Phase ', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_rx2_win, 5, 3, 1, 3)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._delay_samp_range = Range(0, 400, 1, 100, 200)
        self._delay_samp_win = RangeWidget(self._delay_samp_range, self.set_delay_samp, 'TX/RX Delay [Samples]', "counter_slider", float)
        self.top_layout.addWidget(self._delay_samp_win)
        self._amp_tx4_range = Range(0, 10, 0.01, 1, 200)
        self._amp_tx4_win = RangeWidget(self._amp_tx4_range, self.set_amp_tx4, 'TX4 - Amp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_tx4_win, 6, 4, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._amp_tx3_range = Range(0, 10, 0.01, 1, 200)
        self._amp_tx3_win = RangeWidget(self._amp_tx3_range, self.set_amp_tx3, 'TX3 - Amp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_tx3_win, 6, 2, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._amp_tx2_range = Range(0, 10, 0.01, 1, 200)
        self._amp_tx2_win = RangeWidget(self._amp_tx2_range, self.set_amp_tx2, 'TX2 - Amp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_tx2_win, 6, 0, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._amp_rx2_range = Range(0, 10, 0.01, 1, 200)
        self._amp_rx2_win = RangeWidget(self._amp_rx2_range, self.set_amp_rx2, 'RX2 - Amp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_rx2_win, 5, 0, 1, 3)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.radar_ts_fft_cc_0_2_0 = radar.ts_fft_cc(n_samples*fft_interp,  "packet_len")
        self.radar_ts_fft_cc_0_2 = radar.ts_fft_cc(n_samples*fft_interp,  "packet_len")
        self.radar_ts_fft_cc_0_2.set_min_output_buffer(40000)
        self.qtgui_time_sink_x_0_1_0 = qtgui.time_sink_f(
            int(n_samples*fft_interp/64), #size
            samp_rate, #samp_rate
            "FFT - RX2", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_1_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1_0.set_y_label('Magnitude', "")

        self.qtgui_time_sink_x_0_1_0.enable_tags(True)
        self.qtgui_time_sink_x_0_1_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_1_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_1_0.enable_grid(True)
        self.qtgui_time_sink_x_0_1_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_1_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [0.6, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_1_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_1_0_win)
        self.qtgui_time_sink_x_0_1 = qtgui.time_sink_f(
            int(n_samples*fft_interp/64), #size
            samp_rate, #samp_rate
            "FFT - RX1", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_1.set_y_label('Magnitude', "")

        self.qtgui_time_sink_x_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_1.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_1.enable_grid(True)
        self.qtgui_time_sink_x_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_1.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [0.6, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_1.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_1_win)
        self.qtgui_time_sink_x_0_0 = qtgui.time_sink_f(
            n_samples, #size
            samp_rate, #samp_rate
            "IMAG", #name
            2 #number of inputs
        )
        self.qtgui_time_sink_x_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0.enable_grid(True)
        self.qtgui_time_sink_x_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0.enable_stem_plot(False)


        labels = ['RX1', 'RX2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 2.0, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [0.6, 0.6, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_win, 4, 0, 1, 6)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            n_samples, #size
            samp_rate, #samp_rate
            "REAL", #name
            2 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(True)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['RX1', 'RX2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [2, 2, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [0.6, 0.6, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_win, 3, 0, 1, 6)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_2 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_2.set_update_time(0.10)
        self.qtgui_number_sink_0_2.set_title("Freq Difference")

        labels = ['RX1-RX2', '', '', '', '',
            '', '', '', '', '']
        units = ['Hz', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_2.set_min(i, 0)
            self.qtgui_number_sink_0_2.set_max(i, 10e6)
            self.qtgui_number_sink_0_2.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_2.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_2.set_label(i, labels[i])
            self.qtgui_number_sink_0_2.set_unit(i, units[i])
            self.qtgui_number_sink_0_2.set_factor(i, factor[i])

        self.qtgui_number_sink_0_2.enable_autoscale(True)
        self._qtgui_number_sink_0_2_win = sip.wrapinstance(self.qtgui_number_sink_0_2.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_2_win, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_1_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_1_0.set_update_time(0.10)
        self.qtgui_number_sink_0_1_0.set_title('Frequency - RX2')

        labels = ['Frequency - RX2', '', '', '', '',
            '', '', '', '', '']
        units = ['Hz', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_1_0.set_min(i, 0)
            self.qtgui_number_sink_0_1_0.set_max(i, 10e6)
            self.qtgui_number_sink_0_1_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_1_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_1_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_1_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_1_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_1_0.enable_autoscale(True)
        self._qtgui_number_sink_0_1_0_win = sip.wrapinstance(self.qtgui_number_sink_0_1_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_1_0_win, 9, 0, 1, 2)
        for r in range(9, 10):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_1 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_1.set_update_time(0.10)
        self.qtgui_number_sink_0_1.set_title("Frequency - RX1")

        labels = [' ', '', '', '', '',
            '', '', '', '', '']
        units = ['Hz', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_1.set_min(i, 0)
            self.qtgui_number_sink_0_1.set_max(i, 10e6)
            self.qtgui_number_sink_0_1.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_1.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_1.set_label(i, labels[i])
            self.qtgui_number_sink_0_1.set_unit(i, units[i])
            self.qtgui_number_sink_0_1.set_factor(i, factor[i])

        self.qtgui_number_sink_0_1.enable_autoscale(True)
        self._qtgui_number_sink_0_1_win = sip.wrapinstance(self.qtgui_number_sink_0_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_1_win, 8, 0, 1, 2)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_0_1_0 = qtgui.number_sink(
            gr.sizeof_float,
            0.5,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_0_1_0.set_update_time(0.10)
        self.qtgui_number_sink_0_0_1_0.set_title("Phase Difference")

        labels = ['RX1-RX2', '', '', '', '',
            '', '', '', '', '']
        units = ['rad', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_0_1_0.set_min(i, 0)
            self.qtgui_number_sink_0_0_1_0.set_max(i, 10e6)
            self.qtgui_number_sink_0_0_1_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0_1_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0_1_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0_1_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0_1_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0_1_0.enable_autoscale(False)
        self._qtgui_number_sink_0_0_1_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0_1_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_0_1_0_win, 2, 4, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_0_0_1_0 = qtgui.number_sink(
            gr.sizeof_float,
            0.5,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_0_0_1_0.set_update_time(0.10)
        self.qtgui_number_sink_0_0_0_1_0.set_title("Magnitude Ratio")

        labels = ['RX1/RX2', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_0_0_1_0.set_min(i, 0)
            self.qtgui_number_sink_0_0_0_1_0.set_max(i, 10e6)
            self.qtgui_number_sink_0_0_0_1_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0_0_1_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0_0_1_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0_0_1_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0_0_1_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0_0_1_0.enable_autoscale(False)
        self._qtgui_number_sink_0_0_0_1_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0_0_1_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_0_0_1_0_win, 2, 2, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_0_0_1 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_0_0_1.set_update_time(0.10)
        self.qtgui_number_sink_0_0_0_1.set_title("Phase - RX2")

        labels = ['Phase - RX2', '', '', '', '',
            '', '', '', '', '']
        units = ['rad', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_0_0_1.set_min(i, 0)
            self.qtgui_number_sink_0_0_0_1.set_max(i, 10e6)
            self.qtgui_number_sink_0_0_0_1.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0_0_1.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0_0_1.set_label(i, labels[i])
            self.qtgui_number_sink_0_0_0_1.set_unit(i, units[i])
            self.qtgui_number_sink_0_0_0_1.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0_0_1.enable_autoscale(False)
        self._qtgui_number_sink_0_0_0_1_win = sip.wrapinstance(self.qtgui_number_sink_0_0_0_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_0_0_1_win, 9, 4, 1, 2)
        for r in range(9, 10):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_0_0_0_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_0_0_0_0.set_update_time(0.10)
        self.qtgui_number_sink_0_0_0_0_0.set_title("Magnitude - RX2")

        labels = ['Mag - RX2', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_0_0_0_0.set_min(i, 0)
            self.qtgui_number_sink_0_0_0_0_0.set_max(i, 10e6)
            self.qtgui_number_sink_0_0_0_0_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0_0_0_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0_0_0_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0_0_0_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0_0_0_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0_0_0_0.enable_autoscale(False)
        self._qtgui_number_sink_0_0_0_0_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_0_0_0_0_win, 9, 2, 1, 2)
        for r in range(9, 10):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_0_0_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_0_0_0.set_update_time(0.10)
        self.qtgui_number_sink_0_0_0_0.set_title("Magnitude - RX1")

        labels = ['RX1', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_0_0_0.set_min(i, 0)
            self.qtgui_number_sink_0_0_0_0.set_max(i, 10e6)
            self.qtgui_number_sink_0_0_0_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0_0_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0_0_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0_0_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0_0_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0_0_0.enable_autoscale(False)
        self._qtgui_number_sink_0_0_0_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_0_0_0_win, 8, 2, 1, 2)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0_0_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0_0_0.set_update_time(0.10)
        self.qtgui_number_sink_0_0_0.set_title("Phase - RX1")

        labels = ['RX1', '', '', '', '',
            '', '', '', '', '']
        units = ['rad', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0_0_0.set_min(i, 0)
            self.qtgui_number_sink_0_0_0.set_max(i, 10e6)
            self.qtgui_number_sink_0_0_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0_0_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0_0_0.set_label(i, labels[i])
            self.qtgui_number_sink_0_0_0.set_unit(i, units[i])
            self.qtgui_number_sink_0_0_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0_0_0.enable_autoscale(False)
        self._qtgui_number_sink_0_0_0_win = sip.wrapinstance(self.qtgui_number_sink_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_number_sink_0_0_0_win, 8, 4, 1, 2)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_number_sink_0 = qtgui.number_sink(
            gr.sizeof_float,
            0,
            qtgui.NUM_GRAPH_NONE,
            1
        )
        self.qtgui_number_sink_0.set_update_time(0.10)
        self.qtgui_number_sink_0.set_title("")

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        units = ['', '', '', '', '',
            '', '', '', '', '']
        colors = [("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"),
            ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black"), ("black", "black")]
        factor = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]

        for i in range(1):
            self.qtgui_number_sink_0.set_min(i, -1)
            self.qtgui_number_sink_0.set_max(i, 1)
            self.qtgui_number_sink_0.set_color(i, colors[i][0], colors[i][1])
            if len(labels[i]) == 0:
                self.qtgui_number_sink_0.set_label(i, "Data {0}".format(i))
            else:
                self.qtgui_number_sink_0.set_label(i, labels[i])
            self.qtgui_number_sink_0.set_unit(i, units[i])
            self.qtgui_number_sink_0.set_factor(i, factor[i])

        self.qtgui_number_sink_0.enable_autoscale(True)
        self._qtgui_number_sink_0_win = sip.wrapinstance(self.qtgui_number_sink_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_number_sink_0_win)
        self.mimo_ofdm_jrc_usrp_mimo_trx_0 = mimo_ofdm_jrc.usrp_mimo_trx(2, 4, 2, samp_rate, usrp_freq, delay_samp, False, 0.05, "addr0=192.168.120.2, addr1=192.168.101.2, master_clock_rate=250e6", "external,external", "external,external", "TX/RX,TX/RX,TX/RX,TX/RX", tx_gain, 0.5, 0.01, "", "RX2,RX2", rx_gain, 0.5, 0.01, 0, "", "packet_len")
        self.mimo_ofdm_jrc_fft_peak_detect_0_0 = mimo_ofdm_jrc.fft_peak_detect(samp_rate, 1.0, -120, 0, [1,1], False, "packet_len")
        self.mimo_ofdm_jrc_fft_peak_detect_0 = mimo_ofdm_jrc.fft_peak_detect(samp_rate, 1.0, -120, 0, [1,1], False, "packet_len")
        self.foo_pad_tagged_stream_0_0 = foo.pad_tagged_stream(n_samples*fft_interp,  "packet_len")
        self.foo_pad_tagged_stream_0 = foo.pad_tagged_stream(n_samples*fft_interp,  "packet_len")
        self.foo_pad_tagged_stream_0.set_min_output_buffer(80000)
        self.blocks_sub_xx_0_0 = blocks.sub_ff(1)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_gr_complex, 1, n_samples, "packet_len")
        self.blocks_multiply_const_vxx_0_0_0_0 = blocks.multiply_const_cc(amp_tx4*cmath.exp(1j*phase_tx4))
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_cc(amp_tx3*cmath.exp(1j*phase_tx3))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(amp_tx2*cmath.exp(1j*phase_tx2))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(amp_rx2*cmath.exp(1j*phase_rx2))
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_complex_to_real_0_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_real_0 = blocks.complex_to_real(1)
        self.blocks_complex_to_mag_0_0_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_mag_0_0 = blocks.complex_to_mag(1)
        self.blocks_complex_to_imag_0_0 = blocks.complex_to_imag(1)
        self.blocks_complex_to_imag_0 = blocks.complex_to_imag(1)
        self.blocks_complex_to_arg_0 = blocks.complex_to_arg(1)
        self.analog_sig_source_x_0_0 = analog.sig_source_c(samp_rate, analog.GR_COS_WAVE, sine_freq, 0.2, 0, 0)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_sig_source_x_0_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_complex_to_arg_0, 0), (self.qtgui_number_sink_0, 0))
        self.connect((self.blocks_complex_to_imag_0, 0), (self.qtgui_time_sink_x_0_0, 1))
        self.connect((self.blocks_complex_to_imag_0_0, 0), (self.qtgui_time_sink_x_0_0, 0))
        self.connect((self.blocks_complex_to_mag_0_0, 0), (self.qtgui_time_sink_x_0_1, 0))
        self.connect((self.blocks_complex_to_mag_0_0_0, 0), (self.qtgui_time_sink_x_0_1_0, 0))
        self.connect((self.blocks_complex_to_real_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_complex_to_real_0_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_divide_xx_0, 0), (self.qtgui_number_sink_0_0_0_1_0, 0))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.blocks_complex_to_arg_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_complex_to_imag_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_complex_to_real_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.foo_pad_tagged_stream_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 2))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 3))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.blocks_multiply_const_vxx_0_0_0_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.qtgui_number_sink_0_0_1_0, 0))
        self.connect((self.blocks_sub_xx_0_0, 0), (self.qtgui_number_sink_0_2, 0))
        self.connect((self.foo_pad_tagged_stream_0, 0), (self.radar_ts_fft_cc_0_2, 0))
        self.connect((self.foo_pad_tagged_stream_0_0, 0), (self.radar_ts_fft_cc_0_2_0, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0, 2), (self.blocks_divide_xx_0, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0, 1), (self.blocks_sub_xx_0, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0, 0), (self.blocks_sub_xx_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0, 1), (self.qtgui_number_sink_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0, 2), (self.qtgui_number_sink_0_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0, 0), (self.qtgui_number_sink_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0_0, 2), (self.blocks_divide_xx_0, 1))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0_0, 1), (self.blocks_sub_xx_0, 1))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0_0, 0), (self.blocks_sub_xx_0_0, 1))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0_0, 2), (self.qtgui_number_sink_0_0_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0_0, 1), (self.qtgui_number_sink_0_0_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_fft_peak_detect_0_0, 0), (self.qtgui_number_sink_0_1_0, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0), (self.blocks_complex_to_imag_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0), (self.blocks_complex_to_real_0, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 1), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0), (self.foo_pad_tagged_stream_0, 0))
        self.connect((self.radar_ts_fft_cc_0_2, 0), (self.blocks_complex_to_mag_0_0, 0))
        self.connect((self.radar_ts_fft_cc_0_2, 0), (self.mimo_ofdm_jrc_fft_peak_detect_0, 0))
        self.connect((self.radar_ts_fft_cc_0_2_0, 0), (self.blocks_complex_to_mag_0_0_0, 0))
        self.connect((self.radar_ts_fft_cc_0_2_0, 0), (self.mimo_ofdm_jrc_fft_peak_detect_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mimo_usrp_alignment")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_sine_freq(self):
        return self.sine_freq

    def set_sine_freq(self, sine_freq):
        self.sine_freq = sine_freq
        self.set_n_samples(int(self.samp_rate/self.sine_freq)*4)
        self.analog_sig_source_x_0_0.set_frequency(self.sine_freq)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_n_samples(int(self.samp_rate/self.sine_freq)*4)
        self.analog_sig_source_x_0_0.set_sampling_freq(self.samp_rate)
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_0.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1.set_samp_rate(self.samp_rate)
        self.qtgui_time_sink_x_0_1_0.set_samp_rate(self.samp_rate)

    def get_wait_to_start(self):
        return self.wait_to_start

    def set_wait_to_start(self, wait_to_start):
        self.wait_to_start = wait_to_start

    def get_usrp_freq(self):
        return self.usrp_freq

    def set_usrp_freq(self, usrp_freq):
        self.usrp_freq = usrp_freq

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_tx_gain(self.tx_gain)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_rx_gain(self.rx_gain)

    def get_phase_tx4(self):
        return self.phase_tx4

    def set_phase_tx4(self, phase_tx4):
        self.phase_tx4 = phase_tx4
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.amp_tx4*cmath.exp(1j*self.phase_tx4))

    def get_phase_tx3(self):
        return self.phase_tx3

    def set_phase_tx3(self, phase_tx3):
        self.phase_tx3 = phase_tx3
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.amp_tx3*cmath.exp(1j*self.phase_tx3))

    def get_phase_tx2(self):
        return self.phase_tx2

    def set_phase_tx2(self, phase_tx2):
        self.phase_tx2 = phase_tx2
        self.blocks_multiply_const_vxx_0_0.set_k(self.amp_tx2*cmath.exp(1j*self.phase_tx2))

    def get_phase_rx2(self):
        return self.phase_rx2

    def set_phase_rx2(self, phase_rx2):
        self.phase_rx2 = phase_rx2
        self.blocks_multiply_const_vxx_0.set_k(self.amp_rx2*cmath.exp(1j*self.phase_rx2))

    def get_n_samples(self):
        return self.n_samples

    def set_n_samples(self, n_samples):
        self.n_samples = n_samples
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.n_samples)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.n_samples)

    def get_fft_interp(self):
        return self.fft_interp

    def set_fft_interp(self, fft_interp):
        self.fft_interp = fft_interp

    def get_delay_samp(self):
        return self.delay_samp

    def set_delay_samp(self, delay_samp):
        self.delay_samp = delay_samp
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_num_delay_samps(self.delay_samp)

    def get_amp_tx4(self):
        return self.amp_tx4

    def set_amp_tx4(self, amp_tx4):
        self.amp_tx4 = amp_tx4
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.amp_tx4*cmath.exp(1j*self.phase_tx4))

    def get_amp_tx3(self):
        return self.amp_tx3

    def set_amp_tx3(self, amp_tx3):
        self.amp_tx3 = amp_tx3
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.amp_tx3*cmath.exp(1j*self.phase_tx3))

    def get_amp_tx2(self):
        return self.amp_tx2

    def set_amp_tx2(self, amp_tx2):
        self.amp_tx2 = amp_tx2
        self.blocks_multiply_const_vxx_0_0.set_k(self.amp_tx2*cmath.exp(1j*self.phase_tx2))

    def get_amp_rx2(self):
        return self.amp_rx2

    def set_amp_rx2(self, amp_rx2):
        self.amp_rx2 = amp_rx2
        self.blocks_multiply_const_vxx_0.set_k(self.amp_rx2*cmath.exp(1j*self.phase_rx2))





def main(top_block_cls=mimo_usrp_alignment, options=None):

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
