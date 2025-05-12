#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: TDM_FMCW_MIMO_ISAC
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
import pmt
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import FMCW_MIMO
import cmath
import mimo_ofdm_jrc
import numpy as np
import ofdm_config  # embedded python module
import os
import random
import string

from gnuradio import qtgui

class FMCW_MIMO_ISAC(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "TDM_FMCW_MIMO_ISAC")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("TDM_FMCW_MIMO_ISAC")
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

        self.settings = Qt.QSettings("GNU Radio", "FMCW_MIMO_ISAC")

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
        self.parrent_path = parrent_path = "/home/host-pc/O-JRC/examples"
        self.fft_len = fft_len = ofdm_config.N_sc
        self.tx_multiplier = tx_multiplier = 0.42
        self.tx_gain = tx_gain = 50
        self.samp_rate = samp_rate = int(125e6)
        self.rx_gain = rx_gain = 50
        self.radar_data_file = radar_data_file = parrent_path+"/data/radar_data.csv"
        self.radar_aided = radar_aided = False
        self.phase_tx4 = phase_tx4 = 2.02
        self.phase_tx3 = phase_tx3 = 1.95
        self.phase_tx2 = phase_tx2 = -1.2
        self.phase_rx2 = phase_rx2 = -1.15
        self.mcs = mcs = 3
        self.freq_smoothing = freq_smoothing = False
        self.delay_samp = delay_samp = 187+5
        self.cp_len = cp_len = int(fft_len/4)
        self.chan_est_file = chan_est_file = parrent_path+"/data/chan_est.csv"
        self.bandwidth = bandwidth = 125e6
        self.amp_tx4 = amp_tx4 = 0.87
        self.amp_tx3 = amp_tx3 = 0.75
        self.amp_tx2 = amp_tx2 = 0.68
        self.amp_rx2 = amp_rx2 = 1.43
        self.USRP_frequency = USRP_frequency = 4e9
        self.TDM_delay_time = TDM_delay_time = 10
        self.N_tx = N_tx = 4
        self.N_rx = N_rx = 2
        self.N_USRP = N_USRP = 2

        ##################################################
        # Blocks
        ##################################################
        self._tx_multiplier_range = Range(0.01, 4, 0.01, 0.42, 200)
        self._tx_multiplier_win = RangeWidget(self._tx_multiplier_range, self.set_tx_multiplier, 'TX Scaling', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_multiplier_win, 0, 6, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(6, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._radar_aided_options = [False, True]
        # Create the labels list
        self._radar_aided_labels = ['OFF', 'ON']
        # Create the combo box
        self._radar_aided_tool_bar = Qt.QToolBar(self)
        self._radar_aided_tool_bar.addWidget(Qt.QLabel('Radar-aided   \nPrecoding' + ": "))
        self._radar_aided_combo_box = Qt.QComboBox()
        self._radar_aided_tool_bar.addWidget(self._radar_aided_combo_box)
        for _label in self._radar_aided_labels: self._radar_aided_combo_box.addItem(_label)
        self._radar_aided_callback = lambda i: Qt.QMetaObject.invokeMethod(self._radar_aided_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._radar_aided_options.index(i)))
        self._radar_aided_callback(self.radar_aided)
        self._radar_aided_combo_box.currentIndexChanged.connect(
            lambda i: self.set_radar_aided(self._radar_aided_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._radar_aided_tool_bar, 2, 2, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_tx4_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, 2.02, 200)
        self._phase_tx4_win = RangeWidget(self._phase_tx4_range, self.set_phase_tx4, 'TX4 \n Phase', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_tx4_win, 7, 6, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(6, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_tx3_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, 1.95, 200)
        self._phase_tx3_win = RangeWidget(self._phase_tx3_range, self.set_phase_tx3, 'TX3 \n Phase', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_tx3_win, 7, 4, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._phase_tx2_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, -1.2, 200)
        self._phase_tx2_win = RangeWidget(self._phase_tx2_range, self.set_phase_tx2, 'TX2 \n Phase', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_tx2_win, 7, 2, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
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
        self.top_grid_layout.addWidget(self._mcs_group_box, 3, 0, 1, 8)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._freq_smoothing_options = [False, True]
        # Create the labels list
        self._freq_smoothing_labels = ['OFF', 'ON']
        # Create the combo box
        self._freq_smoothing_tool_bar = Qt.QToolBar(self)
        self._freq_smoothing_tool_bar.addWidget(Qt.QLabel('Frequency    \nSmoothing' + ": "))
        self._freq_smoothing_combo_box = Qt.QComboBox()
        self._freq_smoothing_tool_bar.addWidget(self._freq_smoothing_combo_box)
        for _label in self._freq_smoothing_labels: self._freq_smoothing_combo_box.addItem(_label)
        self._freq_smoothing_callback = lambda i: Qt.QMetaObject.invokeMethod(self._freq_smoothing_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._freq_smoothing_options.index(i)))
        self._freq_smoothing_callback(self.freq_smoothing)
        self._freq_smoothing_combo_box.currentIndexChanged.connect(
            lambda i: self.set_freq_smoothing(self._freq_smoothing_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._freq_smoothing_tool_bar, 2, 4, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._delay_samp_range = Range(0, 500, 1, 187+5, 200)
        self._delay_samp_win = RangeWidget(self._delay_samp_range, self.set_delay_samp, 'TX/RX Sync', "counter_slider", float)
        self.top_grid_layout.addWidget(self._delay_samp_win, 8, 0, 1, 8)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._amp_tx4_range = Range(0, 10, 0.01, 0.87, 200)
        self._amp_tx4_win = RangeWidget(self._amp_tx4_range, self.set_amp_tx4, 'TX4 \n Amp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_tx4_win, 6, 6, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(6, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._amp_tx3_range = Range(0, 10, 0.01, 0.75, 200)
        self._amp_tx3_win = RangeWidget(self._amp_tx3_range, self.set_amp_tx3, 'TX3 \n Amp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_tx3_win, 6, 4, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(4, 6):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._amp_tx2_range = Range(0, 10, 0.01, 0.68, 200)
        self._amp_tx2_win = RangeWidget(self._amp_tx2_range, self.set_amp_tx2, 'TX2 \n Amp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_tx2_win, 6, 2, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._TDM_delay_time_range = Range(0, 1000, 10, 10, 200)
        self._TDM_delay_time_win = RangeWidget(self._TDM_delay_time_range, self.set_TDM_delay_time, 'TDM Delay Time(ms)', "counter_slider", float)
        self.top_layout.addWidget(self._TDM_delay_time_win)
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
        self._phase_rx2_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, -1.15, 200)
        self._phase_rx2_win = RangeWidget(self._phase_rx2_range, self.set_phase_rx2, 'RX2 \nPhase', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_rx2_win, 7, 0, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mimo_ofdm_jrc_zero_pad_0_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0_0_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_zero_pad_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_zero_pad_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_zero_pad_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_stream_encoder_0 = mimo_ofdm_jrc.stream_encoder(mcs, ofdm_config.N_data, 0, False)
        self.mimo_ofdm_jrc_mimo_precoder_0 = mimo_ofdm_jrc.mimo_precoder(fft_len, N_tx, 1, ofdm_config.data_subcarriers, ofdm_config.pilot_subcarriers, ofdm_config.pilot_symbols, ofdm_config.l_stf_ltf_64, ofdm_config.ltf_mapped_sc__ss_sym, chan_est_file, freq_smoothing, radar_data_file, radar_aided, False, False, "packet_len",  False)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_processor_affinity([7])
        self.mimo_ofdm_jrc_mimo_precoder_0.set_min_output_buffer(1000)
        self.fft_vxx_0_3 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_3.set_min_output_buffer(65536)
        self.fft_vxx_0_2_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_2_0.set_min_output_buffer(65536)
        self.fft_vxx_0_2 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_2.set_min_output_buffer(65536)
        self.fft_vxx_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0.set_min_output_buffer(65536)
        self.digital_ofdm_cyclic_prefixer_0_1 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.blocks_socket_pdu_0 = blocks.socket_pdu('UDP_SERVER', '', '52001', 5000, False)
        self.blocks_multiply_const_vxx_0_0_1_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_1 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0_0_0 = blocks.multiply_const_cc(amp_tx4*cmath.exp(1j*phase_tx4))
        self.blocks_multiply_const_vxx_0_0_0_0 = blocks.multiply_const_cc(amp_tx3*cmath.exp(1j*phase_tx3))
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_cc(amp_tx2*cmath.exp(1j*phase_tx2))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_conjugate_cc_0 = blocks.multiply_conjugate_cc(1)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, '/home/haocheng/O-JRC/examples/FMCW_Radar/GNU-Radio-Flowgraph/fmcw_chirp.dat', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_source_0.set_min_output_buffer(24000)
        self.blocks_file_sink_0_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/haocheng/O-JRC/examples/FMCW_Radar/GNU-Radio-Flowgraph/saved_data/saved_fmcw_io_sample_rx2.dat', False)
        self.blocks_file_sink_0_0.set_unbuffered(False)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, '/home/haocheng/O-JRC/examples/FMCW_Radar/GNU-Radio-Flowgraph/saved_data/saved_fmcw_io_sample_rx1.dat', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self._amp_rx2_range = Range(0, 10, 0.01, 1.43, 200)
        self._amp_rx2_win = RangeWidget(self._amp_rx2_range, self.set_amp_rx2, 'RX2 \nAmp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_rx2_win, 6, 0, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.FMCW_MIMO_FMCW_Multiplexing_1 = FMCW_MIMO.FMCW_Multiplexing(N_tx,"TDM",TDM_delay_time,"packet_len")
        self.FMCW_MIMO_FMCW_MIMO_USRP_0 = FMCW_MIMO.FMCW_MIMO_USRP(N_USRP, N_tx, N_rx, samp_rate, USRP_frequency, delay_samp, False, , "addr0=192.168.1xx.2, addr1=192.168.1xx.2, master_clock_rate=xxxe6", "external,external", "external,external", "TX/RX,TX/RX", , 0.5, 0.01, "", "RX2,RX2", , 0.5, 0.01, 0, "", "packet_len")


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.mimo_ofdm_jrc_stream_encoder_0, 'pdu_in'))
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0), (self.blocks_file_sink_0, 0))
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 1), (self.blocks_file_sink_0_0, 0))
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0), (self.blocks_multiply_conjugate_cc_0, 0))
        self.connect((self.FMCW_MIMO_FMCW_MIMO_USRP_0, 1), (self.blocks_multiply_conjugate_cc_0, 1))
        self.connect((self.FMCW_MIMO_FMCW_Multiplexing_1, 2), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 2))
        self.connect((self.FMCW_MIMO_FMCW_Multiplexing_1, 3), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 3))
        self.connect((self.FMCW_MIMO_FMCW_Multiplexing_1, 0), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 0))
        self.connect((self.FMCW_MIMO_FMCW_Multiplexing_1, 1), (self.FMCW_MIMO_FMCW_MIMO_USRP_0, 1))
        self.connect((self.blocks_file_source_0, 0), (self.FMCW_MIMO_FMCW_Multiplexing_1, 4))
        self.connect((self.blocks_multiply_conjugate_cc_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mimo_ofdm_jrc_zero_pad_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_1, 0), (self.blocks_multiply_const_vxx_0_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_1_0, 0), (self.blocks_multiply_const_vxx_0_0_0_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_1_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_1, 0), (self.blocks_multiply_const_vxx_0_0_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.fft_vxx_0_2, 0), (self.digital_ofdm_cyclic_prefixer_0_0, 0))
        self.connect((self.fft_vxx_0_2_0, 0), (self.digital_ofdm_cyclic_prefixer_0_0_0, 0))
        self.connect((self.fft_vxx_0_3, 0), (self.digital_ofdm_cyclic_prefixer_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.fft_vxx_0_2, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 3), (self.fft_vxx_0_2_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 2), (self.fft_vxx_0_3, 0))
        self.connect((self.mimo_ofdm_jrc_stream_encoder_0, 0), (self.mimo_ofdm_jrc_mimo_precoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.FMCW_MIMO_FMCW_Multiplexing_1, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0, 0), (self.FMCW_MIMO_FMCW_Multiplexing_1, 1))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0, 0), (self.FMCW_MIMO_FMCW_Multiplexing_1, 2))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0), (self.FMCW_MIMO_FMCW_Multiplexing_1, 3))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "FMCW_MIMO_ISAC")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_parrent_path(self):
        return self.parrent_path

    def set_parrent_path(self, parrent_path):
        self.parrent_path = parrent_path
        self.set_chan_est_file(self.parrent_path+"/data/chan_est.csv")
        self.set_radar_data_file(self.parrent_path+"/data/radar_data.csv")

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_cp_len(int(self.fft_len/4))

    def get_tx_multiplier(self):
        return self.tx_multiplier

    def set_tx_multiplier(self, tx_multiplier):
        self.tx_multiplier = tx_multiplier
        self.blocks_multiply_const_vxx_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_1.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_1_0.set_k(self.tx_multiplier)

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

    def get_radar_data_file(self):
        return self.radar_data_file

    def set_radar_data_file(self, radar_data_file):
        self.radar_data_file = radar_data_file

    def get_radar_aided(self):
        return self.radar_aided

    def set_radar_aided(self, radar_aided):
        self.radar_aided = radar_aided
        self._radar_aided_callback(self.radar_aided)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_radar_aided(self.radar_aided)

    def get_phase_tx4(self):
        return self.phase_tx4

    def set_phase_tx4(self, phase_tx4):
        self.phase_tx4 = phase_tx4
        self.blocks_multiply_const_vxx_0_0_0_0_0.set_k(self.amp_tx4*cmath.exp(1j*self.phase_tx4))

    def get_phase_tx3(self):
        return self.phase_tx3

    def set_phase_tx3(self, phase_tx3):
        self.phase_tx3 = phase_tx3
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.amp_tx3*cmath.exp(1j*self.phase_tx3))

    def get_phase_tx2(self):
        return self.phase_tx2

    def set_phase_tx2(self, phase_tx2):
        self.phase_tx2 = phase_tx2
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.amp_tx2*cmath.exp(1j*self.phase_tx2))

    def get_phase_rx2(self):
        return self.phase_rx2

    def set_phase_rx2(self, phase_rx2):
        self.phase_rx2 = phase_rx2

    def get_mcs(self):
        return self.mcs

    def set_mcs(self, mcs):
        self.mcs = mcs
        self._mcs_callback(self.mcs)
        self.mimo_ofdm_jrc_stream_encoder_0.set_mcs(self.mcs)

    def get_freq_smoothing(self):
        return self.freq_smoothing

    def set_freq_smoothing(self, freq_smoothing):
        self.freq_smoothing = freq_smoothing
        self._freq_smoothing_callback(self.freq_smoothing)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_chan_est_smoothing(self.freq_smoothing)

    def get_delay_samp(self):
        return self.delay_samp

    def set_delay_samp(self, delay_samp):
        self.delay_samp = delay_samp
        self.FMCW_MIMO_FMCW_MIMO_USRP_0.set_num_delay_samps(self.delay_samp)

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len

    def get_chan_est_file(self):
        return self.chan_est_file

    def set_chan_est_file(self, chan_est_file):
        self.chan_est_file = chan_est_file

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.bandwidth)

    def get_amp_tx4(self):
        return self.amp_tx4

    def set_amp_tx4(self, amp_tx4):
        self.amp_tx4 = amp_tx4
        self.blocks_multiply_const_vxx_0_0_0_0_0.set_k(self.amp_tx4*cmath.exp(1j*self.phase_tx4))

    def get_amp_tx3(self):
        return self.amp_tx3

    def set_amp_tx3(self, amp_tx3):
        self.amp_tx3 = amp_tx3
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.amp_tx3*cmath.exp(1j*self.phase_tx3))

    def get_amp_tx2(self):
        return self.amp_tx2

    def set_amp_tx2(self, amp_tx2):
        self.amp_tx2 = amp_tx2
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.amp_tx2*cmath.exp(1j*self.phase_tx2))

    def get_amp_rx2(self):
        return self.amp_rx2

    def set_amp_rx2(self, amp_rx2):
        self.amp_rx2 = amp_rx2

    def get_USRP_frequency(self):
        return self.USRP_frequency

    def set_USRP_frequency(self, USRP_frequency):
        self.USRP_frequency = USRP_frequency

    def get_TDM_delay_time(self):
        return self.TDM_delay_time

    def set_TDM_delay_time(self, TDM_delay_time):
        self.TDM_delay_time = TDM_delay_time

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





def main(top_block_cls=FMCW_MIMO_ISAC, options=None):

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
