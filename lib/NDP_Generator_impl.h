/* -*- c++ -*- */
/*
 * Copyright 2023 gr-mimo_ofdm_jrc author.
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

#ifndef INCLUDED_MIMO_OFDM_JRC_NDP_GENERATOR_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_NDP_GENERATOR_IMPL_H

#include <mimo_ofdm_jrc/NDP_Generator.h>
#include <vector>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    enum class PAKCET_TYPE {NDP, DATA};

    class NDP_Generator_impl : public gr::sync_block
    {
     private:
      // Nothing to declare in this block.
      std::vector<char> d_ndpCharArr;
      int d_dataSize;
      int d_packetCounter;

     public:
      NDP_Generator_impl();
      ~NDP_Generator_impl();

      // Where all the action really happens
      int work(
              int noutput_items,
              gr_vector_const_void_star &input_items,
              gr_vector_void_star &output_items
      );
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_NDP_GENERATOR_IMPL_H */

