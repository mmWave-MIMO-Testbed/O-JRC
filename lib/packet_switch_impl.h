/* -*- c++ -*- */
/*
 * Copyright 2012-2013 Free Software Foundation, Inc.
 *
 * This file is part of GNU Radio
 *
 * GNU Radio is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3, or (at your option)
 * any later version.
 *
 * GNU Radio is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with GNU Radio; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 51 Franklin Street,
 * Boston, MA 02110-1301, USA.
 */

#ifndef INCLUDED_MIMO_OFDM_JRC_PACKET_SWITCH_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_PACKET_SWITCH_IMPL_H

#include <mimo_ofdm_jrc/packet_switch.h>


namespace gr {
namespace mimo_ofdm_jrc {

class packet_switch_impl : public packet_switch
{
private:
    long d_period_ms;
    std::string d_packet_info_file;
    bool d_finished;
    boost::shared_ptr<gr::thread::thread> d_thread;
    std::string d_current_time;
    std::string d_last_time;
    std::string d_type;
    std::string d_size;
    pmt::pmt_t d_msg;
    const pmt::pmt_t d_port;

    std::vector<std::string> split(const std::string &s, char delimiter);

    void read_packet_info();

    

public:
    packet_switch_impl(long period_ms, const std::string& packet_info_file);
    ~packet_switch_impl();

    bool start();
    
    bool stop();

    void run();
};

} /* namespace mimo_ofdm_jrc */
} /* namespace gr */

#endif /* INCLUDED_MIMO_OFDM_JRC_PACKET_SWITCH_IMPL_H */

