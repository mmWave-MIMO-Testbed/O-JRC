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

#ifndef INCLUDED_MIMO_OFDM_JRC_NDP_GEN_UDP_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_NDP_GEN_UDP_IMPL_H

#include <mimo_ofdm_jrc/NDP_Gen_UDP.h>
#include <boost/asio.hpp>

namespace gr {
  namespace mimo_ofdm_jrc {

    enum class PAKCET_TYPE {NDP, DATA};
    class NDP_Gen_UDP_impl : public NDP_Gen_UDP
    {
     private:
      boost::asio::io_context d_io_context;
      boost::asio::ip::udp::socket d_socket;
      boost::asio::ip::udp::endpoint d_remote_endpoint;
      std::vector<char> d_data;
      std::vector<char> d_ndpCharArr;
      int d_interval;

     public:
     NDP_Gen_UDP_impl(const std::string& host, int port, int interval);
     ~NDP_Gen_UDP_impl();
     
     //typedef std::shared_ptr<NDP_Gen_UDP_impl> sptr;
     //static sptr make(const std::string& host, int port, int interval);

      int work(int noutput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_NDP_GEN_UDP_IMPL_H */

