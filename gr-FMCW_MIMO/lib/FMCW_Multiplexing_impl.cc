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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "FMCW_Multiplexing_impl.h"
#include <iostream>
#include <boost/algorithm/string.hpp>

namespace gr {
  namespace FMCW_MIMO {

    FMCW_Multiplexing::sptr
    FMCW_Multiplexing::make(int N_tx, bool multiplexing_type, float TDM_delay, 
                            const std::string& len_key)
    {
      return gnuradio::get_initial_sptr
        (new FMCW_Multiplexing_impl(N_tx, multiplexing_type, TDM_delay, len_key));
    }


    /*
     * The private constructor
     */
    FMCW_Multiplexing_impl::FMCW_Multiplexing_impl(int N_tx, bool multiplexing_type, float TDM_delay, const std::string& len_key)
      : gr::tagged_stream_block("FMCW_Multiplexing",
              gr::io_signature::makev(2, 2, std::vector<int>({ static_cast<int>(sizeof(gr_complex)*N_tx), static_cast<int>(sizeof(gr_complex)) })),
              gr::io_signature::make(N_tx, N_tx, sizeof(gr_complex)), len_key)
    {
      d_N_tx = N_tx;
      d_TDM_delay = TDM_delay;
    }

    /*
     * Our virtual destructor.
     */
    FMCW_Multiplexing_impl::~FMCW_Multiplexing_impl()
    {
    }

    int
    FMCW_Multiplexing_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
      int noutput_items = ninput_items[0];
      return noutput_items ;
    }

    int
    FMCW_Multiplexing_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
		  // Set output items on packet length
		  noutput_items = ninput_items[0];
      // Obtain tx_in
      const gr_complex* tx_in = (const gr_complex*) input_items[0];
      // Obtain FMCW in
      const gr_complex* fmcw_in = (const gr_complex*) input_items[1];

      // Do <+signal processing+>

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace FMCW_MIMO */
} /* namespace gr */

