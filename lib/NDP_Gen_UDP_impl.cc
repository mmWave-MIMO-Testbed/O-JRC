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
#include "NDP_Gen_UDP_impl.h"

namespace gr {
  namespace mimo_ofdm_jrc {

    NDP_Gen_UDP::sptr
    NDP_Gen_UDP::make()
    {
      return gnuradio::get_initial_sptr
        (new NDP_Gen_UDP_impl());
    }


    /*
     * The private constructor
     */
    NDP_Gen_UDP_impl::NDP_Gen_UDP_impl(const std::string& host, int port, int interval)
      : gr::block("NDP_Gen_UDP",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)),
        d_socket(d_io_context),
        d_interval(interval)
    {
      /*
      d_data.resize(3);
      d_data[0]=static_cast<char>(PACKET_TYPE::NDP);
      std::fill_n(d_data.begin()+1, d_data.size()-1, 'X');
      d_udp_sink = gr::udp_sink::make(sizeof(char),host,port);*/
      
      boost::asio::ip::udp::resolver resolver(d_io_context);
      auto endpoints = resolver.resolve(boost::asio::ip::udp::v4(), host, std::to_string(port));
      d_remote_endpoint = *endpoints.begin();
    }

    /*
     * Our virtual destructor.
     */
    NDP_Gen_UDP_impl::~NDP_Gen_UDP_impl()
    {
    }

    void
    NDP_Gen_UDP_impl::forecast (int noutput_items, gr_vector_int &ninput_items_required)
    {
      /* <+forecast+> e.g. ninput_items_required[0] = noutput_items */
    }

    int
    NDP_Gen_UDP_impl::general_work (int noutput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
      // Do <+signal processing+>
      // Tell runtime system how many input items we consumed on
      // each input stream.
      
      /*
      d_udp_sink ->send(d_data.data(),d_data.size());
      boost::this_thread::sleep(boost::posix_time::microseconds(d_interval * 1000));

      consume_each (noutput_items);*/

      for (int i = 0; i < noutput_items; i++) {
        // 创建要发送的数据包
        std::vector<char> ndpCharArr(3);
        ndpCharArr[0] = (char) PACKET_TYPE::NDP;
        std::fill_n(ndpCharArr.begin()+1, ndpCharArr.size()-1, 'X');
        boost::asio::const_buffer buffer(ndpCharArr.data(), ndpCharArr.size());

        // 发送数据包
        d_socket.send_to(buffer, d_remote_endpoint);

        // 等待一段时间
        std::this_thread::sleep_for(std::chrono::microseconds((int)(d_interval*1000)));

      // Tell runtime system how many output items we produced.
      return noutput_items;
    }
    }
  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

