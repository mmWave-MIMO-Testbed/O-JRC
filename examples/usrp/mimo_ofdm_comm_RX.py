#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: MIMO OFDM Comm Receiver
# Author: Ceyhun D. Ozkaptan, Haocheng Zhu, Xin Liu
# Description: The Ohio State University
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
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
from gnuradio.qtgui import Range, RangeWidget
import cmath
import mimo_ofdm_jrc
import numpy as np
import ofdm_config  # embedded python module
import os
import random
import string

from gnuradio import qtgui

class mimo_ofdm_comm_RX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "MIMO OFDM Comm Receiver")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("MIMO OFDM Comm Receiver")
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

        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_comm_RX")

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
        self.usrp_freq = usrp_freq = 4e9
        self.fft_len = fft_len = ofdm_config.N_sc
        self.rf_frequency = rf_frequency = usrp_freq+20e9
        self.parrent_path = parrent_path = "/home/host-pc/O-JRC/examples"
        self.cp_len = cp_len = int(fft_len/4)
        self.wavelength = wavelength = 3e8/rf_frequency
        self.sync_length = sync_length = 4*(fft_len+cp_len)
        self.save_comm_log = save_comm_log = False
        self.samp_rate = samp_rate = int(125e6)
        self.rx_gain = rx_gain = 45
        self.radar_read_file = radar_read_file = parrent_path+"/data/radar_data.csv"
        self.radar_log_file = radar_log_file = parrent_path+"/data/radar_log.csv"
        self.packet_data_file = packet_data_file = parrent_path+"/data/packet_data.csv"
        self.corr_window_size = corr_window_size = int(fft_len/2)
        self.comm_log_file = comm_log_file = parrent_path+"/data/comm_log.csv"
        self.chan_est_ndp_file = chan_est_ndp_file = parrent_path+"/data/chan_est_ndp.csv"
        self.chan_est_file = chan_est_file = parrent_path+"/data/chan_est.csv"
        self.chan_est_data_file = chan_est_data_file = parrent_path+"/data/chan_est_data.csv"
        self.chan_est = chan_est = 1
        self.N_tx = N_tx = ofdm_config.N_tx
        self.N_ltf = N_ltf = ofdm_config.N_ltf

        ##################################################
        # Blocks
        ##################################################
        # Create the options list
        self._save_comm_log_options = [False, True]
        # Create the labels list
        self._save_comm_log_labels = ['OFF', 'ON']
        # Create the combo box
        self._save_comm_log_tool_bar = Qt.QToolBar(self)
        self._save_comm_log_tool_bar.addWidget(Qt.QLabel('Save Comm Log' + ": "))
        self._save_comm_log_combo_box = Qt.QComboBox()
        self._save_comm_log_tool_bar.addWidget(self._save_comm_log_combo_box)
        for _label in self._save_comm_log_labels: self._save_comm_log_combo_box.addItem(_label)
        self._save_comm_log_callback = lambda i: Qt.QMetaObject.invokeMethod(self._save_comm_log_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._save_comm_log_options.index(i)))
        self._save_comm_log_callback(self.save_comm_log)
        self._save_comm_log_combo_box.currentIndexChanged.connect(
            lambda i: self.set_save_comm_log(self._save_comm_log_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._save_comm_log_tool_bar, 0, 3, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = Range(0, 60, 1, 45, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, 'RX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 1, 1, 2)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._chan_est_options = [0, 1]
        # Create the labels list
        self._chan_est_labels = ['LS', 'STA']
        # Create the combo box
        # Create the radio buttons
        self._chan_est_group_box = Qt.QGroupBox('Channel Estimation Algorithm' + ": ")
        self._chan_est_box = Qt.QHBoxLayout()
        class variable_chooser_button_group(Qt.QButtonGroup):
            def __init__(self, parent=None):
                Qt.QButtonGroup.__init__(self, parent)
            @pyqtSlot(int)
            def updateButtonChecked(self, button_id):
                self.button(button_id).setChecked(True)
        self._chan_est_button_group = variable_chooser_button_group()
        self._chan_est_group_box.setLayout(self._chan_est_box)
        for i, _label in enumerate(self._chan_est_labels):
            radio_button = Qt.QRadioButton(_label)
            self._chan_est_box.addWidget(radio_button)
            self._chan_est_button_group.addButton(radio_button, i)
        self._chan_est_callback = lambda i: Qt.QMetaObject.invokeMethod(self._chan_est_button_group, "updateButtonChecked", Qt.Q_ARG("int", self._chan_est_options.index(i)))
        self._chan_est_callback(self.chan_est)
        self._chan_est_button_group.buttonClicked[int].connect(
            lambda i: self.set_chan_est(self._chan_est_options[i]))
        self.top_grid_layout.addWidget(self._chan_est_group_box, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("addr=192.168.122.2,master_clock_rate=250e6", '')),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_subdev_spec("A:0", 0)
        self.uhd_usrp_source_0.set_center_freq(usrp_freq, 0)
        self.uhd_usrp_source_0.set_gain(rx_gain, 0)
        self.uhd_usrp_source_0.set_antenna('RX2', 0)
        self.uhd_usrp_source_0.set_bandwidth(samp_rate, 0)
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        # No synchronization enforced.
        self.uhd_usrp_source_0.set_min_output_buffer(24000)
        self.qtgui_time_sink_x_0_2 = qtgui.time_sink_f(
            (fft_len+cp_len)*30, #size
            1, #samp_rate
            "PREAMBLE DETECTOR", #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_2.set_update_time(0.1)
        self.qtgui_time_sink_x_0_2.set_y_axis(-0.1, 2)

        self.qtgui_time_sink_x_0_2.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_2.enable_tags(True)
        self.qtgui_time_sink_x_0_2.set_trigger_mode(qtgui.TRIG_MODE_NORM, qtgui.TRIG_SLOPE_POS, 0.7, 300, 0, '')
        self.qtgui_time_sink_x_0_2.enable_autoscale(False)
        self.qtgui_time_sink_x_0_2.enable_grid(True)
        self.qtgui_time_sink_x_0_2.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_2.enable_control_panel(False)
        self.qtgui_time_sink_x_0_2.enable_stem_plot(False)

        self.qtgui_time_sink_x_0_2.disable_legend()

        labels = ['', '', '', '', '',
            '', '', '', '', '']
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
                self.qtgui_time_sink_x_0_2.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0_2.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_2.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_2.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_2.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_2.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_2.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_2_win = sip.wrapinstance(self.qtgui_time_sink_x_0_2.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_time_sink_x_0_2_win, 4, 0, 1, 2)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            ofdm_config.N_data*5, #size
            'CONSTELLATIONS', #name
            1 #number of inputs
        )
        self.qtgui_const_sink_x_0.set_update_time(0.10)
        self.qtgui_const_sink_x_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "packet_len")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(True)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)

        self.qtgui_const_sink_x_0.disable_legend()

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [0.6, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 4, 2, 1, 2)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mimo_ofdm_jrc_stream_decoder_0 = mimo_ofdm_jrc.stream_decoder(len(ofdm_config.data_subcarriers), comm_log_file, save_comm_log, False)
        self.mimo_ofdm_jrc_stream_decoder_0.set_processor_affinity([5])
        self.mimo_ofdm_jrc_moving_avg_1 = mimo_ofdm_jrc.moving_avg(32, 1, 20000, False)
        self.mimo_ofdm_jrc_moving_avg_1.set_processor_affinity([1])
        self.mimo_ofdm_jrc_moving_avg_1.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_moving_avg_0 = mimo_ofdm_jrc.moving_avg(32, 1/32, 20000, False)
        self.mimo_ofdm_jrc_moving_avg_0.set_processor_affinity([0])
        self.mimo_ofdm_jrc_moving_avg_0.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0 = mimo_ofdm_jrc.mimo_ofdm_equalizer(chan_est, rf_frequency, samp_rate, fft_len, cp_len, ofdm_config.data_subcarriers, ofdm_config.pilot_subcarriers, ofdm_config.pilot_symbols, ofdm_config.l_stf_ltf_64[3], ofdm_config.ltf_mapped_sc__ss_sym, N_tx, chan_est_file, comm_log_file, chan_est_data_file,chan_est_ndp_file ,False, False)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_processor_affinity([4])
        self.mimo_ofdm_jrc_gui_time_plot_1_0 = mimo_ofdm_jrc.gui_time_plot(250, "throughput", "Throughput [KByte/s]", [0,5], 10, "Received Data Throughput")
        self.mimo_ofdm_jrc_gui_time_plot_1 = mimo_ofdm_jrc.gui_time_plot(250, "per", "PER [%]", [0,102], 10, "Packet Error Rate")
        self.mimo_ofdm_jrc_gui_time_plot_0_0 = mimo_ofdm_jrc.gui_time_plot(250, "snr", "SNR [dB]", [0,40], 10, "Signal-to-Noise Ratio")
        self.mimo_ofdm_jrc_frame_sync_0 = mimo_ofdm_jrc.frame_sync(fft_len, cp_len, sync_length, ofdm_config.l_ltf_fir, False)
        self.mimo_ofdm_jrc_frame_detector_0 = mimo_ofdm_jrc.frame_detector(64, 16, 0.85, 30, (len(ofdm_config.l_stf_ltf_64)+N_tx)*(fft_len+cp_len), False)
        self.mimo_ofdm_jrc_frame_detector_0.set_processor_affinity([3])
        self.mimo_ofdm_jrc_frame_detector_0.set_min_output_buffer(48000)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_len, True, window.rectangular(fft_len), True, 1)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, len(ofdm_config.data_subcarriers))
        self.blocks_sub_xx_0 = blocks.sub_cc(1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_len)
        self.blocks_socket_pdu_1 = blocks.socket_pdu('UDP_CLIENT', '127.0.0.1', '52002', 5000, False)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_xx_0.set_min_output_buffer(24000)
        self.blocks_moving_average_xx_1_0 = blocks.moving_average_ff(int(corr_window_size)+int(fft_len/4), 1/1.5, 16000, 1)
        self.blocks_moving_average_xx_1_0.set_processor_affinity([2])
        self.blocks_moving_average_xx_1_0.set_min_output_buffer(24000)
        self.blocks_divide_xx_0 = blocks.divide_ff(1)
        self.blocks_delay_0_0 = blocks.delay(gr.sizeof_gr_complex*1, int(fft_len/4))
        self.blocks_delay_0_0.set_min_output_buffer(24000)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_gr_complex*1, sync_length)
        self.blocks_conjugate_cc_0 = blocks.conjugate_cc()
        self.blocks_conjugate_cc_0.set_min_output_buffer(24000)
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(1)
        self.blocks_complex_to_mag_squared_0_0.set_min_output_buffer(24000)
        self.blocks_complex_to_mag_0 = blocks.complex_to_mag(1)
        self.blocks_abs_xx_0 = blocks.abs_ff(1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.mimo_ofdm_jrc_stream_decoder_0, 'sym'), (self.blocks_socket_pdu_1, 'pdus'))
        self.msg_connect((self.mimo_ofdm_jrc_stream_decoder_0, 'stats'), (self.mimo_ofdm_jrc_gui_time_plot_0_0, 'stats'))
        self.msg_connect((self.mimo_ofdm_jrc_stream_decoder_0, 'stats'), (self.mimo_ofdm_jrc_gui_time_plot_1, 'stats'))
        self.msg_connect((self.mimo_ofdm_jrc_stream_decoder_0, 'stats'), (self.mimo_ofdm_jrc_gui_time_plot_1_0, 'stats'))
        self.connect((self.blocks_abs_xx_0, 0), (self.blocks_divide_xx_0, 1))
        self.connect((self.blocks_complex_to_mag_0, 0), (self.blocks_divide_xx_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.blocks_moving_average_xx_1_0, 0))
        self.connect((self.blocks_conjugate_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.mimo_ofdm_jrc_frame_sync_0, 1))
        self.connect((self.blocks_delay_0_0, 0), (self.blocks_conjugate_cc_0, 0))
        self.connect((self.blocks_delay_0_0, 0), (self.mimo_ofdm_jrc_frame_detector_0, 0))
        self.connect((self.blocks_divide_xx_0, 0), (self.mimo_ofdm_jrc_frame_detector_0, 2))
        self.connect((self.blocks_divide_xx_0, 0), (self.qtgui_time_sink_x_0_2, 0))
        self.connect((self.blocks_moving_average_xx_1_0, 0), (self.blocks_abs_xx_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.mimo_ofdm_jrc_moving_avg_1, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_delay_0_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0, 0))
        self.connect((self.mimo_ofdm_jrc_frame_detector_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.mimo_ofdm_jrc_frame_detector_0, 0), (self.mimo_ofdm_jrc_frame_sync_0, 0))
        self.connect((self.mimo_ofdm_jrc_frame_sync_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0, 0), (self.mimo_ofdm_jrc_stream_decoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_moving_avg_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.mimo_ofdm_jrc_moving_avg_1, 0), (self.blocks_complex_to_mag_0, 0))
        self.connect((self.mimo_ofdm_jrc_moving_avg_1, 0), (self.mimo_ofdm_jrc_frame_detector_0, 1))
        self.connect((self.mimo_ofdm_jrc_stream_decoder_0, 0), (self.blocks_null_sink_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.mimo_ofdm_jrc_moving_avg_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_comm_RX")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_usrp_freq(self):
        return self.usrp_freq

    def set_usrp_freq(self, usrp_freq):
        self.usrp_freq = usrp_freq
        self.set_rf_frequency(self.usrp_freq+20e9)
        self.uhd_usrp_source_0.set_center_freq(self.usrp_freq, 0)

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_corr_window_size(int(self.fft_len/2))
        self.set_cp_len(int(self.fft_len/4))
        self.set_sync_length(4*(self.fft_len+self.cp_len))
        self.blocks_delay_0_0.set_dly(int(self.fft_len/4))
        self.blocks_moving_average_xx_1_0.set_length_and_scale(int(self.corr_window_size)+int(self.fft_len/4), 1/1.5)

    def get_rf_frequency(self):
        return self.rf_frequency

    def set_rf_frequency(self, rf_frequency):
        self.rf_frequency = rf_frequency
        self.set_wavelength(3e8/self.rf_frequency)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_frequency(self.rf_frequency)

    def get_parrent_path(self):
        return self.parrent_path

    def set_parrent_path(self, parrent_path):
        self.parrent_path = parrent_path
        self.set_chan_est_data_file(self.parrent_path+"/data/chan_est_data.csv")
        self.set_chan_est_file(self.parrent_path+"/data/chan_est.csv")
        self.set_chan_est_ndp_file(self.parrent_path+"/data/chan_est_ndp.csv")
        self.set_comm_log_file(self.parrent_path+"/data/comm_log.csv")
        self.set_packet_data_file(self.parrent_path+"/data/packet_data.csv")
        self.set_radar_log_file(self.parrent_path+"/data/radar_log.csv")
        self.set_radar_read_file(self.parrent_path+"/data/radar_data.csv")

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len
        self.set_sync_length(4*(self.fft_len+self.cp_len))

    def get_wavelength(self):
        return self.wavelength

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength

    def get_sync_length(self):
        return self.sync_length

    def set_sync_length(self, sync_length):
        self.sync_length = sync_length
        self.blocks_delay_0.set_dly(self.sync_length)

    def get_save_comm_log(self):
        return self.save_comm_log

    def set_save_comm_log(self, save_comm_log):
        self.save_comm_log = save_comm_log
        self._save_comm_log_callback(self.save_comm_log)
        self.mimo_ofdm_jrc_stream_decoder_0.set_stats_record(self.save_comm_log)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_bandwidth(self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0.set_bandwidth(self.samp_rate, 0)

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.uhd_usrp_source_0.set_gain(self.rx_gain, 0)

    def get_radar_read_file(self):
        return self.radar_read_file

    def set_radar_read_file(self, radar_read_file):
        self.radar_read_file = radar_read_file

    def get_radar_log_file(self):
        return self.radar_log_file

    def set_radar_log_file(self, radar_log_file):
        self.radar_log_file = radar_log_file

    def get_packet_data_file(self):
        return self.packet_data_file

    def set_packet_data_file(self, packet_data_file):
        self.packet_data_file = packet_data_file

    def get_corr_window_size(self):
        return self.corr_window_size

    def set_corr_window_size(self, corr_window_size):
        self.corr_window_size = corr_window_size
        self.blocks_moving_average_xx_1_0.set_length_and_scale(int(self.corr_window_size)+int(self.fft_len/4), 1/1.5)

    def get_comm_log_file(self):
        return self.comm_log_file

    def set_comm_log_file(self, comm_log_file):
        self.comm_log_file = comm_log_file

    def get_chan_est_ndp_file(self):
        return self.chan_est_ndp_file

    def set_chan_est_ndp_file(self, chan_est_ndp_file):
        self.chan_est_ndp_file = chan_est_ndp_file

    def get_chan_est_file(self):
        return self.chan_est_file

    def set_chan_est_file(self, chan_est_file):
        self.chan_est_file = chan_est_file

    def get_chan_est_data_file(self):
        return self.chan_est_data_file

    def set_chan_est_data_file(self, chan_est_data_file):
        self.chan_est_data_file = chan_est_data_file

    def get_chan_est(self):
        return self.chan_est

    def set_chan_est(self, chan_est):
        self.chan_est = chan_est
        self._chan_est_callback(self.chan_est)
        self.mimo_ofdm_jrc_mimo_ofdm_equalizer_0.set_estimator(self.chan_est)

    def get_N_tx(self):
        return self.N_tx

    def set_N_tx(self, N_tx):
        self.N_tx = N_tx

    def get_N_ltf(self):
        return self.N_ltf

    def set_N_ltf(self, N_ltf):
        self.N_ltf = N_ltf





def main(top_block_cls=mimo_ofdm_comm_RX, options=None):

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
