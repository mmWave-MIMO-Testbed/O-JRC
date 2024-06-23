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
from gnuradio import blocks
from gnuradio import digital
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
from gnuradio.filter import firdes
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
import cmath
import mimo_ofdm_jrc
import numpy as np
import ofdm_config  # embedded python module
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
        self.usrp_freq = usrp_freq = 4e9
        self.samp_rate = samp_rate = int(125e6)
        self.rf_freq = rf_freq = usrp_freq+20e9
        self.parrent_path = parrent_path = "/home/host-pc/O-JRC/examples"
        self.interp_factor_angle = interp_factor_angle = 16
        self.fft_len = fft_len = ofdm_config.N_sc
        self.N_tx = N_tx = ofdm_config.N_tx
        self.N_rx = N_rx = 2
        self.wavelength = wavelength = 3e8/rf_freq
        self.tx_multiplier = tx_multiplier = 0.42
        self.tx_gain = tx_gain = 42
        self.signal_strength_log_file = signal_strength_log_file = parrent_path+"/data/signal_strength_log.csv"
        self.save_radar_log = save_radar_log = False
        self.rx_gain = rx_gain = 41
        self.radar_log_file = radar_log_file = parrent_path+"/data/radar_log.csv"
        self.radar_data_file = radar_data_file = parrent_path+"/data/radar_data.csv"
        self.radar_chan_file = radar_chan_file = parrent_path+"/data/radar_chan.csv"
        self.radar_aided = radar_aided = False
        self.phased_steering = phased_steering = False
        self.phase_tx4 = phase_tx4 = 2.02
        self.phase_tx3 = phase_tx3 = 1.95
        self.phase_tx2 = phase_tx2 = -1.2
        self.phase_rx2 = phase_rx2 = -1.15
        self.packet_data_file = packet_data_file = parrent_path+"/data/packet_data.csv"
        self.mcs = mcs = 3
        self.interp_factor = interp_factor = 8
        self.freq_smoothing = freq_smoothing = False
        self.digital_beamforming = digital_beamforming = True
        self.delay_samp = delay_samp = 187+5
        self.cp_len = cp_len = int(fft_len/4)
        self.chan_est_file = chan_est_file = parrent_path+"/data/chan_est.csv"
        self.capture_radar = capture_radar = False
        self.background_record = background_record = True
        self.angle_res = angle_res = np.rad2deg(np.arcsin(2/(N_tx*N_rx)))
        self.angle_axis = angle_axis = np.arcsin( 2/(N_tx*N_rx*interp_factor_angle)*(np.arange(0, N_tx*N_rx*interp_factor_angle)-np.floor(N_tx*N_rx*interp_factor_angle/2)+0.5) )*180/cmath.pi
        self.amp_tx4 = amp_tx4 = 0.87
        self.amp_tx3 = amp_tx3 = 0.75
        self.amp_tx2 = amp_tx2 = 0.68
        self.amp_rx2 = amp_rx2 = 1.43
        self.R_res = R_res = 3e8/(2*samp_rate)
        self.R_max = R_max = 3e8*fft_len/(2*samp_rate)
        self.N_ltf = N_ltf = ofdm_config.N_ltf

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
        self._tx_gain_range = Range(0, 60, 1, 42, 200)
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
        self._rx_gain_range = Range(0, 60, 1, 41, 200)
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
        self._phase_rx2_range = Range(-2*cmath.pi, 2*cmath.pi, 0.01, -1.15, 200)
        self._phase_rx2_win = RangeWidget(self._phase_rx2_range, self.set_phase_rx2, 'RX2 \nPhase', "counter_slider", float)
        self.top_grid_layout.addWidget(self._phase_rx2_win, 7, 0, 1, 2)
        for r in range(7, 8):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
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
        self._delay_samp_range = Range(0, 500, 1, 187+5, 200)
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
        self._amp_rx2_range = Range(0, 10, 0.01, 1.43, 200)
        self._amp_rx2_win = RangeWidget(self._amp_rx2_range, self.set_amp_rx2, 'RX2 \nAmp', "counter_slider", float)
        self.top_grid_layout.addWidget(self._amp_rx2_win, 6, 0, 1, 2)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
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
        self.mimo_ofdm_jrc_zero_pad_0_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0_0_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_zero_pad_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_zero_pad_0_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_zero_pad_0 = mimo_ofdm_jrc.zero_pad(False, 5, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0.set_min_output_buffer(8000)
        self.mimo_ofdm_jrc_usrp_mimo_trx_0 = mimo_ofdm_jrc.usrp_mimo_trx(2, 4, 2, samp_rate, usrp_freq, delay_samp, False, 0.04, "addr0=192.168.120.2, addr1=192.168.101.2, master_clock_rate=250e6", "external,external", "external,external", "TX/RX,TX/RX,TX/RX,TX/RX", tx_gain, 0.6, 0.01, "", "RX2,RX2", rx_gain, 0.6, 0.01, 0, "", "packet_len")
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_processor_affinity([6])
        self.mimo_ofdm_jrc_stream_encoder_0 = mimo_ofdm_jrc.stream_encoder(mcs, ofdm_config.N_data, 0, False)
        self.mimo_ofdm_jrc_socket_pdu_jrc_0 = mimo_ofdm_jrc.socket_pdu_jrc('UDP_SERVER', '', '52001', 5000)
        self.mimo_ofdm_jrc_range_angle_estimator_0 = mimo_ofdm_jrc.range_angle_estimator(N_tx*N_rx*interp_factor_angle, np.linspace(0, 3e8*fft_len/(2*samp_rate), fft_len*interp_factor), np.arcsin( 2/(N_tx*N_rx*interp_factor_angle)*(np.arange(0, N_tx*N_rx*interp_factor_angle)-np.floor(N_tx*N_rx*interp_factor_angle/2)+0.5) )*180/cmath.pi, R_res*2, angle_res*2, 15, 50, radar_log_file, signal_strength_log_file, save_radar_log, "packet_len", False)
        self.mimo_ofdm_jrc_packet_switch_0 = mimo_ofdm_jrc.packet_switch(100, packet_data_file)
        self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0_0 = mimo_ofdm_jrc.ofdm_cyclic_prefix_remover(fft_len, cp_len, "packet_len")
        self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0 = mimo_ofdm_jrc.ofdm_cyclic_prefix_remover(fft_len, cp_len, "packet_len")
        self.mimo_ofdm_jrc_ndp_generator_0 = mimo_ofdm_jrc.ndp_generator()
        self.mimo_ofdm_jrc_mimo_precoder_0 = mimo_ofdm_jrc.mimo_precoder(fft_len, N_tx, 1, ofdm_config.data_subcarriers, ofdm_config.pilot_subcarriers, ofdm_config.pilot_symbols, ofdm_config.l_stf_ltf_64, ofdm_config.ltf_mapped_sc__ss_sym, chan_est_file, freq_smoothing, radar_data_file, radar_aided, False, False, "packet_len",  False)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_processor_affinity([7])
        self.mimo_ofdm_jrc_mimo_precoder_0.set_min_output_buffer(1000)
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0 = mimo_ofdm_jrc.mimo_ofdm_radar(fft_len, N_tx, N_rx, N_tx, len(ofdm_config.l_stf_ltf_64)+1, True, background_record, 10, interp_factor, False, radar_chan_file, save_radar_log, "packet_len",  False)
        self.mimo_ofdm_jrc_matrix_transpose_0 = mimo_ofdm_jrc.matrix_transpose(fft_len*interp_factor, N_tx*N_rx, interp_factor_angle, False, "packet_len")
        self.mimo_ofdm_jrc_gui_time_plot_2 = mimo_ofdm_jrc.gui_time_plot(250, "angle", "Angle (degree)", [-70,70], 10, "Angle Estimate")
        self.mimo_ofdm_jrc_gui_time_plot_1 = mimo_ofdm_jrc.gui_time_plot(250, "snr", "SNR [dB]", [10,40], 10, "Signal-to-Noise Ratio")
        self.mimo_ofdm_jrc_gui_time_plot_0 = mimo_ofdm_jrc.gui_time_plot(250, "range", "Range (m)", [0, 20], 10, "Range Estimate")
        self.mimo_ofdm_jrc_gui_heatmap_plot_0 = mimo_ofdm_jrc.gui_heatmap_plot(N_tx*N_rx*interp_factor_angle, digital_beamforming,'',100, "Angle", "Range (m)", 'Range-Angle Image', angle_axis, np.linspace(0, 3e8*fft_len/(2*samp_rate), fft_len*interp_factor), 9, [70, -70, 10], [0, 10, 2], False, False, "packet_len")
        self.fft_vxx_0_3 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_3.set_min_output_buffer(65536)
        self.fft_vxx_0_2_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_2_0.set_min_output_buffer(65536)
        self.fft_vxx_0_2 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_2.set_min_output_buffer(65536)
        self.fft_vxx_0_1_0 = fft.fft_vcc(N_tx*N_rx*interp_factor_angle, True, window.rectangular(N_tx*N_rx*interp_factor_angle), True, 1)
        self.fft_vxx_0_1 = fft.fft_vcc(fft_len*interp_factor, False, window.rectangular(fft_len*interp_factor), False, 1)
        self.fft_vxx_0_0_0 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0.set_min_output_buffer(65536)
        self.digital_ofdm_cyclic_prefixer_0_1 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        self._capture_radar_choices = {'Pressed': True, 'Released': True}
        _capture_radar_push_button.pressed.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Pressed']))
        _capture_radar_push_button.released.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Released']))
        self.top_layout.addWidget(_capture_radar_push_button)
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_cc(amp_rx2*cmath.exp(1j*phase_rx2))
        self.blocks_multiply_const_vxx_0_0_1_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_1 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0_0_0 = blocks.multiply_const_cc(amp_tx4*cmath.exp(1j*phase_tx4))
        self.blocks_multiply_const_vxx_0_0_0_0 = blocks.multiply_const_cc(amp_tx3*cmath.exp(1j*phase_tx3))
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_cc(amp_tx2*cmath.exp(1j*phase_tx2))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(N_tx*N_rx*interp_factor_angle)
        self.blocks_complex_to_mag_squared_0_0.set_processor_affinity([9])


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.mimo_ofdm_jrc_ndp_generator_0, 'out'), (self.mimo_ofdm_jrc_stream_encoder_0, 'pdu_in'))
        self.msg_connect((self.mimo_ofdm_jrc_packet_switch_0, 'strobe'), (self.mimo_ofdm_jrc_ndp_generator_0, 'enable'))
        self.msg_connect((self.mimo_ofdm_jrc_packet_switch_0, 'strobe'), (self.mimo_ofdm_jrc_socket_pdu_jrc_0, 'enable'))
        self.msg_connect((self.mimo_ofdm_jrc_range_angle_estimator_0, 'params'), (self.mimo_ofdm_jrc_gui_time_plot_0, 'stats'))
        self.msg_connect((self.mimo_ofdm_jrc_range_angle_estimator_0, 'params'), (self.mimo_ofdm_jrc_gui_time_plot_1, 'stats'))
        self.msg_connect((self.mimo_ofdm_jrc_range_angle_estimator_0, 'params'), (self.mimo_ofdm_jrc_gui_time_plot_2, 'stats'))
        self.msg_connect((self.mimo_ofdm_jrc_socket_pdu_jrc_0, 'pdus'), (self.mimo_ofdm_jrc_stream_encoder_0, 'pdu_in'))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.mimo_ofdm_jrc_gui_heatmap_plot_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mimo_ofdm_jrc_zero_pad_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_1, 0), (self.blocks_multiply_const_vxx_0_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_1_0, 0), (self.blocks_multiply_const_vxx_0_0_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_1_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_1, 0), (self.blocks_multiply_const_vxx_0_0_1, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 4))
        self.connect((self.fft_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 5))
        self.connect((self.fft_vxx_0_1, 0), (self.mimo_ofdm_jrc_matrix_transpose_0, 0))
        self.connect((self.fft_vxx_0_1_0, 0), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.fft_vxx_0_1_0, 0), (self.mimo_ofdm_jrc_range_angle_estimator_0, 0))
        self.connect((self.fft_vxx_0_2, 0), (self.digital_ofdm_cyclic_prefixer_0_0, 0))
        self.connect((self.fft_vxx_0_2_0, 0), (self.digital_ofdm_cyclic_prefixer_0_0_0, 0))
        self.connect((self.fft_vxx_0_3, 0), (self.digital_ofdm_cyclic_prefixer_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_matrix_transpose_0, 0), (self.fft_vxx_0_1_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0), (self.fft_vxx_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.fft_vxx_0_2, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 3), (self.fft_vxx_0_2_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 2), (self.fft_vxx_0_3, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 1))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 2), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 2))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 3), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 3))
        self.connect((self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0_0, 0), (self.fft_vxx_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_stream_encoder_0, 0), (self.mimo_ofdm_jrc_mimo_precoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 1), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0), (self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 1))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 2))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0), (self.mimo_ofdm_jrc_usrp_mimo_trx_0, 3))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_jrc_TRX")
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

    def get_interp_factor_angle(self):
        return self.interp_factor_angle

    def set_interp_factor_angle(self, interp_factor_angle):
        self.interp_factor_angle = interp_factor_angle
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_R_max(3e8*self.fft_len/(2*self.samp_rate))
        self.set_cp_len(int(self.fft_len/4))

    def get_N_tx(self):
        return self.N_tx

    def set_N_tx(self, N_tx):
        self.N_tx = N_tx
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)
        self.set_angle_res(np.rad2deg(np.arcsin(2/(self.N_tx*self.N_rx))))

    def get_N_rx(self):
        return self.N_rx

    def set_N_rx(self, N_rx):
        self.N_rx = N_rx
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)
        self.set_angle_res(np.rad2deg(np.arcsin(2/(self.N_tx*self.N_rx))))

    def get_wavelength(self):
        return self.wavelength

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength

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
        self.mimo_ofdm_jrc_usrp_mimo_trx_0.set_tx_gain(self.tx_gain)

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
        self.blocks_multiply_const_vxx_0_1.set_k(self.amp_rx2*cmath.exp(1j*self.phase_rx2))

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

    def get_interp_factor(self):
        return self.interp_factor

    def set_interp_factor(self, interp_factor):
        self.interp_factor = interp_factor

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

    def get_angle_res(self):
        return self.angle_res

    def set_angle_res(self, angle_res):
        self.angle_res = angle_res

    def get_angle_axis(self):
        return self.angle_axis

    def set_angle_axis(self, angle_axis):
        self.angle_axis = angle_axis

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
        self.blocks_multiply_const_vxx_0_1.set_k(self.amp_rx2*cmath.exp(1j*self.phase_rx2))

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
