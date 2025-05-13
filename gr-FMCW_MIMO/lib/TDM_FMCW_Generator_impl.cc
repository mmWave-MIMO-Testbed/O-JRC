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
#include "TDM_FMCW_Generator_impl.h"
#include <cmath>
#include <cstring>
#include <stdexcept>

namespace gr {
  namespace FMCW_MIMO {

    TDM_FMCW_Generator::sptr
    TDM_FMCW_Generator::make(double samp_rate,
                          double bandwidth,
                          double chirp_duration,
                          double tdm_offset,
                          int    num_tx,
                        const std::string &len_key)
    {
      return sptr(new TDM_FMCW_Generator_impl(
                                            samp_rate, bandwidth, chirp_duration, tdm_offset, num_tx, len_key));
    }


    /*
     * The private constructor
     */
    TDM_FMCW_Generator_impl::TDM_FMCW_Generator_impl(
      double samp_rate,
      double bandwidth,
      double chirp_duration,
      double tdm_offset,
      int    num_tx,
      const std::string &len_key)
      : gr::tagged_stream_block("TDM_FMCW_Generator",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(num_tx, num_tx, sizeof(gr_complex)),len_key),
              d_samp_rate(samp_rate),
              d_bandwidth(bandwidth),
              d_chirp_duration(chirp_duration),
              d_tdm_offset(tdm_offset),
              d_num_tx(num_tx),
              d_sample_count(0),
              d_enabled(true),
              d_len_key(pmt::string_to_symbol(len_key)),
              d_len_key_str(len_key)
    {
      if (d_chirp_duration > d_tdm_offset) 
      {
        throw std::invalid_argument("chirp_duration must be <= tdm_offset");
      }
      d_chirp_len = std::round(d_chirp_duration * d_samp_rate);
      d_slot_len  = std::round(d_tdm_offset   * d_samp_rate);
      d_period    = d_slot_len * d_num_tx;
      d_chirp.resize(d_chirp_len);

      double f0 = -d_bandwidth/2.0;
      double f1 = +d_bandwidth/2.0;
      for (int n = 0; n < d_chirp_len; ++n) 
      {
        double t = n / d_samp_rate;
        double phase = 2*M_PI*(f0*t + 0.5*(f1 - f0)/d_chirp_duration * t*t);
        d_chirp[n] = gr_complex(std::cos(phase), std::sin(phase));
      }
    }

    /*
     * Our virtual destructor.
     */

    void TDM_FMCW_Generator_impl::set_enabled(bool enabled) 
    {
      d_enabled = enabled;
    }
     
    TDM_FMCW_Generator_impl::~TDM_FMCW_Generator_impl() 
    {
      // Nothing to do here
    }

    // void
    // TDM_FMCW_Generator_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    // {
    //   /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    //   for (auto &n : ninput_items_required) n = 0;
    // }

int TDM_FMCW_Generator_impl::work(        
        int noutput_items,
    gr_vector_int             &ninput_items,
    gr_vector_const_void_star &input_items,
    gr_vector_void_star       &output_items)
    {
      // insert length tag
      pmt::pmt_t value = pmt::from_long(noutput_items);
      for (int ch = 0; ch < d_num_tx; ++ch) {
        add_item_tag(ch,
                     nitems_written(ch),
                     d_len_key,
                     value);
      }

      // FMCW TDM chirp generation
      for (int ch = 0; ch < d_num_tx; ++ch) {
        auto out = reinterpret_cast<gr_complex*>(output_items[ch]);
        if (!d_enabled) {
          std::memset(out, 0, noutput_items * sizeof(gr_complex));
        } else {
          for (int i = 0; i < noutput_items; ++i) {
            int idx  = (d_sample_count + i) % d_period;
            int slot = idx / d_slot_len;
            int pos  = idx - slot * d_slot_len;
            gr_complex v = (pos < d_chirp_len ? d_chirp[pos] : gr_complex(0,0));
            out[i] = (slot == ch ? v : gr_complex(0,0));
          }
        }
      }

      d_sample_count = (d_sample_count + noutput_items) % d_period;
      return noutput_items;
    }

  } /* namespace FMCW_MIMO */
} /* namespace gr */

