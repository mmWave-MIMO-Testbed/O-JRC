#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: MIMO OFDM Radar Simulation
# Author: Ceyhun D. Ozkaptan
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
from gnuradio import analog
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
import ofdm_config  # embedded python module
import os
import random
import string

from gnuradio import qtgui

class mimo_ofdm_radar_sim(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "MIMO OFDM Radar Simulation")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("MIMO OFDM Radar Simulation")
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

        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_radar_sim")

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
        self.freq = freq = 4e9
        self.rf_freq = rf_freq = freq+20e9
        self.wavelength = wavelength = 3e8/rf_freq
        self.trgt_rcs_dbsm = trgt_rcs_dbsm = 20
        self.trgt_range_multi = trgt_range_multi = np.array([5.0, 5.5], dtype=float)
        self.samp_rate = samp_rate = 125000000
        self.parrent_path = parrent_path = "/home/haocheng/O-JRC/examples"
        self.noise_figure_dB = noise_figure_dB = 10
        self.interp_factor_angle = interp_factor_angle = 16
        self.fft_len = fft_len = int(2**6)
        self.N_tx = N_tx = ofdm_config.N_tx
        self.N_rx = N_rx = 2
        self.tx_multiplier = tx_multiplier = 0.1
        self.trgt_velocity_multi = trgt_velocity_multi = [0.0] * len(trgt_range_multi)
        self.trgt_rcs_multi = trgt_rcs_multi = [10**(trgt_rcs_dbsm/10.0), 10**(trgt_rcs_dbsm/10.0)]
        self.trgt_angle_multi = trgt_angle_multi = np.array([0.0, 10.0], dtype=float)
        self.target_data_file = target_data_file = parrent_path+"/RL_ResourceAllocation_Data/target_data.csv"
        self.save_radar_log = save_radar_log = False
        self.radar_log_file = radar_log_file = parrent_path+"/RL_ResourceAllocation_Data/radar_log.csv"
        self.radar_chan_file = radar_chan_file = parrent_path+"/RL_ResourceAllocation_Data/radar_chan.csv"
        self.pilot_symbols = pilot_symbols = ((1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1))
        self.pilot_carriers_64 = pilot_carriers_64 = (-21, -7, 7, 21)
        self.packet_data_file = packet_data_file = parrent_path+"/RL_ResourceAllocation_Data/packet_data.csv"
        self.noise_var = noise_var = 4.003886160000000e-21*samp_rate*10**(noise_figure_dB/10.0)
        self.max_ofdm_symbols = max_ofdm_symbols = 800
        self.interp_factor_range = interp_factor_range = 8
        self.interp_factor = interp_factor = 8
        self.data_carriers_64 = data_carriers_64 = list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0)) + list(range(1, 7)) + list(range(8, 21)) +list( range(22, 27))
        self.cp_len = cp_len = int(fft_len/4)
        self.chan_est_path = chan_est_path = parrent_path+"/RL_ResourceAllocation_Data/chan_est.csv"
        self.capture_radar = capture_radar = False
        self.angle_res = angle_res = np.rad2deg(np.arcsin(2/(N_tx*N_rx)))
        self.angle_axis = angle_axis = np.arcsin( 2/(N_tx*N_rx*interp_factor_angle)*(np.arange(0, N_tx*N_rx*interp_factor_angle)-np.floor(N_tx*N_rx*interp_factor_angle/2)+0.5) )*180/cmath.pi
        self.TX4_RXs = TX4_RXs = [5/2*wavelength, 9/2*wavelength]
        self.TX3_RXs = TX3_RXs = [4/2*wavelength, 8/2*wavelength]
        self.TX2_RXs = TX2_RXs = [3/2*wavelength, 7/2*wavelength]
        self.TX1_RXs = TX1_RXs = [1*wavelength, 3*wavelength]
        self.R_res = R_res = 3e8/(2*samp_rate)
        self.R_max = R_max = 3e8*fft_len/(2*samp_rate)
        self.N_sym = N_sym = 2
        self.N_ltf = N_ltf = ofdm_config.N_ltf

        ##################################################
        # Blocks
        ##################################################
        self._tx_multiplier_range = Range(0.01, 10, 0.05, 0.1, 200)
        self._tx_multiplier_win = RangeWidget(self._tx_multiplier_range, self.set_tx_multiplier, 'TX Gain', "counter_slider", float)
        self.top_grid_layout.addWidget(self._tx_multiplier_win, 1, 0, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        # Create the options list
        self._save_radar_log_options = [False, True]
        # Create the labels list
        self._save_radar_log_labels = ['False', 'True']
        # Create the combo box
        self._save_radar_log_tool_bar = Qt.QToolBar(self)
        self._save_radar_log_tool_bar.addWidget(Qt.QLabel('Save Radar Log' + ": "))
        self._save_radar_log_combo_box = Qt.QComboBox()
        self._save_radar_log_tool_bar.addWidget(self._save_radar_log_combo_box)
        for _label in self._save_radar_log_labels: self._save_radar_log_combo_box.addItem(_label)
        self._save_radar_log_callback = lambda i: Qt.QMetaObject.invokeMethod(self._save_radar_log_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._save_radar_log_options.index(i)))
        self._save_radar_log_callback(self.save_radar_log)
        self._save_radar_log_combo_box.currentIndexChanged.connect(
            lambda i: self.set_save_radar_log(self._save_radar_log_options[i]))
        # Create the radio buttons
        self.top_grid_layout.addWidget(self._save_radar_log_tool_bar, 5, 0, 1, 2)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0_0_1 = qtgui.time_sink_c(
            (fft_len+cp_len)*12, #size
            1, #samp_rate
            'Signal TX1', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_1.enable_grid(False)
        self.qtgui_time_sink_x_0_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_1.enable_stem_plot(False)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
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
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_1_win)
        self.qtgui_time_sink_x_0_0_0_0_0 = qtgui.time_sink_c(
            fft_len*12, #size
            1, #samp_rate
            'Signal RX1', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_0_0_0.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0_0_0.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_0_0_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_0_0.enable_tags(True)
        self.qtgui_time_sink_x_0_0_0_0_0.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.1, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_0_0_0.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_0_0.enable_grid(False)
        self.qtgui_time_sink_x_0_0_0_0_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_0_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_0_0_0.enable_stem_plot(False)


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
                    self.qtgui_time_sink_x_0_0_0_0_0.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_0_0_0.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_0_0_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_0_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_0_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_0_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_0_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_0_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_0_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_0_0.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_0_0_win)
        self._noise_figure_dB_range = Range(1, 40, 0.1, 10, 200)
        self._noise_figure_dB_win = RangeWidget(self._noise_figure_dB_range, self.set_noise_figure_dB, 'Noise Figure (dB)', "counter_slider", float)
        self.top_grid_layout.addWidget(self._noise_figure_dB_win, 1, 2, 1, 2)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mimo_ofdm_jrc_zero_pad_0_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 0, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0_0_0.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_zero_pad_0_0_0 = mimo_ofdm_jrc.zero_pad(False, 0, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0_0.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_zero_pad_0_0 = mimo_ofdm_jrc.zero_pad(False, 0, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0_0.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_zero_pad_0 = mimo_ofdm_jrc.zero_pad(False, 0, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0.set_min_output_buffer(24000)
        self.mimo_ofdm_jrc_stream_encoder_0 = mimo_ofdm_jrc.stream_encoder(mimo_ofdm_jrc.QPSK_3_4, len(data_carriers_64), 0, False)
        self.mimo_ofdm_jrc_socket_pdu_jrc_0 = mimo_ofdm_jrc.socket_pdu_jrc('UDP_SERVER', '', '52001', 10000)
        self.mimo_ofdm_jrc_range_angle_estimator_0 = mimo_ofdm_jrc.range_angle_estimator(N_tx*N_rx*interp_factor_angle, np.linspace(0, 3e8*fft_len/(2*samp_rate), fft_len*interp_factor_range), np.arcsin( 2/(N_tx*N_rx*interp_factor_angle)*(np.arange(0, N_tx*N_rx*interp_factor_angle)-np.floor(N_tx*N_rx*interp_factor_angle/2)+0.5) )*180/cmath.pi, R_res*2, angle_res*2, 20, 0, radar_log_file, "", save_radar_log, "packet_len", False)
        self.mimo_ofdm_jrc_packet_switch_0 = mimo_ofdm_jrc.packet_switch(50, packet_data_file)
        self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0_0 = mimo_ofdm_jrc.ofdm_cyclic_prefix_remover(fft_len, cp_len, "packet_len")
        self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0 = mimo_ofdm_jrc.ofdm_cyclic_prefix_remover(fft_len, cp_len, "packet_len")
        self.mimo_ofdm_jrc_ndp_generator_0 = mimo_ofdm_jrc.ndp_generator()
        self.mimo_ofdm_jrc_mimo_precoder_0 = mimo_ofdm_jrc.mimo_precoder(fft_len, N_tx, 1, data_carriers_64, pilot_carriers_64, pilot_symbols, ofdm_config.l_stf_ltf_64, ofdm_config.ltf_mapped_sc__ss_sym, "", False, "", False, False, False, "packet_len",  False)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_min_output_buffer(800)
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0 = mimo_ofdm_jrc.mimo_ofdm_radar(fft_len, N_tx, N_rx, N_tx, len(ofdm_config.l_stf_ltf_64)+1, False, False, 8, interp_factor_range, False, radar_chan_file, True, "packet_len",  False)
        self.mimo_ofdm_jrc_matrix_transpose_0 = mimo_ofdm_jrc.matrix_transpose(fft_len*interp_factor_range, N_tx*N_rx, interp_factor_angle, False, "packet_len")
        self.mimo_ofdm_jrc_matrix_transpose_0.set_min_output_buffer(10000)
        self.mimo_ofdm_jrc_gui_time_plot_2 = mimo_ofdm_jrc.gui_time_plot(250, "range", "Range (m)", [0,20], 10, "Range Estimate")
        self.mimo_ofdm_jrc_gui_time_plot_1 = mimo_ofdm_jrc.gui_time_plot(250, "angle", "Angle (degree)", [-70,70], 10, "Angle Estimate")
        self.mimo_ofdm_jrc_gui_time_plot_0 = mimo_ofdm_jrc.gui_time_plot(250, "snr", "SNR [dB]", [0,40], 10, "Signal-to-Noise Ratio")
        self.mimo_ofdm_jrc_gui_heatmap_plot_digital_0 = mimo_ofdm_jrc.gui_heatmap_plot_digital(N_tx*N_rx*interp_factor_angle,100, "Angle", "Range (m)", 'Range-Angle Image', angle_axis, np.linspace(0, 3e8*fft_len/(2*samp_rate), fft_len*interp_factor), 9, [-70, 70, 10], [0, 10, 1], False, False, "packet_len")
        self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0_0 = mimo_ofdm_jrc.Multi_targets_simulator_make_from_csv( '/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data/target_data.csv', TX4_RXs, samp_rate, rf_freq, -40, False, False, "packet_len", False)
        self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0_0.set_min_output_buffer(64000)
        self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0 = mimo_ofdm_jrc.Multi_targets_simulator_make_from_csv( '/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data/target_data.csv', TX3_RXs, samp_rate, rf_freq, -40, False, False, "packet_len", False)
        self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0.set_min_output_buffer(64000)
        self.mimo_ofdm_jrc_Multi_targets_simulator_0_0 = mimo_ofdm_jrc.Multi_targets_simulator_make_from_csv( '/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data/target_data.csv', TX2_RXs, samp_rate, rf_freq, -40, False, False, "packet_len", False)
        self.mimo_ofdm_jrc_Multi_targets_simulator_0_0.set_min_output_buffer(64000)
        self.mimo_ofdm_jrc_Multi_targets_simulator_0 = mimo_ofdm_jrc.Multi_targets_simulator_make_from_csv( '/home/haocheng/O-JRC/examples/RL_ResourceAllocation_Data/target_data.csv', TX1_RXs, samp_rate, rf_freq, -40, False, False, "packet_len", False)
        self.mimo_ofdm_jrc_Multi_targets_simulator_0.set_min_output_buffer(64000)
        self.fft_vxx_0_2_0_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_2_0_0.set_min_output_buffer(800)
        self.fft_vxx_0_2_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_2_0.set_min_output_buffer(800)
        self.fft_vxx_0_2 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0_2.set_min_output_buffer(800)
        self.fft_vxx_0_1_0 = fft.fft_vcc(N_tx*N_rx*interp_factor_angle, True, window.rectangular(N_tx*N_rx*interp_factor_angle), True, 1)
        self.fft_vxx_0_1 = fft.fft_vcc(fft_len*interp_factor_range, False, window.rectangular(fft_len*interp_factor_range), False, 1)
        self.fft_vxx_0_0_0 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0.set_min_output_buffer(800)
        self.digital_ofdm_cyclic_prefixer_0_0_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0_0_0.set_min_output_buffer(64000)
        self.digital_ofdm_cyclic_prefixer_0_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0_0.set_min_output_buffer(64000)
        self.digital_ofdm_cyclic_prefixer_0_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0_0.set_min_output_buffer(64000)
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0.set_min_output_buffer(64000)
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        self._capture_radar_choices = {'Pressed': True, 'Released': False}
        _capture_radar_push_button.pressed.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Pressed']))
        _capture_radar_push_button.released.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Released']))
        self.top_grid_layout.addWidget(_capture_radar_push_button, 5, 2, 1, 2)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(2, 4):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_multiply_const_vxx_0_0_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0_0.set_min_output_buffer(64000)
        self.blocks_multiply_const_vxx_0_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0.set_min_output_buffer(64000)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0_0.set_min_output_buffer(64000)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0.set_min_output_buffer(64000)
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(N_tx*N_rx*interp_factor_angle)
        self.blocks_complex_to_mag_squared_0_0.set_processor_affinity([9])
        self.blocks_add_xx_0_0 = blocks.add_vcc(1)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_noise_source_x_0_0 = analog.noise_source_c(analog.GR_GAUSSIAN, np.sqrt(noise_var), 1)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, np.sqrt(noise_var), 0)


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
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 4))
        self.connect((self.analog_noise_source_x_0_0, 0), (self.blocks_add_xx_0_0, 4))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.qtgui_time_sink_x_0_0_0_0_0, 0))
        self.connect((self.blocks_add_xx_0_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.mimo_ofdm_jrc_gui_heatmap_plot_digital_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mimo_ofdm_jrc_zero_pad_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_time_sink_x_0_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0_0_0, 0), (self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0_0_0_0, 0), (self.blocks_multiply_const_vxx_0_0_0_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 4))
        self.connect((self.fft_vxx_0_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 5))
        self.connect((self.fft_vxx_0_1, 0), (self.mimo_ofdm_jrc_matrix_transpose_0, 0))
        self.connect((self.fft_vxx_0_1_0, 0), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.fft_vxx_0_1_0, 0), (self.mimo_ofdm_jrc_range_angle_estimator_0, 0))
        self.connect((self.fft_vxx_0_2, 0), (self.digital_ofdm_cyclic_prefixer_0_0, 0))
        self.connect((self.fft_vxx_0_2_0, 0), (self.digital_ofdm_cyclic_prefixer_0_0_0, 0))
        self.connect((self.fft_vxx_0_2_0_0, 0), (self.digital_ofdm_cyclic_prefixer_0_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0, 1), (self.blocks_add_xx_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0_0, 1), (self.blocks_add_xx_0_0, 1))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0, 0), (self.blocks_add_xx_0, 3))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0, 1), (self.blocks_add_xx_0_0, 2))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0_0, 0), (self.blocks_add_xx_0, 2))
        self.connect((self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0_0, 1), (self.blocks_add_xx_0_0, 3))
        self.connect((self.mimo_ofdm_jrc_matrix_transpose_0, 0), (self.fft_vxx_0_1_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0), (self.fft_vxx_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.fft_vxx_0_2, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 2), (self.fft_vxx_0_2_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 3), (self.fft_vxx_0_2_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 2), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 2))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 3), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 3))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 1), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 1))
        self.connect((self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0_0, 0), (self.fft_vxx_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_stream_encoder_0, 0), (self.mimo_ofdm_jrc_mimo_precoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.mimo_ofdm_jrc_Multi_targets_simulator_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0, 0), (self.mimo_ofdm_jrc_Multi_targets_simulator_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0, 0), (self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0_0_0_0, 0), (self.mimo_ofdm_jrc_Multi_targets_simulator_0_0_0_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "mimo_ofdm_radar_sim")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.set_rf_freq(self.freq+20e9)

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.set_wavelength(3e8/self.rf_freq)

    def get_wavelength(self):
        return self.wavelength

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength
        self.set_TX1_RXs([1*self.wavelength, 3*self.wavelength])
        self.set_TX2_RXs([3/2*self.wavelength, 7/2*self.wavelength])
        self.set_TX3_RXs([4/2*self.wavelength, 8/2*self.wavelength])
        self.set_TX4_RXs([5/2*self.wavelength, 9/2*self.wavelength])

    def get_trgt_rcs_dbsm(self):
        return self.trgt_rcs_dbsm

    def set_trgt_rcs_dbsm(self, trgt_rcs_dbsm):
        self.trgt_rcs_dbsm = trgt_rcs_dbsm
        self.set_trgt_rcs_multi([10**(self.trgt_rcs_dbsm/10.0), 10**(self.trgt_rcs_dbsm/10.0)])

    def get_trgt_range_multi(self):
        return self.trgt_range_multi

    def set_trgt_range_multi(self, trgt_range_multi):
        self.trgt_range_multi = trgt_range_multi
        self.set_trgt_velocity_multi([0.0] * len(self.trgt_range_multi))

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_R_max(3e8*self.fft_len/(2*self.samp_rate))
        self.set_R_res(3e8/(2*self.samp_rate))
        self.set_noise_var(4.003886160000000e-21*self.samp_rate*10**(self.noise_figure_dB/10.0))
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)

    def get_parrent_path(self):
        return self.parrent_path

    def set_parrent_path(self, parrent_path):
        self.parrent_path = parrent_path
        self.set_chan_est_path(self.parrent_path+"/RL_ResourceAllocation_Data/chan_est.csv")
        self.set_packet_data_file(self.parrent_path+"/RL_ResourceAllocation_Data/packet_data.csv")
        self.set_radar_chan_file(self.parrent_path+"/RL_ResourceAllocation_Data/radar_chan.csv")
        self.set_radar_log_file(self.parrent_path+"/RL_ResourceAllocation_Data/radar_log.csv")
        self.set_target_data_file(self.parrent_path+"/RL_ResourceAllocation_Data/target_data.csv")

    def get_noise_figure_dB(self):
        return self.noise_figure_dB

    def set_noise_figure_dB(self, noise_figure_dB):
        self.noise_figure_dB = noise_figure_dB
        self.set_noise_var(4.003886160000000e-21*self.samp_rate*10**(self.noise_figure_dB/10.0))

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

    def get_tx_multiplier(self):
        return self.tx_multiplier

    def set_tx_multiplier(self, tx_multiplier):
        self.tx_multiplier = tx_multiplier
        self.blocks_multiply_const_vxx_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0.set_k(self.tx_multiplier)
        self.blocks_multiply_const_vxx_0_0_0_0.set_k(self.tx_multiplier)

    def get_trgt_velocity_multi(self):
        return self.trgt_velocity_multi

    def set_trgt_velocity_multi(self, trgt_velocity_multi):
        self.trgt_velocity_multi = trgt_velocity_multi

    def get_trgt_rcs_multi(self):
        return self.trgt_rcs_multi

    def set_trgt_rcs_multi(self, trgt_rcs_multi):
        self.trgt_rcs_multi = trgt_rcs_multi

    def get_trgt_angle_multi(self):
        return self.trgt_angle_multi

    def set_trgt_angle_multi(self, trgt_angle_multi):
        self.trgt_angle_multi = trgt_angle_multi

    def get_target_data_file(self):
        return self.target_data_file

    def set_target_data_file(self, target_data_file):
        self.target_data_file = target_data_file

    def get_save_radar_log(self):
        return self.save_radar_log

    def set_save_radar_log(self, save_radar_log):
        self.save_radar_log = save_radar_log
        self._save_radar_log_callback(self.save_radar_log)
        self.mimo_ofdm_jrc_range_angle_estimator_0.set_stats_record(self.save_radar_log);

    def get_radar_log_file(self):
        return self.radar_log_file

    def set_radar_log_file(self, radar_log_file):
        self.radar_log_file = radar_log_file

    def get_radar_chan_file(self):
        return self.radar_chan_file

    def set_radar_chan_file(self, radar_chan_file):
        self.radar_chan_file = radar_chan_file

    def get_pilot_symbols(self):
        return self.pilot_symbols

    def set_pilot_symbols(self, pilot_symbols):
        self.pilot_symbols = pilot_symbols

    def get_pilot_carriers_64(self):
        return self.pilot_carriers_64

    def set_pilot_carriers_64(self, pilot_carriers_64):
        self.pilot_carriers_64 = pilot_carriers_64

    def get_packet_data_file(self):
        return self.packet_data_file

    def set_packet_data_file(self, packet_data_file):
        self.packet_data_file = packet_data_file

    def get_noise_var(self):
        return self.noise_var

    def set_noise_var(self, noise_var):
        self.noise_var = noise_var
        self.analog_noise_source_x_0.set_amplitude(np.sqrt(self.noise_var))
        self.analog_noise_source_x_0_0.set_amplitude(np.sqrt(self.noise_var))

    def get_max_ofdm_symbols(self):
        return self.max_ofdm_symbols

    def set_max_ofdm_symbols(self, max_ofdm_symbols):
        self.max_ofdm_symbols = max_ofdm_symbols

    def get_interp_factor_range(self):
        return self.interp_factor_range

    def set_interp_factor_range(self, interp_factor_range):
        self.interp_factor_range = interp_factor_range

    def get_interp_factor(self):
        return self.interp_factor

    def set_interp_factor(self, interp_factor):
        self.interp_factor = interp_factor

    def get_data_carriers_64(self):
        return self.data_carriers_64

    def set_data_carriers_64(self, data_carriers_64):
        self.data_carriers_64 = data_carriers_64

    def get_cp_len(self):
        return self.cp_len

    def set_cp_len(self, cp_len):
        self.cp_len = cp_len

    def get_chan_est_path(self):
        return self.chan_est_path

    def set_chan_est_path(self, chan_est_path):
        self.chan_est_path = chan_est_path

    def get_capture_radar(self):
        return self.capture_radar

    def set_capture_radar(self, capture_radar):
        self.capture_radar = capture_radar
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0.capture_radar_data(self.capture_radar);

    def get_angle_res(self):
        return self.angle_res

    def set_angle_res(self, angle_res):
        self.angle_res = angle_res

    def get_angle_axis(self):
        return self.angle_axis

    def set_angle_axis(self, angle_axis):
        self.angle_axis = angle_axis

    def get_TX4_RXs(self):
        return self.TX4_RXs

    def set_TX4_RXs(self, TX4_RXs):
        self.TX4_RXs = TX4_RXs

    def get_TX3_RXs(self):
        return self.TX3_RXs

    def set_TX3_RXs(self, TX3_RXs):
        self.TX3_RXs = TX3_RXs

    def get_TX2_RXs(self):
        return self.TX2_RXs

    def set_TX2_RXs(self, TX2_RXs):
        self.TX2_RXs = TX2_RXs

    def get_TX1_RXs(self):
        return self.TX1_RXs

    def set_TX1_RXs(self, TX1_RXs):
        self.TX1_RXs = TX1_RXs

    def get_R_res(self):
        return self.R_res

    def set_R_res(self, R_res):
        self.R_res = R_res

    def get_R_max(self):
        return self.R_max

    def set_R_max(self, R_max):
        self.R_max = R_max

    def get_N_sym(self):
        return self.N_sym

    def set_N_sym(self, N_sym):
        self.N_sym = N_sym

    def get_N_ltf(self):
        return self.N_ltf

    def set_N_ltf(self, N_ltf):
        self.N_ltf = N_ltf





def main(top_block_cls=mimo_ofdm_radar_sim, options=None):

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
