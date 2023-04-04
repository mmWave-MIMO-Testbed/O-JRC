#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Ofdm Mimo Radar Tx
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
from gnuradio import eng_notation
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio.qtgui import Range, RangeWidget
import cmath
import mimo_ofdm_jrc
import numpy as np
import ofdm_config  # embedded python module
import random
import string

from gnuradio import qtgui

class ofdm_mimo_radar_TX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Ofdm Mimo Radar Tx")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Ofdm Mimo Radar Tx")
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

        self.settings = Qt.QSettings("GNU Radio", "ofdm_mimo_radar_TX")

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
        self.usrp_freq = usrp_freq = 5e9
        self.samp_rate = samp_rate = int(125e6)
        self.rf_freq = rf_freq = usrp_freq+20e9
        self.interp_factor = interp_factor = 8
        self.fft_len = fft_len = ofdm_config.N_sc
        self.R_res = R_res = 3e8/(2*samp_rate)
        self.N_tx = N_tx = ofdm_config.N_tx
        self.N_rx = N_rx = 4
        self.wavelength = wavelength = 3e8/rf_freq
        self.variable_qtgui_label_0 = variable_qtgui_label_0 = R_res
        self.tx_multiplier = tx_multiplier = 0.3
        self.tx_gain = tx_gain = 45
        self.rx_gain = rx_gain = 45
        self.phase_calib_tx2 = phase_calib_tx2 = -3.73
        self.phase_calib_rx2 = phase_calib_rx2 = -1.65
        self.mcs = mcs = 3
        self.delay_samp_1 = delay_samp_1 = 334
        self.cp_len = cp_len = int(fft_len/4)
        self.chan_est_path = chan_est_path = "/home/hostpc-usrp/temp/chan_est.csv"
        self.angle_max = angle_max = np.rad2deg(np.arcsin((N_tx*N_rx*interp_factor-5)/(N_tx*N_rx*interp_factor)))
        self.amp_calib_tx2 = amp_calib_tx2 = 1.83
        self.amp_calib_rx2 = amp_calib_rx2 = 1.63
        self.R_max = R_max = 3e8*fft_len/(2*samp_rate)
        self.N_ltf = N_ltf = ofdm_config.N_ltf

        ##################################################
        # Blocks
        ##################################################
        self._tx_multiplier_range = Range(0.01, 4, 0.01, 0.3, 200)
        self._tx_multiplier_win = RangeWidget(self._tx_multiplier_range, self.set_tx_multiplier, 'TX Multiplier', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_multiplier_win, 0, 4, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._tx_gain_range = Range(0, 60, 1, 45, 200)
        self._tx_gain_win = RangeWidget(self._tx_gain_range, self.set_tx_gain, 'TX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_gain_win, 0, 0, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = Range(0, 60, 1, 45, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, 'RX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 2, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_calib_tx2_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, -3.73, 200)
        self._phase_calib_tx2_win = RangeWidget(self._phase_calib_tx2_range, self.set_phase_calib_tx2, 'Phase Offset TX2', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_calib_tx2_win, 6, 3, 1, 3)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._mcs_options = [0, 1, 2, 3, 4, 5]
        # Create the labels list
        self._mcs_labels = ['BPSK 1/2', 'BPSK 3/4', 'QPSK 1/2', 'QPSK 3/4', '16QAM 1/2', '16QAM 3/4']
        # Create the combo box
        # Create the radio buttons
        self._mcs_group_box = Qt.QGroupBox('Modulation and Coding Scheme' + ": ")
        self._mcs_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._mcs_button_group = variable_chooser_button_group()
        self._mcs_group_box.setLayout(self._mcs_box)
        for i, _label in enumerate(self._mcs_labels):
            radio_button = Qt.QRadioButton(_label)
            self._mcs_box.addWidget(radio_button)
            self._mcs_button_group.addButton(radio_button, i)
        self._mcs_callback = lambda i: Qt.QMetaObject.invokeMethod(self._mcs_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._mcs_options.index(i)))
        self._mcs_callback(self.mcs)
        self._mcs_button_group.buttonClicked[int].connect(
            lambda i: self.set_mcs(self._mcs_options[i]))
        self.top_grid_layout.addWidget(self._mcs_group_box, 2, 0, 1, 6)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._delay_samp_1_range = Range(0, 500, 1, 334, 200)
        self._delay_samp_1_win = RangeWidget(self._delay_samp_1_range, self.set_delay_samp_1, 'TX/RX Delay [Samples]', "counter_slider", float)
        self.top_layout.addWidget(self._delay_samp_1_win)
        self._amp_calib_tx2_range = Range(0, 10, 0.01, 1.83, 200)
        self._amp_calib_tx2_win = RangeWidget(self._amp_calib_tx2_range, self.set_amp_calib_tx2, 'Amplitude Factor TX2', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_calib_tx2_win, 6, 0, 1, 3)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._variable_qtgui_label_0_tool_bar = Qt.QToolBar(self)

        if None:
            self._variable_qtgui_label_0_formatter = None
        else:
            self._variable_qtgui_label_0_formatter = lambda x: eng_notation.num_to_str(x)

        self._variable_qtgui_label_0_tool_bar.addWidget(Qt.QLabel('Range Resolution' + ": "))
        self._variable_qtgui_label_0_label = Qt.QLabel(str(self._variable_qtgui_label_0_formatter(self.variable_qtgui_label_0)))
        self._variable_qtgui_label_0_tool_bar.addWidget(self._variable_qtgui_label_0_label)
        self.top_layout.addWidget(self._variable_qtgui_label_0_tool_bar)
        self.qtgui_time_sink_x_0_0_1_2 = qtgui.time_sink_c(
            (fft_len+cp_len)*15, #size
            1, #samp_rate
            'Signal TX2', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_1_2.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_2.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_1_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_2.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_2.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 200, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_1_2.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_2.enable_grid(True)
        self.qtgui_time_sink_x_0_0_1_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_2.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_2.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [2, 2, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [0.7, 0.7, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_2.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_2.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_2_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_2.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_2_win)
        self.qtgui_time_sink_x_0_0_1_1 = qtgui.time_sink_c(
            (fft_len+cp_len)*15, #size
            1, #samp_rate
            'Signal RX', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_1_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_1_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_1.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_1.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 100, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_1_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_1.enable_grid(True)
        self.qtgui_time_sink_x_0_0_1_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_1.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_1_1_win, 7, 0, 1, 1)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0_0_1_0_0_0 = qtgui.time_sink_c(
            fft_len*13, #size
            1, #samp_rate
            'PRECODER 2', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_1_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_0_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_1_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_0_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_1_0_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_0_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_0_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_0_0_0.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_0_0_0_win)
        self.qtgui_time_sink_x_0_0_1_0_0 = qtgui.time_sink_c(
            fft_len*13, #size
            1, #samp_rate
            'PRECODER 1', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_1_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_1_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_1_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1_0_0.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_0_0_win)
        self.qtgui_time_sink_x_0_0_1 = qtgui.time_sink_c(
            (fft_len+cp_len)*15, #size
            1, #samp_rate
            'Signal TX1', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 200, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1.enable_grid(True)
        self.qtgui_time_sink_x_0_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [2, 2, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [0.7, 0.7, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_time_sink_x_0_0_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_1.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_0_1_win, 8, 0, 1, 6)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_calib_rx2_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, -1.65, 200)
        self._phase_calib_rx2_win = RangeWidget(self._phase_calib_rx2_range, self.set_phase_calib_rx2, 'Phase Offset RX2', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_calib_rx2_win, 5, 3, 1, 3)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mimo_ofdm_jrc_zero_pad_1 = mimo_ofdm_jrc.zero_pad(False, 0, 100)
        self.mimo_ofdm_jrc_zero_pad_1.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_zero_pad_0 = mimo_ofdm_jrc.zero_pad(False, 0, 100)
        self.mimo_ofdm_jrc_zero_pad_0.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_sync_mimo_trx_0 = mimo_ofdm_jrc.sync_mimo_trx(1, 2, 2, samp_rate, usrp_freq, delay_samp_1, False, 0.1, "addr=192.168.100.2,master_clock_rate=250e6", "", "internal", "internal", "TX/RX,TX/RX", tx_gain, 1.0, 0.02, 0, "addr=192.168.100.2,master_clock_rate=250e6", "", "internal", "internal", "RX2,RX2", rx_gain, 1.0, 0.02, 0, "packet_len")
        self.mimo_ofdm_jrc_sync_mimo_trx_0.set_block_alias("block_0")
        self.mimo_ofdm_jrc_sync_mimo_trx_0.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_stream_encoder_0 = mimo_ofdm_jrc.stream_encoder(mcs, ofdm_config.N_data, 0, False)
        self.mimo_ofdm_jrc_stream_encoder_0.set_min_output_buffer(65536)
        self.mimo_ofdm_jrc_mimo_precoder_0 = mimo_ofdm_jrc.mimo_precoder(fft_len, N_tx, 1, ofdm_config.data_subcarriers, ofdm_config.pilot_subcarriers, ofdm_config.pilot_symbols, ofdm_config.l_stf_ltf_64, ofdm_config.ltf_mapped_sc__ss_sym, "", False, "", False, False, False, "packet_len",  False)
        self.fft_vxx_0_2 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.digital_ofdm_cyclic_prefixer_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.blocks_vector_to_stream_0_0_0_0_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_len)
        self.blocks_vector_to_stream_0_0_0_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_len)
        self.blocks_socket_pdu_0 = blocks.socket_pdu('UDP_SERVER', '', '52001', 5000, False)
        self.blocks_null_sink_0_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_cc(amp_calib_tx2*cmath.exp(1j*phase_calib_tx2))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(tx_multiplier)
        self._amp_calib_rx2_range = Range(0, 10, 0.01, 1.63, 200)
        self._amp_calib_rx2_win = RangeWidget(self._amp_calib_rx2_range, self.set_amp_calib_rx2, 'Amplitude Factor RX2', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_calib_rx2_win, 5, 0, 1, 3)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.mimo_ofdm_jrc_stream_encoder_0, 'pdu_in'))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mimo_ofdm_jrc_zero_pad_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_1, 0))
        self.connect((self.blocks_vector_to_stream_0_0_0_0, 0), (self.qtgui_time_sink_x_0_0_1_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0_0_0_0_0, 0), (self.qtgui_time_sink_x_0_0_1_0_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.fft_vxx_0_2, 0), (self.digital_ofdm_cyclic_prefixer_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.blocks_vector_to_stream_0_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.blocks_vector_to_stream_0_0_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.fft_vxx_0_2, 0))
        self.connect((self.mimo_ofdm_jrc_stream_encoder_0, 0), (self.mimo_ofdm_jrc_mimo_precoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_sync_mimo_trx_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.mimo_ofdm_jrc_sync_mimo_trx_0, 1), (self.blocks_null_sink_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_sync_mimo_trx_0, 1), (self.qtgui_time_sink_x_0_0_1_1, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.mimo_ofdm_jrc_sync_mimo_trx_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.qtgui_time_sink_x_0_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_1, 0), (self.mimo_ofdm_jrc_sync_mimo_trx_0, 1))
        self.connect((self.mimo_ofdm_jrc_zero_pad_1, 0), (self.qtgui_time_sink_x_0_0_1_2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "ofdm_mimo_radar_TX")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_usrp_freq(self):
        return self.usrp_freq

    def set_usrp_freq(self, usrp_freq):
        self.usrp_freq = usrp_freq
        self.set_rf_freq(self.usrp_freq+20e9)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_R_max(3e8*self.fft_len/(2*self.samp_rate))
        self.set_R_res(3e8/(2*self.samp_rate))

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.set_wavelength(3e8/self.rf_freq)

    def get_interp_factor(self):
        return self.interp_factor

    def set_interp_factor(self, interp_factor):
        self.interp_factor = interp_factor
        self.set_angle_max(np.rad2deg(np.arcsin((self.N_tx*self.N_rx*self.interp_factor-5)/(self.N_tx*self.N_rx*self.interp_factor))))

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_R_max(3e8*self.fft_len/(2*self.samp_rate))
        self.set_cp_len(int(self.fft_len/4))

    def get_R_res(self):
        return self.R_res

    def set_R_res(self, R_res):
        self.R_res = R_res
        self.set_variable_qtgui_label_0(self._variable_qtgui_label_0_formatter(self.R_res))

    def get_N_tx(self):
        return self.N_tx

    def set_N_tx(self, N_tx):
        self.N_tx = N_tx
        self.set_angle_max(np.rad2deg(np.arcsin((self.N_tx*self.N_rx*self.interp_factor-5)/(self.N_tx*self.N_rx*self.interp_factor))))

    def get_N_rx(self):
        return self.N_rx

    def set_N_rx(self, N_rx):
        self.N_rx = N_rx
        self.set_angle_max(np.rad2deg(np.arcsin((self.N_tx*self.N_rx*self.interp_factor-5)/(self.N_tx*self.N_rx*self.interp_factor))))

    def get_wavelength(self):
        return self.wavelength

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength

    def get_variable_qtgui_label_0(self):
        return self.variable_qtgui_label_0

    def set_variable_qtgui_label_0(self, variable_qtgui_label_0):
        self.variable_qtgui_label_0 = variable_qtgui_label_0
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_0_label, "setText", Qt.Q_ARG("QString", self.variable_qtgui_label_0))

    def get_tx_multiplier(self):
        return self.tx_multiplier

    def set_tx_multiplier(self, tx_multiplier):
        self.tx_multiplier = tx_multiplier
        self.blocks_multiply_const_vxx_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0.set_k(self.tx_multiplier)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.mimo_ofdm_jrc_sync_mimo_trx_0.set_tx_gain(self.tx_gain)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.mimo_ofdm_jrc_sync_mimo_trx_0.set_rx_gain(self.rx_gain)

    def get_phase_calib_tx2(self):
        return self.phase_calib_tx2

    def set_phase_calib_tx2(self, phase_calib_tx2):
        self.phase_calib_tx2 = phase_calib_tx2
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.amp_calib_tx2*cmath.exp(1j*self.phase_calib_tx2))

    def get_phase_calib_rx2(self):
        return self.phase_calib_rx2

    def set_phase_calib_rx2(self, phase_calib_rx2):
        self.phase_calib_rx2 = phase_calib_rx2

    def get_mcs(self):
        return self.mcs

    def set_mcs(self, mcs):
        self.mcs = mcs
        self._mcs_callback(self.mcs)
        self.mimo_ofdm_jrc_stream_encoder_0.set_mcs(self.mcs)

    def get_delay_samp_1(self):
        return self.delay_samp_1

    def set_delay_samp_1(self, delay_samp_1):
        self.delay_samp_1 = delay_samp_1
        self.mimo_ofdm_jrc_sync_mimo_trx_0.set_num_delay_samps(self.delay_samp_1)

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len

    def get_chan_est_path(self):
        return self.chan_est_path

    def set_chan_est_path(self, chan_est_path):
        self.chan_est_path = chan_est_path

    def get_angle_max(self):
        return self.angle_max

    def set_angle_max(self, angle_max):
        self.angle_max = angle_max

    def get_amp_calib_tx2(self):
        return self.amp_calib_tx2

    def set_amp_calib_tx2(self, amp_calib_tx2):
        self.amp_calib_tx2 = amp_calib_tx2
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.amp_calib_tx2*cmath.exp(1j*self.phase_calib_tx2))

    def get_amp_calib_rx2(self):
        return self.amp_calib_rx2

    def set_amp_calib_rx2(self, amp_calib_rx2):
        self.amp_calib_rx2 = amp_calib_rx2

    def get_R_max(self):
        return self.R_max

    def set_R_max(self, R_max):
        self.R_max = R_max

    def get_N_ltf(self):
        return self.N_ltf

    def set_N_ltf(self, N_ltf):
        self.N_ltf = N_ltf





def main(top_block_cls=ofdm_mimo_radar_TX, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        print("Error: failed to enable real-time scheduling.")

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
