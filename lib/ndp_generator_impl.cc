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
#include <mutex>
#include <condition_variable>
#include <boost/date_time/posix_time/posix_time.hpp>
#include <sstream>
#include <string>


namespace gr {
  namespace mimo_ofdm_jrc {

    ndp_generator::sptr ndp_generator::make()
    {
      return gnuradio::get_initial_sptr(new ndp_generator_impl());
    }

    ndp_generator_impl::ndp_generator_impl()
      : block("ndp_generator",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)),
        d_enabled(false)
    {
      message_port_register_out(pmt::mp("out"));
      message_port_register_in(pmt::mp("enable"));
      set_msg_handler(pmt::mp("enable"), boost::bind(&ndp_generator_impl::enable_handler, this, _1));
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
        {
          std::unique_lock<std::mutex> lock(d_mutex);
          d_enabled = true;
          d_condition_variable.notify_one();
        }
      
      d_thread->interrupt();
      d_thread->join();
      return true;
    }


    void ndp_generator_impl::enable_handler(pmt::pmt_t msg)
    {
      if (pmt::is_symbol(msg))
      {
        std::string str_msg = pmt::symbol_to_string(msg);
        // std::cout << "Received msg: " << str_msg << std::endl;
        std::istringstream ss(str_msg);
        std::string type;
        std::getline(ss, type, '#');

        if (std::stoi(type) == 1)
        {
          d_enabled = true;
          std::unique_lock<std::mutex> lock(d_mutex);
          d_condition_variable.notify_one();
        }
      }
      else
      {
        std::cerr << "Error: expected string value for enable signal" << std::endl;
      }
    }


    void ndp_generator_impl::send_data()
    {
      while (true) 
      {   
        
        std::unique_lock<std::mutex> lock(d_mutex);
        d_condition_variable.wait(lock, [this] { return d_enabled; });
        
        
        const uint8_t data[] = {0x01, 0x58, 0x58};
        pmt::pmt_t vector_data = pmt::init_u8vector(3, data);
        pmt::pmt_t pdu = pmt::cons(pmt::PMT_NIL, vector_data);
        message_port_pub(pmt::mp("out"), pdu);

        d_enabled = false; // reset the enable flag

        boost::this_thread::sleep(boost::posix_time::milliseconds(5));
        
        if (boost::this_thread::interruption_requested())
        {
          break;
        }
      }
    }

  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

