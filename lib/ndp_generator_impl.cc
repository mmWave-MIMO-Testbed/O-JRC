/* -*- c++ -*- */
/*
 * Copyright 2023 The Ohio State University.
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
#include "ndp_generator_impl.h"

namespace gr {
  namespace mimo_ofdm_jrc {

    ndp_generator::sptr ndp_generator::make()
    {
      return gnuradio::get_initial_sptr(new ndp_generator_impl());
    }

    ndp_generator_impl::ndp_generator_impl()
      : block("ndp_generator",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0))
    {
      message_port_register_out(pmt::mp("out"));
    }

    ndp_generator_impl::~ndp_generator_impl()
    {
    }

    bool ndp_generator_impl::start()
    {
      d_thread = boost::shared_ptr<boost::thread>(
          new boost::thread(boost::bind(&ndp_generator_impl::send_data, this)));
      return true;
    }

    bool ndp_generator_impl::stop()
    {
      d_thread->interrupt();
      d_thread->join();
      return true;
    }

    void ndp_generator_impl::send_data()
    {
      while (true) {
        boost::this_thread::sleep(boost::posix_time::milliseconds(100));

        const uint8_t data[] = {0x01, 0x58, 0x58};
        pmt::pmt_t vector_data = pmt::init_u8vector(3, data);
        pmt::pmt_t pdu = pmt::cons(pmt::PMT_NIL, vector_data);
        message_port_pub(pmt::mp("out"), pdu);

        std::cout << "Output data: ";
        for (size_t i = 0; i < sizeof(data); ++i) {
          std::cout << std::hex << static_cast<int>(data[i]) << " ";
        }
        std::cout << std::endl;
      }
    }

  } /* namespace fake_socket_pdu */
} /* namespace gr */

