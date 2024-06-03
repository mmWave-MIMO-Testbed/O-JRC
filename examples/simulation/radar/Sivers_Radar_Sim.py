#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Sivers Radar Sim
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
import preamble_designer_SISO  # embedded python module
import random
import string

from gnuradio import qtgui

class Sivers_Radar_Sim(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Sivers Radar Sim")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Sivers Radar Sim")
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

        self.settings = Qt.QSettings("GNU Radio", "Sivers_Radar_Sim")

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
        self.rf_freq = rf_freq = 25e9
        self.wavelength = wavelength = 3e8/rf_freq
        self.samp_rate = samp_rate = 125000000
        self.parrent_path = parrent_path = "/home/haocheng/O-JRC/examples"
        self.noise_figure_dB = noise_figure_dB = 10
        self.interp_factor_angle = interp_factor_angle = 16
        self.interp_factor = interp_factor = 8
        self.fft_len = fft_len = int(2**6)
        self.N_tx = N_tx = preamble_designer_SISO.N_tx
        self.N_rx = N_rx = 1
        self.tx_multiplier = tx_multiplier = 0.1
        self.trgt_velocity = trgt_velocity = 0
        self.trgt_rcs_dbsm = trgt_rcs_dbsm = 20
        self.trgt_range = trgt_range = 10
        self.trgt_angle = trgt_angle = 0
        self.sync_words = sync_words = ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), (0, 0j, 0, 0j, 0, 0j, -1, 1j, -1, 1j, -1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 1j, 1, 1j, 1, 1j, 1, 1j, -1, (-0-1j), 1, -1j, -1, 1j, 0, -1j, 1, (-0-1j), 1, -1j, 1, 1j, -1, -1j, 1, (-0-1j), -1, 1j, 1, 1j, 1, 1j, 1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 0j, 0, 0j, 0, 0j), (0, 0, 0, 0, 0, 0, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0))
        self.sivers_angle_log = sivers_angle_log = parrent_path+"/data/sivers_angle_log.csv"
        self.save_radar_log = save_radar_log = False
        self.radar_log_file = radar_log_file = parrent_path+"/data/radar_log.csv"
        self.radar_chan_file = radar_chan_file = parrent_path+"/data/radar_chan.csv"
        self.pilot_symbols = pilot_symbols = ((1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1))
        self.pilot_carriers_64 = pilot_carriers_64 = (-21, -7, 7, 21)
        self.noise_var = noise_var = 4.003886160000000e-21*samp_rate*10**(noise_figure_dB/10.0)
        self.max_ofdm_symbols = max_ofdm_symbols = 800
        self.freq = freq = 4e8
        self.digital_beamforming = digital_beamforming = False
        self.data_carriers_64 = data_carriers_64 = list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0)) + list(range(1, 7)) + list(range(8, 21)) +list( range(22, 27))
        self.cp_len = cp_len = int(fft_len/4)
        self.chan_est_path = chan_est_path = parrent_path+"/data/chan_est.csv"
        self.capture_radar = capture_radar = False
        self.angle_max = angle_max = np.rad2deg(np.arcsin((N_tx*N_rx*interp_factor-5)/(N_tx*N_rx*interp_factor)))
        self.angle_axis_Sivers = angle_axis_Sivers = np.linspace(-50,50,11)
        self.angle_axis = angle_axis = np.arcsin( 2/(N_tx*N_rx*interp_factor_angle)*(np.arange(0, N_tx*N_rx*interp_factor_angle)-np.floor(N_tx*N_rx*interp_factor_angle/2)+0.5) )*180/cmath.pi
        self.TX1_RXs = TX1_RXs = [1*wavelength, 3*wavelength]
        self.R_res = R_res = 3e8/(2*samp_rate)
        self.R_max = R_max = 3e8*fft_len/(2*samp_rate)
        self.N_sym = N_sym = 2
        self.N_ltf = N_ltf = preamble_designer_SISO.N_ltf

        ##################################################
        # Blocks
        ##################################################
        self._tx_multiplier_range = Range(0.05, 10, 0.05, 0.1, 200)
        self._tx_multiplier_win = RangeWidget(self._tx_multiplier_range, self.set_tx_multiplier, 'TX Gain', "counter_slider", float)
        self.top_layout.addWidget(self._tx_multiplier_win)
        self._trgt_velocity_range = Range(-40, 40, 1, 0, 200)
        self._trgt_velocity_win = RangeWidget(self._trgt_velocity_range, self.set_trgt_velocity, 'Velocity', "counter_slider", float)
        self.top_layout.addWidget(self._trgt_velocity_win)
        self._trgt_range_range = Range(0.1, R_max, 1, 10, 200)
        self._trgt_range_win = RangeWidget(self._trgt_range_range, self.set_trgt_range, "Target's Distance", "counter_slider", float)
        self.top_layout.addWidget(self._trgt_range_win)
        self._trgt_angle_range = Range(-89, +89, 1, 0, 200)
        self._trgt_angle_win = RangeWidget(self._trgt_angle_range, self.set_trgt_angle, "Target's Angle", "counter_slider", int)
        self.top_layout.addWidget(self._trgt_angle_win)
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
        self.top_layout.addWidget(self._save_radar_log_tool_bar)
        self.qtgui_time_sink_x_0_0_0_0_0_1 = qtgui.time_sink_c(
            512, #size
            samp_rate, #samp_rate
            'Signal IDFT', #name
            1 #number of inputs
        )
        self.qtgui_time_sink_x_0_0_0_0_0_1.set_update_time(0.10)
        self.qtgui_time_sink_x_0_0_0_0_0_1.set_y_axis(-1, 1)

        self.qtgui_time_sink_x_0_0_0_0_0_1.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0_0_0_0_0_1.enable_tags(True)
        self.qtgui_time_sink_x_0_0_0_0_0_1.set_trigger_mode(qtgui.TRIG_MODE_TAG, qtgui.TRIG_SLOPE_POS, 0.1, 0, 0, "packet_len")
        self.qtgui_time_sink_x_0_0_0_0_0_1.enable_autoscale(True)
        self.qtgui_time_sink_x_0_0_0_0_0_1.enable_grid(False)
        self.qtgui_time_sink_x_0_0_0_0_0_1.enable_axis_labels(True)
        self.qtgui_time_sink_x_0_0_0_0_0_1.enable_control_panel(False)
        self.qtgui_time_sink_x_0_0_0_0_0_1.enable_stem_plot(False)


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
                    self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_label(i, "Re{{Data {0}}}".format(i/2))
                else:
                    self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_label(i, "Im{{Data {0}}}".format(i/2))
            else:
                self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0_0_0_0_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_0_0_0_0_1_win = sip.wrapinstance(self.qtgui_time_sink_x_0_0_0_0_0_1.pyqwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_0_0_0_0_1_win)
        self._noise_figure_dB_range = Range(1, 40, 0.1, 10, 200)
        self._noise_figure_dB_win = RangeWidget(self._noise_figure_dB_range, self.set_noise_figure_dB, 'Noise Figure (dB)', "counter_slider", float)
        self.top_layout.addWidget(self._noise_figure_dB_win)
        self.mimo_ofdm_jrc_zero_pad_0 = mimo_ofdm_jrc.zero_pad(False, 0, (fft_len+cp_len)*3)
        self.mimo_ofdm_jrc_zero_pad_0.set_min_output_buffer(40000)
        self.mimo_ofdm_jrc_target_simulator_0 = mimo_ofdm_jrc.target_simulator([trgt_range], [trgt_velocity], [10**(trgt_rcs_dbsm/10.0)], [trgt_angle], TX1_RXs, samp_rate, rf_freq, -40, False, False, "packet_len", False)
        self.mimo_ofdm_jrc_target_simulator_0.set_min_output_buffer(64000)
        self.mimo_ofdm_jrc_stream_encoder_0 = mimo_ofdm_jrc.stream_encoder(3, len(data_carriers_64), 0, False)
        self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0 = mimo_ofdm_jrc.ofdm_cyclic_prefix_remover(fft_len, cp_len, "packet_len")
        self.mimo_ofdm_jrc_mimo_precoder_0 = mimo_ofdm_jrc.mimo_precoder(fft_len, N_tx, 1, data_carriers_64, pilot_carriers_64, pilot_symbols, preamble_designer_SISO.l_stf_ltf_64, preamble_designer_SISO.ltf_mapped_sc__ss_sym, '', True, '', False, False, False, "packet_len",  False)
        self.mimo_ofdm_jrc_mimo_precoder_0.set_min_output_buffer(800)
        self.mimo_ofdm_jrc_mimo_ofdm_radar_0 = mimo_ofdm_jrc.mimo_ofdm_radar(fft_len, N_tx, N_rx, N_tx, len(preamble_designer_SISO.l_stf_ltf_64)+1, False, False, 8, interp_factor, False, radar_chan_file, False, "packet_len",  False)
        self.mimo_ofdm_jrc_matrix_transpose_0 = mimo_ofdm_jrc.matrix_transpose(fft_len * interp_factor, 1, interp_factor_angle, False, "packet_len")
        self.mimo_ofdm_jrc_matrix_transpose_0.set_min_output_buffer(65535)
        self.mimo_ofdm_jrc_gui_heatmap_plot_0 = mimo_ofdm_jrc.gui_heatmap_plot(interp_factor_angle, digital_beamforming,sivers_angle_log,100, "Angle", "Range (m)", 'Range-Angle Image', angle_axis, np.linspace(0, 3e8*fft_len/(2*samp_rate), fft_len*interp_factor), 15, [-60, 60, 10], [0, 32, 4], False, False, "packet_len")
        self.fft_vxx_0_1_0 = fft.fft_vcc(interp_factor_angle, True, [], True, 1)
        self.fft_vxx_0_1 = fft.fft_vcc(fft_len * interp_factor, False, window.rectangular(fft_len * interp_factor), True, 1)
        self.fft_vxx_0_0 = fft.fft_vcc(fft_len, True, (), True, 1)
        self.fft_vxx_0 = fft.fft_vcc(fft_len, False, tuple([1/64**.5] * 64), True, 1)
        self.fft_vxx_0.set_min_output_buffer(800)
        self.digital_ofdm_cyclic_prefixer_0 = digital.ofdm_cyclic_prefixer(fft_len, fft_len + cp_len, 0, "packet_len")
        self.digital_ofdm_cyclic_prefixer_0.set_min_output_buffer(64000)
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        _capture_radar_push_button = Qt.QPushButton('Capture Radar Image ')
        self._capture_radar_choices = {'Pressed': True, 'Released': False}
        _capture_radar_push_button.pressed.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Pressed']))
        _capture_radar_push_button.released.connect(lambda: self.set_capture_radar(self._capture_radar_choices['Released']))
        self.top_layout.addWidget(_capture_radar_push_button)
        self.blocks_vector_to_stream_1_0 = blocks.vector_to_stream(gr.sizeof_gr_complex*1, 512)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_socket_pdu_0 = blocks.socket_pdu('UDP_SERVER', '', '52001', 5000, False)
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_gr_complex*1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(tx_multiplier)
        self.blocks_multiply_const_vxx_0.set_min_output_buffer(64000)
        self.blocks_complex_to_mag_squared_0_0 = blocks.complex_to_mag_squared(interp_factor_angle)
        self.blocks_complex_to_mag_squared_0_0.set_processor_affinity([0])
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, np.sqrt(noise_var), 0)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_socket_pdu_0, 'pdus'), (self.mimo_ofdm_jrc_stream_encoder_0, 'pdu_in'))
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_complex_to_mag_squared_0_0, 0), (self.mimo_ofdm_jrc_gui_heatmap_plot_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mimo_ofdm_jrc_zero_pad_0, 0))
        self.connect((self.blocks_throttle_0, 0), (self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0))
        self.connect((self.blocks_vector_to_stream_1_0, 0), (self.qtgui_time_sink_x_0_0_0_0_0_1, 0))
        self.connect((self.digital_ofdm_cyclic_prefixer_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.digital_ofdm_cyclic_prefixer_0, 0))
        self.connect((self.fft_vxx_0_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 1))
        self.connect((self.fft_vxx_0_1, 0), (self.blocks_vector_to_stream_1_0, 0))
        self.connect((self.fft_vxx_0_1, 0), (self.mimo_ofdm_jrc_matrix_transpose_0, 0))
        self.connect((self.fft_vxx_0_1_0, 0), (self.blocks_complex_to_mag_squared_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_matrix_transpose_0, 0), (self.fft_vxx_0_1_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0), (self.fft_vxx_0_1, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.mimo_ofdm_jrc_mimo_precoder_0, 0), (self.mimo_ofdm_jrc_mimo_ofdm_radar_0, 0))
        self.connect((self.mimo_ofdm_jrc_ofdm_cyclic_prefix_remover_0, 0), (self.fft_vxx_0_0, 0))
        self.connect((self.mimo_ofdm_jrc_stream_encoder_0, 0), (self.mimo_ofdm_jrc_mimo_precoder_0, 0))
        self.connect((self.mimo_ofdm_jrc_target_simulator_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.mimo_ofdm_jrc_target_simulator_0, 1), (self.blocks_null_sink_1, 0))
        self.connect((self.mimo_ofdm_jrc_zero_pad_0, 0), (self.mimo_ofdm_jrc_target_simulator_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "Sivers_Radar_Sim")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_rf_freq(self):
        return self.rf_freq

    def set_rf_freq(self, rf_freq):
        self.rf_freq = rf_freq
        self.set_wavelength(3e8/self.rf_freq)
        self.mimo_ofdm_jrc_target_simulator_0.setup_targets([self.trgt_range], [self.trgt_velocity], [10**(self.trgt_rcs_dbsm/10.0)], [self.trgt_angle], self.TX1_RXs, self.samp_rate, self.rf_freq, -40, False, False)

    def get_wavelength(self):
        return self.wavelength

    def set_wavelength(self, wavelength):
        self.wavelength = wavelength
        self.set_TX1_RXs([1*self.wavelength, 3*self.wavelength])

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_R_max(3e8*self.fft_len/(2*self.samp_rate))
        self.set_R_res(3e8/(2*self.samp_rate))
        self.set_noise_var(4.003886160000000e-21*self.samp_rate*10**(self.noise_figure_dB/10.0))
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.mimo_ofdm_jrc_target_simulator_0.setup_targets([self.trgt_range], [self.trgt_velocity], [10**(self.trgt_rcs_dbsm/10.0)], [self.trgt_angle], self.TX1_RXs, self.samp_rate, self.rf_freq, -40, False, False)
        self.qtgui_time_sink_x_0_0_0_0_0_1.set_samp_rate(self.samp_rate)

    def get_parrent_path(self):
        return self.parrent_path

    def set_parrent_path(self, parrent_path):
        self.parrent_path = parrent_path
        self.set_chan_est_path(self.parrent_path+"/data/chan_est.csv")
        self.set_radar_chan_file(self.parrent_path+"/data/radar_chan.csv")
        self.set_radar_log_file(self.parrent_path+"/data/radar_log.csv")
        self.set_sivers_angle_log(self.parrent_path+"/data/sivers_angle_log.csv")

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

    def get_N_tx(self):
        return self.N_tx

    def set_N_tx(self, N_tx):
        self.N_tx = N_tx
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)
        self.set_angle_max(np.rad2deg(np.arcsin((self.N_tx*self.N_rx*self.interp_factor-5)/(self.N_tx*self.N_rx*self.interp_factor))))

    def get_N_rx(self):
        return self.N_rx

    def set_N_rx(self, N_rx):
        self.N_rx = N_rx
        self.set_angle_axis(np.arcsin( 2/(self.N_tx*self.N_rx*self.interp_factor_angle)*(np.arange(0, self.N_tx*self.N_rx*self.interp_factor_angle)-np.floor(self.N_tx*self.N_rx*self.interp_factor_angle/2)+0.5) )*180/cmath.pi)
        self.set_angle_max(np.rad2deg(np.arcsin((self.N_tx*self.N_rx*self.interp_factor-5)/(self.N_tx*self.N_rx*self.interp_factor))))

    def get_tx_multiplier(self):
        return self.tx_multiplier

    def set_tx_multiplier(self, tx_multiplier):
        self.tx_multiplier = tx_multiplier
        self.blocks_multiply_const_vxx_0.set_k(self.tx_multiplier)

    def get_trgt_velocity(self):
        return self.trgt_velocity

    def set_trgt_velocity(self, trgt_velocity):
        self.trgt_velocity = trgt_velocity
        self.mimo_ofdm_jrc_target_simulator_0.setup_targets([self.trgt_range], [self.trgt_velocity], [10**(self.trgt_rcs_dbsm/10.0)], [self.trgt_angle], self.TX1_RXs, self.samp_rate, self.rf_freq, -40, False, False)

    def get_trgt_rcs_dbsm(self):
        return self.trgt_rcs_dbsm

    def set_trgt_rcs_dbsm(self, trgt_rcs_dbsm):
        self.trgt_rcs_dbsm = trgt_rcs_dbsm
        self.mimo_ofdm_jrc_target_simulator_0.setup_targets([self.trgt_range], [self.trgt_velocity], [10**(self.trgt_rcs_dbsm/10.0)], [self.trgt_angle], self.TX1_RXs, self.samp_rate, self.rf_freq, -40, False, False)

    def get_trgt_range(self):
        return self.trgt_range

    def set_trgt_range(self, trgt_range):
        self.trgt_range = trgt_range
        self.mimo_ofdm_jrc_target_simulator_0.setup_targets([self.trgt_range], [self.trgt_velocity], [10**(self.trgt_rcs_dbsm/10.0)], [self.trgt_angle], self.TX1_RXs, self.samp_rate, self.rf_freq, -40, False, False)

    def get_trgt_angle(self):
        return self.trgt_angle

    def set_trgt_angle(self, trgt_angle):
        self.trgt_angle = trgt_angle
        self.mimo_ofdm_jrc_target_simulator_0.setup_targets([self.trgt_range], [self.trgt_velocity], [10**(self.trgt_rcs_dbsm/10.0)], [self.trgt_angle], self.TX1_RXs, self.samp_rate, self.rf_freq, -40, False, False)

    def get_sync_words(self):
        return self.sync_words

    def set_sync_words(self, sync_words):
        self.sync_words = sync_words

    def get_sivers_angle_log(self):
        return self.sivers_angle_log

    def set_sivers_angle_log(self, sivers_angle_log):
        self.sivers_angle_log = sivers_angle_log

    def get_save_radar_log(self):
        return self.save_radar_log

    def set_save_radar_log(self, save_radar_log):
        self.save_radar_log = save_radar_log
        self._save_radar_log_callback(self.save_radar_log)

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

    def get_noise_var(self):
        return self.noise_var

    def set_noise_var(self, noise_var):
        self.noise_var = noise_var
        self.analog_noise_source_x_0.set_amplitude(np.sqrt(self.noise_var))

    def get_max_ofdm_symbols(self):
        return self.max_ofdm_symbols

    def set_max_ofdm_symbols(self, max_ofdm_symbols):
        self.max_ofdm_symbols = max_ofdm_symbols

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_digital_beamforming(self):
        return self.digital_beamforming

    def set_digital_beamforming(self, digital_beamforming):
        self.digital_beamforming = digital_beamforming
        self._digital_beamforming_callback(self.digital_beamforming)

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

    def get_angle_max(self):
        return self.angle_max

    def set_angle_max(self, angle_max):
        self.angle_max = angle_max

    def get_angle_axis_Sivers(self):
        return self.angle_axis_Sivers

    def set_angle_axis_Sivers(self, angle_axis_Sivers):
        self.angle_axis_Sivers = angle_axis_Sivers

    def get_angle_axis(self):
        return self.angle_axis

    def set_angle_axis(self, angle_axis):
        self.angle_axis = angle_axis

    def get_TX1_RXs(self):
        return self.TX1_RXs

    def set_TX1_RXs(self, TX1_RXs):
        self.TX1_RXs = TX1_RXs
        self.mimo_ofdm_jrc_target_simulator_0.setup_targets([self.trgt_range], [self.trgt_velocity], [10**(self.trgt_rcs_dbsm/10.0)], [self.trgt_angle], self.TX1_RXs, self.samp_rate, self.rf_freq, -40, False, False)

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





def main(top_block_cls=Sivers_Radar_Sim, options=None):

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
