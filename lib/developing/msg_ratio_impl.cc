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
#include "msg_ratio_impl.h"

namespace gr {
  namespace mimo_ofdm_jrc {

    msg_ratio::sptr
    msg_ratio::make()
    {
      return gnuradio::get_initial_sptr
        (new msg_ratio_impl());
    }


    /*
     * The private constructor
     */

    msg_ratio::msg_ratio(const std::string &name)
    : gr::block(name,
      gr::io_signature::make(0, 0, 0),
      gr::io_signature::make(0, 0, 0))
    {
      set_counts();
    }

    void msg_ratio::set_counts()
    {
      count_1 = 0;
      count_2 = 0;
    }

    msg_ratio_impl::msg_ratio_impl()
      : msg_ratio("msg_ratio")

    {
      message_port_register_in(pmt::mp("in"));
      set_msg_handler(pmt::mp("in"), boost::bind(&msg_ratio_impl::handle_msg, this, _1));

      // Using a gnuradio timer
      d_thread = gr::thread::thread(boost::bind(&msg_ratio_impl::calculate_ratio, this));
    }

    /*
     * Our virtual destructor.
     */
    msg_ratio_impl::~msg_ratio_impl()
    {
      d_thread.interrupt();
      d_thread.join();
    }

    void
    msg_ratio_impl::handle_msg(pmt::pmt_t msg)
    {
      int value = pmt::to_long(msg);
      if (value == 1)
        count_1++;
      else if (value == 2)
        count_2++;
    }

    void
    msg_ratio_impl::calculate_ratio()
    {
      while(1)
      {
        boost::this_thread::sleep(boost::posix_time::seconds(1));

        if(count_1+count_2 > 0) {
          float ratio = static_cast<float>(count_1) / (count_1 + count_2);
          message_port_pub(pmt::mp("out"), pmt::from_float(ratio));
        }
        
        count_1 = 0;
        count_2 = 0;
      }   
    }
  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

