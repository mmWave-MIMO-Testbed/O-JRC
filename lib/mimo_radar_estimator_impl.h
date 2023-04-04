/* -*- c++ -*- */
/*
 * Copyright 2022 gr-mimo_ofdm_jrc author.
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

#ifndef INCLUDED_MIMO_OFDM_JRC_MIMO_RADAR_ESTIMATOR_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_MIMO_RADAR_ESTIMATOR_IMPL_H

#include <mimo_ofdm_jrc/mimo_radar_estimator.h>
#include <boost/circular_buffer.hpp>
#include "utils.h"

namespace gr {
  namespace mimo_ofdm_jrc {

    class mimo_radar_estimator_impl : public mimo_radar_estimator
    {
     private:
        const int d_fft_len;
        const int d_N_tx;
        const int d_N_rx;
        const int d_N_ltf;
        const int d_N_sync;
        const std::vector<std::vector<gr_complex>> d_P_ltf;
        const std::vector<gr_complex> d_ltf_seq;
        const int d_interp_factor;
        const bool d_enable_tx_interleave;
        const bool d_debug;
        gr_complex* radar_chan_est;

        std::vector<gr_complex> radar_chan_est_temp;

        boost::circular_buffer<std::vector<gr_complex>> radar_chan_est_buffer;
        int d_record_len;
        bool d_background_removal;
        bool d_background_recording;

     protected:
      int calculate_output_stream_length(const gr_vector_int &ninput_items);

     public:
      mimo_radar_estimator_impl(int fft_len,
            int N_tx,
            int N_rx,
            int N_ltf,
            int N_sync,
            const std::vector<std::vector<gr_complex>>& P_ltf,
            const std::vector<gr_complex>& ltf_seq,
            bool background_removal,
            bool background_recording,
            int record_len,
            int interp_factor,
            bool enable_tx_interleave,
            const std::string& len_tag_key,
            bool debug = false);
      ~mimo_radar_estimator_impl();
      void set_background_record(bool background_recording);

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_int &ninput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_MIMO_RADAR_ESTIMATOR_IMPL_H */

