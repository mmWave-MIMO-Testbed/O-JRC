# Install script for directory: /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc

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

if("x${CMAKE_INSTALL_COMPONENT}x" STREQUAL "xUnspecifiedx" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include/mimo_ofdm_jrc" TYPE FILE FILES
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/api.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/fft_peak_detect.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/frame_detector.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/frame_sync.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/gui_heatmap_plot.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/gui_time_plot.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/matrix_transpose.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/mimo_ofdm_equalizer.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/mimo_ofdm_radar.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/mimo_precoder.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/mimo_radar_estimator.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/mimo_radar_estimator_2.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/moving_avg.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/ofdm_cyclic_prefix_remover.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/ofdm_frame_generator.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/range_angle_estimator.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/stream_decoder.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/stream_encoder.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/sync_mimo_trx.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/target_simulator.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/usrp_mimo_trx.h"
    "/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/include/mimo_ofdm_jrc/zero_pad.h"
    )
endif()

