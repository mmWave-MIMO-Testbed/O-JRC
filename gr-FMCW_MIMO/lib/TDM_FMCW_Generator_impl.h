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

#ifndef INCLUDED_FMCW_MIMO_TDM_FMCW_GENERATOR_IMPL_H
#define INCLUDED_FMCW_MIMO_TDM_FMCW_GENERATOR_IMPL_H

#include <FMCW_MIMO/TDM_FMCW_Generator.h>
#include <gnuradio/gr_complex.h>

namespace gr {
  namespace FMCW_MIMO {

    class TDM_FMCW_Generator_impl : public TDM_FMCW_Generator
    {
     private:
      double d_samp_rate;
      double d_bandwidth;
      double d_chirp_duration;
      double d_tdm_offset;
      int    d_num_tx;
      int    d_chirp_len;
      int    d_slot_len;
      int    d_period;
      int    d_sample_count;
      bool   d_enabled;
      std::vector<gr_complex> d_chirp;

     public:
      TDM_FMCW_Generator_impl(double samp_rate,
                           double bandwidth,
                           double chirp_duration,
                           double tdm_offset,
                           int    num_tx);
      ~TDM_FMCW_Generator_impl();

      // Where all the action really happens
      void set_enabled(bool enabled);
      void forecast (int noutput_items, gr_vector_int &ninput_items_required);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);
    };

  } // namespace FMCW_MIMO
} // namespace gr

#endif /* INCLUDED_FMCW_MIMO_TDM_FMCW_GENERATOR_IMPL_H */

