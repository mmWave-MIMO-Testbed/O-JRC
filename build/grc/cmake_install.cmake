# Install script for directory: /home/haocheng/gr-mimo_ofdm_jrc/grc

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "/usr/local")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Install shared libraries without execute permission?
if(NOT DEFINED CMAKE_INSTALL_SO_NO_EXE)
  set(CMAKE_INSTALL_SO_NO_EXE "1")
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set default install directory permissions.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "/usr/bin/objdump")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/share/gnuradio/grc/blocks" TYPE FILE FILES
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_fft_peak_detect.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_frame_detector.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_frame_sync.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_gui_heatmap_plot.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_gui_time_plot.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_matrix_transpose.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_mimo_ofdm_equalizer.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_mimo_ofdm_radar.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_mimo_precoder.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_mimo_radar_estimator.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_mimo_radar_estimator_2.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_moving_avg.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_ofdm_cyclic_prefix_remover.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_ofdm_frame_generator.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_range_angle_estimator.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_stream_decoder.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_stream_encoder.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_sync_mimo_trx.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_target_simulator.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_usrp_mimo_trx.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_zero_pad.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_NDP_Generator.block.yml"
    "/home/haocheng/gr-mimo_ofdm_jrc/grc/mimo_ofdm_jrc_NDP_Gen_UDP.block.yml"
    )
endif()

