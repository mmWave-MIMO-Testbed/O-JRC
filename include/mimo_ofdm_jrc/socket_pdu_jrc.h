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

#ifndef INCLUDED_MIMO_OFDM_JRC_SOCKET_PDU_JRC_H
#define INCLUDED_MIMO_OFDM_JRC_SOCKET_PDU_JRC_H

#include <gnuradio/block.h>
#include <mimo_ofdm_jrc/api.h>


namespace gr {
  namespace mimo_ofdm_jrc {

    /*!
     * \brief <+description of block+>
     * \ingroup mimo_ofdm_jrc
     *
     */

    class MIMO_OFDM_JRC_API socket_pdu_jrc : virtual public gr::block
    {
    public:
        // gr::network::socket_pdu::sptr
        typedef boost::shared_ptr<socket_pdu_jrc> sptr;

        /*!
        * \brief Construct a SOCKET PDU interface
        * \param type "TCP_SERVER", "TCP_CLIENT", "UDP_SERVER", or "UDP_CLIENT"
        * \param addr network address to use
        * \param port network port to use
        * \param MTU maximum transmission unit
        */
        static sptr make(std::string type,
                        std::string addr,
                        std::string port,
                        int MTU);
    };

  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

#endif /* INCLUDED_MIMO_OFDM_JRC_SOCKET_PDU_JRC_H */

