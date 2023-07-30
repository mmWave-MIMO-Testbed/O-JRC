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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "packet_switch_impl.h"
#include <gnuradio/io_signature.h>
#include <errno.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <cstdio>
#include <iostream>
#include <stdexcept>
#include <fstream>
#include <sstream>

namespace gr {
namespace mimo_ofdm_jrc {

packet_switch::sptr packet_switch::make(    long period_ms, 
                                            const std::string& packet_info_file )
{
    return gnuradio::get_initial_sptr(new packet_switch_impl(   period_ms, 
                                                                packet_info_file    ));
}

packet_switch_impl::packet_switch_impl( long period_ms,
                                        const std::string& packet_info_file )
    :   gr::block("packet_switch", gr::io_signature::make(0, 0, 0), gr::io_signature::make(0, 0, 0)),
        d_period_ms(period_ms),
        d_packet_info_file(packet_info_file),
        d_finished(false),
        d_current_time("00:00:00:000"),
        d_last_time("xx:xx:xx:xxx"),
        d_type("0"),
        d_size("50"),
        d_msg(pmt::PMT_NIL),
        d_port(pmt::mp("strobe"))
{
    message_port_register_out(d_port);
}

packet_switch_impl::~packet_switch_impl() {}

bool packet_switch_impl::start()
{
    d_finished = false;
    d_thread = boost::shared_ptr<gr::thread::thread>(new gr::thread::thread(boost::bind(&packet_switch_impl::run, this)));
    return block::start();
}

bool packet_switch_impl::stop()
{
    // Shut down the thread
    d_finished = true;
    d_thread->interrupt();
    d_thread->join();
    return block::stop();
}

std::vector<std::string> packet_switch_impl::split(const std::string &s, char delimiter)
{
    std::vector<std::string> tokens;
    std::string token;
    std::istringstream tokenStream(s);
    while (std::getline(tokenStream, token, delimiter))
    {
        tokens.push_back(token);
    }
    return tokens;
}


void packet_switch_impl::read_packet_info()
{
    std::ifstream file(d_packet_info_file.c_str(), std::ifstream::in);
    std::string line;
    line.clear(); 
    if (std::getline(file, line) && line.size() > 0)
    {
        std::vector<std::string> data = split(line, ',');
        if (data.size() == 3) 
        { 
            d_current_time = data[0];
            d_type = data[1];
            d_size = data[2];
        }
    }
    file.close();
}

void packet_switch_impl::run()
{
    while (!d_finished) 
    {
        boost::this_thread::sleep(boost::posix_time::milliseconds(static_cast<long>(d_period_ms)));
        if (d_finished) 
        {
            return;
        }

        read_packet_info();

        if(d_current_time.compare(d_last_time) != 0) 
        {
            std::string msg = d_type + "#" + d_size;
            d_msg = pmt::string_to_symbol(msg);
            message_port_pub(d_port, d_msg);
            d_last_time = d_current_time;
        }
        else
        {
            continue;
        }  
    }
}

}
}

