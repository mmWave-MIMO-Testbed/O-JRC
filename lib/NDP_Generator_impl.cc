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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "NDP_Generator_impl.h"
#include <algorithm>

namespace gr {
  namespace mimo_ofdm_jrc {


    NDP_Generator::sptr
    NDP_Generator::make()
    {
      return gnuradio::get_initial_sptr
        (new NDP_Generator_impl());
    }


    /*
     * The private constructor
     */
    NDP_Generator_impl::NDP_Generator_impl(int dataSize)
      : gr::sync_block("NDP_Generator",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(1, 1, sizeof(char))),
        d_dataSize(dataSize),
        d_packetCounter(0) {
    d_ndpCharArr.resize(3);
    d_ndpCharArr[0] = (char)PACKET_TYPE::NDP;
    std::fill_n(d_ndpCharArr.begin() + 1, d_ndpCharArr.size() - 1, 'X');}

    /*
     * Our virtual destructor.
     */
    NDP_Generator_impl::~NDP_Generator_impl()
    {
    }

    int NDP_Generator_impl::work(int noutput_items,
        gr_vector_const_void_star &input_items,
        gr_vector_void_star &output_items)
    {
      char *out = (char *) output_items[0];

      for (int i = 0; i < noutput_items; ++i) {
      if (d_packetCounter < d_ndpCharArr.size()) {
        out[i] = d_ndpCharArr[d_packetCounter];
        d_packetCounter++;
       } else {
          out[i] = 'X';
          d_packetCounter = 0;
              }
      }
      // Tell runtime system how many output items we produced.
      return noutput_items;
    
    }
  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

