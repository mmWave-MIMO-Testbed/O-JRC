/* -*- c++ -*- */
/*
 * Copyright 2023 Ohio State University.
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

#ifndef INCLUDED_MIMO_OFDM_JRC_SOCKET_PDU_JRC_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_SOCKET_PDU_JRC_IMPL_H

#include "tcp_connection.h"
#include <mimo_ofdm_jrc/socket_pdu_jrc.h>
#include <gnuradio/thread/thread.h> // Add this include to access the mutex class

namespace gr {
namespace mimo_ofdm_jrc {

class socket_pdu_jrc_impl : public socket_pdu_jrc
{
private:
    boost::asio::io_service d_io_service;
    std::vector<char> d_rxbuf;
    void run_io_service() { d_io_service.run(); }
    gr::thread::thread d_thread;
    bool d_started;

    // TCP specific
    boost::asio::ip::tcp::endpoint d_tcp_endpoint;
    std::vector<tcp_connection::sptr> d_tcp_connections;
    void handle_tcp_read(const boost::system::error_code& error,
                         size_t bytes_transferred);
    bool d_tcp_no_delay;

    // TCP server specific
    boost::shared_ptr<boost::asio::ip::tcp::acceptor> d_acceptor_tcp;
    void start_tcp_accept();
    void tcp_server_send(pmt::pmt_t msg);
    void handle_tcp_accept(tcp_connection::sptr new_connection,
                           const boost::system::error_code& error);

    // TCP client specific
    boost::shared_ptr<boost::asio::ip::tcp::socket> d_tcp_socket;
    void tcp_client_send(pmt::pmt_t msg);

    // UDP specific
    boost::asio::ip::udp::endpoint d_udp_endpoint;
    boost::asio::ip::udp::endpoint d_udp_endpoint_other;
    boost::shared_ptr<boost::asio::ip::udp::socket> d_udp_socket;
    void handle_udp_read(const boost::system::error_code& error,
                         size_t bytes_transferred);
    void udp_send(pmt::pmt_t msg);

    //////////////////////////
    int d_MTU;
    gr::thread::mutex d_mutex; // Add this line
    //////////////////////////

public:
    socket_pdu_jrc_impl(std::string type,
                    std::string addr,
                    std::string port,
                    int MTU = 200,
                    bool tcp_no_delay = false);
    ~socket_pdu_jrc_impl();
    bool stop();

    //////////////////////////
    void set_MTU(int new_MTU); // Add this line
    //////////////////////////
};

} /* namespace blocks */
} /* namespace gr */

#endif /* INCLUDED_BLOCKS_SOCKET_PDU_IMPL_H */
