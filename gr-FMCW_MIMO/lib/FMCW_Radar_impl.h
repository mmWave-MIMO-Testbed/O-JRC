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

#ifndef INCLUDED_FMCW_MIMO_FMCW_RADAR_IMPL_H
#define INCLUDED_FMCW_MIMO_FMCW_RADAR_IMPL_H

#include <FMCW_MIMO/FMCW_Radar.h>

namespace gr {
  namespace FMCW_MIMO {

    class FMCW_Radar_impl : public FMCW_Radar
    {
     private:
      // Nothing to declare in this block.
        const int d_fft_len;
        const int d_N_tx;
        const int d_N_rx;

     public:
      FMCW_Radar_impl(int N_tx, int N_rx, int fft_len, const std::string& len_tag_key);
      ~FMCW_Radar_impl();

      // Where all the action really happens
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace FMCW_MIMO
} // namespace gr

#endif /* INCLUDED_FMCW_MIMO_FMCW_RADAR_IMPL_H */

