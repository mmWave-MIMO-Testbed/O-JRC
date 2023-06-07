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

#ifndef INCLUDED_MIMO_OFDM_JRC_MSG_RATIO_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_MSG_RATIO_IMPL_H

#include <mimo_ofdm_jrc/msg_ratio.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    class msg_ratio_impl : public msg_ratio
    {
     private:
      // Nothing to declare in this block.
      boost::thread d_thread;
      void handle_msg(pmt::pmt_t msg) override;
      void calculate_ratio() override;

     public:
      msg_ratio_impl();
      ~msg_ratio_impl();

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_MSG_RATIO_IMPL_H */

