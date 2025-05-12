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
#include "FMCW_Radar_impl.h"

namespace gr {
  namespace FMCW_MIMO {

    FMCW_Radar::sptr
    FMCW_Radar::make(int N_tx, int N_rx, int fft_len, const std::string& len_tag_key)
    {
      return gnuradio::get_initial_sptr
        (new FMCW_Radar_impl(N_tx, N_rx, fft_len, len_tag_key));
    }


    /*
     * The private constructor
     */
    FMCW_Radar_impl::FMCW_Radar_impl(int N_tx, int N_rx, int fft_len,const std::string& len_tag_key)
      : gr::block("FMCW_Radar",
              gr::io_signature::make(N_tx+N_rx, N_tx+N_rx, sizeof(gr_complex) * fft_len),
              gr::io_signature::make(1, 1, sizeof(gr_complex) * fft_len)),
                d_fft_len(fft_len),
                d_N_tx(N_tx),
                d_N_rx(N_rx)
    {}

    /*
     * Our virtual destructor.
     */
    FMCW_Radar_impl::~FMCW_Radar_impl()
    {
    }

    void
    FMCW_Radar_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    }

    int
    FMCW_Radar_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      const gr_complex *in_tx;
      const gr_complex *in_rx;

      // Do <+signal processing+>
      // Tell runtime system how many input items we consumed on
      // each input stream.
      consume_each (noutput_items);

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }

  } /* namespace FMCW_MIMO */
} /* namespace gr */

