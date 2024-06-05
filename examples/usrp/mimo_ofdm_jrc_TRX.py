#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: MIMO OFDM JRC Transceiver
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
import cmath
import mimo_ofdm_jrc
import numpy as np
import ofdm_config_siso  # embedded python module
import os
import random
import string

from gnuradio import qtgui

class mimo_ofdm_jrc_TRX(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "MIMO OFDM JRC Transceiver")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("MIMO OFDM JRC Transceiver")
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

        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_jrc_TRX")

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
        self.usrp_freq = usrp_freq = 4e8
        self.samp_rate = samp_rate = int(125e6)
        self.rf_freq = rf_freq = usrp_freq+24.6e9
        self.parrent_path = parrent_path = "/home/host-pc/O-JRC/examples"
        self.interp_factor_angle = interp_factor_angle = 16
        self.interp_factor = interp_factor = 8
        self.fft_len = fft_len = ofdm_config_siso.N_sc
        self.N_tx = N_tx = ofdm_config_siso.N_tx
        self.N_rx = N_rx = 1
        self.wavelength = wavelength = 3e8/rf_freq
        self.tx_multiplier = tx_multiplier = 0.42
        self.tx_gain = tx_gain = 20
        self.sivers_angle_log = sivers_angle_log = parrent_path+"/data/sivers_angle_log.csv"
        self.signal_strength_log_file = signal_strength_log_file = parrent_path+"/data/signal_strength_log.csv"
        self.save_radar_log = save_radar_log = False
        self.rx_gain = rx_gain = 20
        self.range_axis = range_axis = np.linspace(0, 3e8*fft_len/(2*samp_rate), fft_len*interp_factor)
        self.radar_log_file = radar_log_file = parrent_path+"/data/radar_log.csv"
        self.radar_data_file = radar_data_file = parrent_path+"/data/radar_data.csv"
        self.radar_chan_file = radar_chan_file = parrent_path+"/data/radar_chan.csv"
        self.radar_aided = radar_aided = False
        self.phased_steering = phased_steering = False
        self.packet_data_file = packet_data_file = parrent_path+"/data/packet_data.csv"
        self.mcs = mcs = 3
        self.freq_smoothing = freq_smoothing = False
        self.digital_beamforming = digital_beamforming = False
        self.delay_samp = delay_samp = 188
        self.cp_len = cp_len = int(fft_len/4)
        self.chan_est_file = chan_est_file = parrent_path+"/data/chan_est.csv"
        self.capture_radar = capture_radar = False
        self.background_record = background_record = False
        self.angle_axis = angle_axis = np.arcsin( 2/(N_tx*N_rx*interp_factor_angle)*(np.arange(0, N_tx*N_rx*interp_factor_angle)-np.floor(N_tx*N_rx*interp_factor_angle/2)+0.5) )*180/cmath.pi
        self.R_res = R_res = 3e8/(2*samp_rate)
        self.R_max = R_max = 3e8*fft_len/(2*samp_rate)
        self.N_ltf = N_ltf = ofdm_config_siso.N_ltf

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
        self._tx_gain_range = Range(0, 60, 1, 20, 200)
        self._tx_gain_win = RangeWidget(self._tx_gain_range, self.set_tx_gain, 'TX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_gain_win, 0, 0, 1, 3)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 3):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._save_radar_log_options = [False, True]
        # Create the labels list
        self._save_radar_log_labels = ['OFF', 'ON']
        # Create the combo box
        self._save_radar_log_tool_bar = Qt.QToolBar(self)
        self._save_radar_log_tool_bar.addWidget(Qt.QLabel('Saving    \nRadar Log' + ": "))
        self._save_radar_log_combo_box = Qt.QComboBox()
        self._save_radar_log_tool_bar.addWidget(self._save_radar_log_combo_box)
        for _label in self._save_radar_log_labels: self._save_radar_log_combo_box.addItem(_label)
        self._save_radar_log_callback = lambda i: Qt.QMetaObject.invokeMethod(self._save_radar_log_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._save_radar_log_options.index(i)))
        self._save_radar_log_callback(self.save_radar_log)
        self._save_radar_log_combo_box.currentIndexChanged.connect(
            lambda i: self.set_save_radar_log(self._save_radar_log_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._save_radar_log_tool_bar, 2, 6, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(6, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rx_gain_range = Range(0, 60, 1, 20, 200)
        self._rx_gain_win = RangeWidget(self._rx_gain_range, self.set_rx_gain, 'RX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._rx_gain_win, 0, 3, 1, 3)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(3, 6):
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
        # Create the options list
        self._digital_beamforming_options = [False, True]
        # Create the labels list
        self._digital_beamforming_labels = ['False', 'True']
        # Create the combo box
        self._digital_beamforming_tool_bar = Qt.QToolBar(self)
        self._digital_beamforming_tool_bar.addWidget(Qt.QLabel('Digital Beamforming' + ": "))
        self._digital_beamforming_combo_box = Qt.QComboBox()
        self._digital_beamforming_tool_bar.addWidget(self._digital_beamforming_combo_box)
        for _label in self._digital_beamforming_labels: self._digital_beamforming_combo_box.addItem(_label)
        self._digital_beamforming_callback = lambda i: Qt.QMetaObject.invokeMethod(self._digital_beamforming_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._digital_beamforming_options.index(i)))
        self._digital_beamforming_callback(self.digital_beamforming)
        self._digital_beamforming_combo_box.currentIndexChanged.connect(
            lambda i: self.set_digital_beamforming(self._digital_beamforming_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._digital_beamforming_tool_bar)
        self._delay_samp_range = Range(0, 500, 1, 188, 200)
        self._delay_samp_win = RangeWidget(self._delay_samp_range, self.set_delay_samp, 'TX/RX Sync', "counter_slider", float)
        self.top_grid_layout.addWidget(self._delay_samp_win, 8, 0, 1, 8)
        for r in range(8, 9):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 8):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._background_record_options = [False, True]
        # Create the labels list
        self._background_record_labels = ['OFF', 'ON']
        # Create the combo box
        self._background_record_tool_bar = Qt.QToolBar(self)
        self._background_record_tool_bar.addWidget(Qt.QLabel('Static Background    \nRecording' + ": "))
        self._background_record_combo_box = Qt.QComboBox()
        self._background_record_tool_bar.addWidget(self._background_record_combo_box)
        for _label in self._background_record_labels: self._background_record_combo_box.addItem(_label)
        self._background_record_callback = lambda i: Qt.QMetaObject.invokeMethod(self._background_record_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._background_record_options.index(i)))
        self._background_record_callback(self.background_record)
        self._background_record_combo_box.currentIndexChanged.connect(
            lambda i: self.set_background_record(self._background_record_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._background_record_tool_bar, 2, 0, 1, 2)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_c(
            512, #size
            1, #samp_rate
            'IDFT', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
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
                    self.qtgui_time_sink_x_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        # Create the options list
        self._phased_steering_options = [False, True]
        # Create the labels list
        self._phased_steering_labels = ['OFF', 'ON']
        # Create the combo box
        self._phased_steering_tool_bar = Qt.QToolBar(self)
        self._phased_steering_tool_bar.addWidget(Qt.QLabel('Phased Steering' + ": "))
        self._phased_steering_combo_box = Qt.QComboBox()
        self._phased_steering_tool_bar.addWidget(self._phased_steering_combo_box)
        for _label in self._phased_steering_labels: self._phased_steering_combo_box.addItem(_label)
        self._phased_steering_callback = lambda i: Qt.QMetaObject.invokeMethod(self._phased_steering_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._phased_steering_options.index(i)))
        self._phased_steering_callback(self.phased_steering)
        self._phased_steering_combo_box.currentIndexChanged.connect(
            lambda i: self.set_phased_steering(self._phased_steering_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._phased_steering_tool_bar, 20, 0, 1, 4)
        for r in range(20, 21):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mimo_ofdm_jrc_zero_pad_0 = mimo_ofdm_jrc.zero_pad(False, 0, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_usrp_mimo_trx_0 = mimo_ofdm_jrc.usrp_mimo_trx(1, 1, 1, samp_rate, usrp_freq, delay_samp, False, 0.04, "addr0=192.168.120.2, master_clock_rate=250e6", "internal", "internal", "TX/RX,TX/RX", tx_gain, 0.6, 0.02, "", "RX2,RX2", rx_gain, 0.6, 0.02, 0, "", "packet_len")
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_processor_affinity([6])
        self.mimo_ofdm_jrc_stream_encoder_0 = mimo_ofdm_jrc.stream_encoder(mcs, ofdm_config_siso.N_data, 0, False)
        self.mimo_ofdm_jrc_socket_pdu_jrc_1 = mimo_ofdm_jrc.socket_pdu_jrc('UDP_SERVER', '', '52001', 5000)
        self.mimo_ofdm_jrc_range_angle_estimator_0 = mimo_ofdm_jrc.range_angle_estimator(N_tx*N_rx*interp_factor_angle, range_axis, np.arcsin( 2/(N_tx*N_rx*interp_factor_angle)*(np.arange(0, N_tx*N_rx*interp_factor_angle)-np.floor(N_tx*N_rx*interp_factor_angle/2)+0.5) )*180/cmath.pi, R_res*2, 10, 15, 50, radar_log_file, signal_strength_log_file, save_radar_log, "packet_len", False)
        self.mimo_ofdm_jrc_packet_switch_1 = mimo_ofdm_jrc.packet_switch(1000, '/path/to/default/file')
        self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0 = mimo_ofdm_jrc.ofdm_cyclic_prefix_remover(fft_len, cp_len, "packet_len")
        self.mimo_ofdm_jrc_ndp_generator_1 = mimo_ofdm_jrc.ndp_generator()
        self.mimo_ofdm_jrc_mimo_precoder_0 = mimo_ofdm_jrc.mimo_precoder(fft_len, N_tx, 1, ofdm_config_siso.data_subcarriers, ofdm_config_siso.pilot_subcarriers, ofdm_config_siso.pilot_symbols, ofdm_config_siso.l_stf_ltf_64, ofdm_config_siso.ltf_mapped_sc__ss_sym, chan_est_file, freq_smoothing, radar_data_file, radar_aided, False, False, "packet_len",  False)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_processor_affinity([7])
        self.mimo_ofdm_jrc_mimo_precoder_0.set_min_output_buffer(1000)
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0 = mimo_ofdm_jrc.mimo_ofdm_radar(fft_len, N_tx, N_rx, N_tx, len(ofdm_config_siso.l_stf_ltf_64)+1, False, background_record, 8, interp_factor, False, radar_chan_file, save_radar_log, "packet_len",  False)
        self.mimo_ofdm_jrc_matrix_transpose_0 = mimo_ofdm_jrc.matrix_transpose(fft_len*interp_factor, N_tx*N_rx, interp_factor_angle, False, "packet_len")
        self.mimo_ofdm_jrc_gui_time_plot_0 = mimo_ofdm_jrc.gui_time_plot(250, "range", "Range (m)", [0, 20], 10, "Range Estimate")
        self.mimo_ofdm_jrc_gui_heatmap_plot_0 = mimo_ofdm_jrc.gui_heatmap_plot(N_tx*N_rx*interp_factor_angle, digital_beamforming,sivers_angle_log,100, "Angle", "Range (m)", 'Range-Angle Image', angle_axis, range_axis, 9, [70, -70, 10], [0, 15,2], False, False, "packet_len")
        self.fft_vxx_0_1_0 = fft.fft_vcc(N_tx*N_rx*interp_factor_angle, True, [], True, 1)
        self.fft_vxx_0_1 = fft.fft_vcc(fft_len*interp_factor, False, window.rectangular(fft_len*interp_factor), True, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0.set_min_output_buffer(65536)
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        self._capture_radar_choices = {'Pressed': True, 'Released': True}
        _capture_radar_push_button.pressed.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Pressed']))
        _capture_radar_push_button.released.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Released']))
        self.top_layout.addWidget(_capture_radar_push_button)
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, fft_len*interp_factor)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(N_tx*N_rx*interp_factor_angle)
        self.blocks_complex_to_mag_squared_0_0.set_processor_affinity([9])


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.mimo_ofdm_jrc_ndp_generator_1, 'out'), (self.mimo_ofdm_jrc_stream_encoder_0, 'pdu_in'))
        self.msg_connect((self.mimo_ofdm_jrc_packet_switch_1, 'strobe'), (self.mimo_ofdm_jrc_ndp_generator_1, 'enable'))
        self.msg_connect((self.mimo_ofdm_jrc_packet_switch_1, 'strobe'), (self.mimo_ofdm_jrc_socket_pdu_jrc_1, 'enable'))
        self.msg_connect((self.mimo_ofdm_jrc_range_angle_estimator_0, 'params'), (self.mimo_ofdm_jrc_gui_time_plot_0, 'stats'))
        self.msg_connect((self.mimo_ofdm_jrc_socket_pdu_jrc_1, 'pdus'), (self.mimo_ofdm_jrc_stream_encoder_0, 'pdu_in'))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.mimo_ofdm_jrc_gui_heatmap_plot_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mimo_ofdm_jrc_zero_pad_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 1))
        self.connect((self.fft_vxx_0_1, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.fft_vxx_0_1, 0), (self.mimo_ofdm_jrc_matrix_transpose_0, 0))
        self.connect((self.fft_vxx_0_1_0, 0), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.fft_vxx_0_1_0, 0), (self.mimo_ofdm_jrc_range_angle_estimator_0, 0))
        self.connect((self.mimo_ofdm_jrc_matrix_transpose_0, 0), (self.fft_vxx_0_1_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0), (self.fft_vxx_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0))
        self.connect((self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_stream_encoder_0, 0), (self.mimo_ofdm_jrc_mimo_precoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0), (self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_jrc_TRX")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_usrp_freq(self):
        return self.usrp_freq

    def set_usrp_freq(self, usrp_freq):
        self.usrp_freq = usrp_freq
        self.set_rf_freq(self.usrp_freq+24.6e9)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_R_max(3e8*self.fft_len/(2*self.samp_rate))
        self.set_R_res(3e8/(2*self.samp_rate))
        self.set_range_axis(np.linspace(0, 3e8*self.fft_len/(2*self.samp_rate), self.fft_len*self.interp_factor))

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.set_wavelength(3e8/self.rf_freq)

    def get_parrent_path(self):
        return self.parrent_path

    def set_parrent_path(self, parrent_path):
        self.parrent_path = parrent_path
        self.set_chan_est_file(self.parrent_path+"/data/chan_est.csv")
        self.set_packet_data_file(self.parrent_path+"/data/packet_data.csv")
        self.set_radar_chan_file(self.parrent_path+"/data/radar_chan.csv")
        self.set_radar_data_file(self.parrent_path+"/data/radar_data.csv")
        self.set_radar_log_file(self.parrent_path+"/data/radar_log.csv")
        self.set_signal_strength_log_file(self.parrent_path+"/data/signal_strength_log.csv")
        self.set_sivers_angle_log(self.parrent_path+"/data/sivers_angle_log.csv")

    def get_interp_factor_angle(self):
        return self.interp_factor_angle

    def set_interp_factor_angle(self, interp_factor_angle):
        self.interp_factor_angle = interp_factor_angle
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)

    def get_interp_factor(self):
        return self.interp_factor

    def set_interp_factor(self, interp_factor):
        self.interp_factor = interp_factor
        self.set_range_axis(np.linspace(0, 3e8*self.fft_len/(2*self.samp_rate), self.fft_len*self.interp_factor))

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_R_max(3e8*self.fft_len/(2*self.samp_rate))
        self.set_cp_len(int(self.fft_len/4))
        self.set_range_axis(np.linspace(0, 3e8*self.fft_len/(2*self.samp_rate), self.fft_len*self.interp_factor))

    def get_N_tx(self):
        return self.N_tx

    def set_N_tx(self, N_tx):
        self.N_tx = N_tx
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)

    def get_N_rx(self):
        return self.N_rx

    def set_N_rx(self, N_rx):
        self.N_rx = N_rx
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)

    def get_wavelength(self):
        return self.wavelength

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength

    def get_tx_multiplier(self):
        return self.tx_multiplier

    def set_tx_multiplier(self, tx_multiplier):
        self.tx_multiplier = tx_multiplier
        self.blocks_multiply_const_vxx_0.set_k(self.tx_multiplier)

    def get_tx_gain(self):
        return self.tx_gain

    def set_tx_gain(self, tx_gain):
        self.tx_gain = tx_gain
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_tx_gain(self.tx_gain)

    def get_sivers_angle_log(self):
        return self.sivers_angle_log

    def set_sivers_angle_log(self, sivers_angle_log):
        self.sivers_angle_log = sivers_angle_log

    def get_signal_strength_log_file(self):
        return self.signal_strength_log_file

    def set_signal_strength_log_file(self, signal_strength_log_file):
        self.signal_strength_log_file = signal_strength_log_file

    def get_save_radar_log(self):
        return self.save_radar_log

    def set_save_radar_log(self, save_radar_log):
        self.save_radar_log = save_radar_log
        self._save_radar_log_callback(self.save_radar_log)
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0.set_stats_record(self.save_radar_log);
        self.mimo_ofdm_jrc_range_angle_estimator_0.set_stats_record(self.save_radar_log);

    def get_rx_gain(self):
        return self.rx_gain

    def set_rx_gain(self, rx_gain):
        self.rx_gain = rx_gain
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_rx_gain(self.rx_gain)

    def get_range_axis(self):
        return self.range_axis

    def set_range_axis(self, range_axis):
        self.range_axis = range_axis

    def get_radar_log_file(self):
        return self.radar_log_file

    def set_radar_log_file(self, radar_log_file):
        self.radar_log_file = radar_log_file

    def get_radar_data_file(self):
        return self.radar_data_file

    def set_radar_data_file(self, radar_data_file):
        self.radar_data_file = radar_data_file

    def get_radar_chan_file(self):
        return self.radar_chan_file

    def set_radar_chan_file(self, radar_chan_file):
        self.radar_chan_file = radar_chan_file

    def get_radar_aided(self):
        return self.radar_aided

    def set_radar_aided(self, radar_aided):
        self.radar_aided = radar_aided
        self._radar_aided_callback(self.radar_aided)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_radar_aided(self.radar_aided)

    def get_phased_steering(self):
        return self.phased_steering

    def set_phased_steering(self, phased_steering):
        self.phased_steering = phased_steering
        self._phased_steering_callback(self.phased_steering)

    def get_packet_data_file(self):
        return self.packet_data_file

    def set_packet_data_file(self, packet_data_file):
        self.packet_data_file = packet_data_file

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

    def get_digital_beamforming(self):
        return self.digital_beamforming

    def set_digital_beamforming(self, digital_beamforming):
        self.digital_beamforming = digital_beamforming
        self._digital_beamforming_callback(self.digital_beamforming)

    def get_delay_samp(self):
        return self.delay_samp

    def set_delay_samp(self, delay_samp):
        self.delay_samp = delay_samp
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_num_delay_samps(self.delay_samp)

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len

    def get_chan_est_file(self):
        return self.chan_est_file

    def set_chan_est_file(self, chan_est_file):
        self.chan_est_file = chan_est_file

    def get_capture_radar(self):
        return self.capture_radar

    def set_capture_radar(self, capture_radar):
        self.capture_radar = capture_radar
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0.capture_radar_data(self.capture_radar);

    def get_background_record(self):
        return self.background_record

    def set_background_record(self, background_record):
        self.background_record = background_record
        self._background_record_callback(self.background_record)
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0.set_background_record(self.background_record);

    def get_angle_axis(self):
        return self.angle_axis

    def set_angle_axis(self, angle_axis):
        self.angle_axis = angle_axis

    def get_R_res(self):
        return self.R_res

    def set_R_res(self, R_res):
        self.R_res = R_res

    def get_R_max(self):
        return self.R_max

    def set_R_max(self, R_max):
        self.R_max = R_max

    def get_N_ltf(self):
        return self.N_ltf

    def set_N_ltf(self, N_ltf):
        self.N_ltf = N_ltf





def main(top_block_cls=mimo_ofdm_jrc_TRX, options=None):
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
