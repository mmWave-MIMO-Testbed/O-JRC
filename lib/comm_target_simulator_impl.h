/* -*- c++ -*- */
/*
 * Copyright 2025 HaochengZhu.
 *
 * This is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * This software is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this software; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_MIMO_OFDM_JRC_COMM_TARGET_SIMULATOR_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_COMM_TARGET_SIMULATOR_IMPL_H

#include <mimo_ofdm_jrc/comm_target_simulator.h>
#include <pmt/pmt.h>
#include <complex>
#include <vector>
#include <mutex>

namespace gr {
  namespace mimo_ofdm_jrc {

    class comm_target_simulator_impl : public comm_target_simulator
    {
     private:
      // Nothing to declare in this block.
      // config & stats
      const int     d_num_tx;
      const bool    d_use_two_pi;
      const double  d_min_dist;

      std::mutex    d_mu;
      double        d_center_freq_hz;
      double        d_lambda_m;
      double        d_theta_deg   = 0.0; // deg
      double        d_distance_m  = 1.0; // m
      std::vector<std::complex<float>> d_coeffs;

      static constexpr double C = 299792458.0; // m/s

      // helper
      void recompute_coeffs_unlocked();
      void handle_cfg_msg_(pmt::pmt_t msg);

     public:
      const int     d_num_tx;
      const bool    d_use_two_pi;
      const double  d_min_dist;

      std::mutex    d_mu;
      double        d_center_freq_hz;
      double        d_lambda_m;
      double        d_theta_deg   = 0.0; // deg
      double        d_distance_m  = 1.0; // m
      std::vector<std::complex<float>> d_coeffs;

      static constexpr double C = 299792458.0; // m/s

      void recompute_coeffs_unlocked();
      void handle_cfg_msg_(pmt::pmt_t msg);
      // setters
      void set_theta_deg(double th_deg) override;
      void set_distance_m(double dist_m) override;
      void set_center_freq(double fc_hz) override;

      comm_target_simulator_impl(int num_tx,
                               double center_freq_hz,
                               double min_distance_m,
                               bool use_two_pi);
      ~comm_target_simulator_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_COMM_TARGET_SIMULATOR_IMPL_H */

