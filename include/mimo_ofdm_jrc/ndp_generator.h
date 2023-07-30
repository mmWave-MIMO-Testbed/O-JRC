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

#ifndef INCLUDED_MIMO_OFDM_JRC_NDP_GENERATOR_H
#define INCLUDED_MIMO_OFDM_JRC_NDP_GENERATOR_H

#include <mimo_ofdm_jrc/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace mimo_ofdm_jrc{

    /*!
     * \brief <+description of block+>
     * \ingroup fake_socket_pdu
     *
     */
    class MIMO_OFDM_JRC_API ndp_generator : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<ndp_generator> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of fake_socket_pdu::fake_socket_pdu_src.
       *
       * To avoid accidental use of raw pointers, fake_socket_pdu::fake_socket_pdu_src's
       * constructor is in a private implementation
       * class. fake_socket_pdu::fake_socket_pdu_src::make is the public interface for
       * creating new instances.
       */
      static sptr make();
    };

  } // namespace fake_socket_pdu
} // namespace gr

#endif /* INCLUDED_FAKE_SOCKET_PDU_SRC_H */

