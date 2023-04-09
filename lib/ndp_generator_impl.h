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

#ifndef INCLUDED_MIMO_OFDM_JRC_NDP_GENERATOR_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_NDP_GENERATOR_IMPL_H

#include <mimo_ofdm_jrc/ndp_generator.h>
#include <boost/shared_ptr.hpp>
#include <boost/thread.hpp>
#include <mutex>
#include <condition_variable>

namespace gr {
  namespace mimo_ofdm_jrc {

    class ndp_generator_impl : public ndp_generator
    {
     private:
      boost::shared_ptr<boost::thread> d_thread;
      std::mutex d_mutex;
      std::condition_variable d_condition_variable;
      void send_data();
      void enable_handler(pmt::pmt_t msg);
      bool d_enabled;

     public:
      ndp_generator_impl();
      ~ndp_generator_impl();

      bool start();
      bool stop();
    };

  } // namespace fake_socket_pdu
} // namespace gr

#endif /* INCLUDED_ndp_generator_IMPL_H */


