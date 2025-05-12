/* -*- c++ -*- */
/*
 * Copyright 2025 Haocheng Zhu.
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

#ifndef INCLUDED_FMCW_MIMO_FMCW_MULTIPLEXING_IMPL_H
#define INCLUDED_FMCW_MIMO_FMCW_MULTIPLEXING_IMPL_H

#include <FMCW_MIMO/FMCW_Multiplexing.h>

namespace gr {
  namespace FMCW_MIMO {

        /*! 
     * brief FMCW TDM Source: multi-TX TDM FMCW，output num_tx complex samples
     *
     * input：
     *  - samp_rate:  (Hz)
     *  - bandwidth:  (Hz)
     *  - chirp_duration: single chirp duration (s)
     *  - tdm_offset: TDM switch time (s)
     *  - num_tx: number of TX channels
     */
    class FMCW_Multiplexing_impl : public FMCW_Multiplexing
    {
     private:
      // Nothing to declare in this block.

     protected:
      int calculate_output_stream_length(const gr_vector_int &ninput_items);

     public:
      FMCW_Multiplexing_impl(int N_tx, bool multiplexing_type, float TDM_delay, 
        const std::string& len_key);
      ~FMCW_Multiplexing_impl();
        int d_N_tx;
        float d_TDM_delay;

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_int &ninput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace FMCW_MIMO
} // namespace gr

#endif /* INCLUDED_FMCW_MIMO_FMCW_MULTIPLEXING_IMPL_H */

