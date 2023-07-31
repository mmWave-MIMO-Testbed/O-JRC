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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "socket_pdu_jrc_impl.h"
#include "tcp_connection.h"
#include <boost/asio.hpp>
#include <gnuradio/io_signature.h>
#include <gnuradio/blocks/pdu.h>


namespace gr {
namespace mimo_ofdm_jrc {

socket_pdu_jrc::sptr socket_pdu_jrc::make(std::string type,
                                  std::string addr,
                                  std::string port,
                                  int MTU /*= 10000*/)
{
    return gnuradio::get_initial_sptr(new socket_pdu_jrc_impl(type, addr, port, MTU));
}

socket_pdu_jrc_impl::socket_pdu_jrc_impl(std::string type,
                                 std::string addr,
                                 std::string port,
                                 int MTU /*= 10000*/)
    : block("socket_pdu_jrc", io_signature::make(0, 0, 0), io_signature::make(0, 0, 0)),
        d_MTU(MTU),
        // d_size(MTU),
        d_enabled(false)
{
    d_rxbuf.resize(d_MTU);
    using namespace gr::blocks::pdu;
    message_port_register_in(gr::blocks::pdu::pdu_port_id());
    message_port_register_out(gr::blocks::pdu::pdu_port_id());
    message_port_register_in(pmt::mp("enable"));
    set_msg_handler(pmt::mp("enable"), [this](pmt::pmt_t msg) { this->enable_handler(msg); });

    if ((type == "UDP_SERVER") && ((addr.empty()) || (addr == "0.0.0.0"))) 
    { // Bind on all interfaces
        
        int port_num = atoi(port.c_str());
        if (port_num == 0)
            throw std::invalid_argument("gr::blocks:socket_pdu_jrc: invalid port for UDP_SERVER");
            d_udp_endpoint = boost::asio::ip::udp::endpoint(boost::asio::ip::udp::v4(), port_num);
    } else if ((type == "UDP_SERVER") || (type == "UDP_CLIENT")) {
        std::cout << "2nd " << std::endl;
        boost::asio::ip::udp::resolver resolver(d_io_service);
        boost::asio::ip::udp::resolver::query query(
            boost::asio::ip::udp::v4(),
            addr,
            port,
            boost::asio::ip::resolver_query_base::passive);

        if (type == "UDP_SERVER")
            d_udp_endpoint = *resolver.resolve(query);
        else
            d_udp_endpoint_other = *resolver.resolve(query);
    }

    if (type == "UDP_SERVER") 
    {
        d_udp_socket.reset(new boost::asio::ip::udp::socket(d_io_service, d_udp_endpoint));
        d_udp_socket->async_receive_from (
            boost::asio::buffer(d_rxbuf),
            d_udp_endpoint_other,
            boost::bind(&socket_pdu_jrc_impl::handle_udp_read,
                        this,
                        boost::asio::placeholders::error,
                        boost::asio::placeholders::bytes_transferred));

            set_msg_handler(gr::blocks::pdu::pdu_port_id(), [this](pmt::pmt_t msg) { this->udp_send(msg); });
    } else if (type == "UDP_CLIENT") 
    {
        d_udp_socket.reset(
        new boost::asio::ip::udp::socket(d_io_service, d_udp_endpoint));
        d_udp_socket->async_receive_from(
            boost::asio::buffer(d_rxbuf),
            d_udp_endpoint_other,
            boost::bind(&socket_pdu_jrc_impl::handle_udp_read,
                        this,
                        boost::asio::placeholders::error,
                        boost::asio::placeholders::bytes_transferred));

        set_msg_handler(gr::blocks::pdu::pdu_port_id(),
                        [this](pmt::pmt_t msg) { this->udp_send(msg); });
    } else
        throw std::runtime_error("gr::blocks:socket_pdu_jrc: unknown socket type");

    d_thread = gr::thread::thread(boost::bind(&socket_pdu_jrc_impl::run_io_service, this));
    d_started = true;
}

socket_pdu_jrc_impl::~socket_pdu_jrc_impl() { stop(); }

bool socket_pdu_jrc_impl::stop()
{
    if (d_started) {
        d_io_service.stop();
        d_thread.interrupt();
        d_thread.join();
    }
    d_started = false;
    return true;
}

void socket_pdu_jrc_impl::enable_handler(pmt::pmt_t msg) {
    if (pmt::is_symbol(msg)) 
    {
        std::string str_msg = pmt::symbol_to_string(msg);
        // std::cout << "Received msg: " << str_msg << std::endl;
        std::istringstream ss(str_msg);
        std::string type_str;
        std::getline(ss, type_str, '#');
        std::string size_str;
        std::getline(ss, size_str, '#');

        // std::cout << "Received type: " << type_str << std::endl;
        // std::cout << "Received size: " << size_str << std::endl;
        
        if (std::stoi(type_str) == 2)
        {
            d_enabled = true;
            d_MTU = std::stoi(size_str);
            gr::thread::scoped_lock lock(d_mutex);  // Lock to prevent race conditions
            d_rxbuf.resize(d_MTU);

        }
    }
    else
    {
        std::cerr << "Error: expected string value for enable signal" << std::endl;
    }
}

void socket_pdu_jrc_impl::handle_udp_read(const boost::system::error_code& error, size_t bytes_transferred)
{
    // std::cout << "Before d_enabled " << d_enabled << std::endl;
    if (!error) 
    {
        // std::cout << "Before d_enabled " << d_enabled << std::endl;
        if (!d_enabled) 
        {
            d_udp_socket->async_receive_from(   boost::asio::buffer(d_rxbuf),
                                                d_udp_endpoint_other,
                                                boost::bind(&socket_pdu_jrc_impl::handle_udp_read,
                                                this,
                                                boost::asio::placeholders::error,
                                                boost::asio::placeholders::bytes_transferred)
                                            );
            return;
        } 
        // std::cout << "After d_enabled " << d_enabled << std::endl;  
        
        pmt::pmt_t vector = pmt::init_u8vector(bytes_transferred, (const uint8_t*)&d_rxbuf[0]);
        pmt::pmt_t pdu = pmt::cons(pmt::PMT_NIL, vector);

        message_port_pub(gr::blocks::pdu::pdu_port_id(), pdu);

        d_udp_socket->async_receive_from(   boost::asio::buffer(d_rxbuf),
                                            d_udp_endpoint_other,
                                            boost::bind(&socket_pdu_jrc_impl::handle_udp_read,
                                            this,
                                            boost::asio::placeholders::error,
                                            boost::asio::placeholders::bytes_transferred)
                                        ); 
        d_enabled = false; // reset the enable flag
    }
}

void socket_pdu_jrc_impl::udp_send(pmt::pmt_t msg)
{      
    
    if (d_udp_endpoint_other.address().to_string() == "0.0.0.0")
        return;

    pmt::pmt_t vector = pmt::cdr(msg);
    size_t len = pmt::blob_length(vector);
    // std::cout << "len:" << len << std::endl;
    size_t offset = 0;
    std::vector<char> txbuf(std::min(len, d_rxbuf.size()));
    // std::vector<char> txbuf(d_MTU);
    // std::cout << "txbuf.size(): " << txbuf.size() << std::endl;
    while (offset < len) 
    {
        size_t send_len = std::min((len - offset), txbuf.size());
        memcpy(&txbuf[0], pmt::uniform_vector_elements(vector, offset), send_len);
        offset += send_len;
        d_udp_socket->send_to(boost::asio::buffer(txbuf, send_len), d_udp_endpoint_other);
    }
}

// void socket_pdu_jrc_impl::set_MTU(int new_MTU) {
//     gr::thread::scoped_lock lock(d_mutex);  // Lock to prevent race conditions
//     d_MTU = new_MTU;
//     d_rxbuf.resize(d_MTU);
// }

} /* namespace blocks */
} /* namespace gr */
