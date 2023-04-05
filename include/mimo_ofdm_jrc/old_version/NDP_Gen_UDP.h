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

#ifndef INCLUDED_MIMO_OFDM_JRC_NDP_GEN_UDP_H
#define INCLUDED_MIMO_OFDM_JRC_NDP_GEN_UDP_H

#include <mimo_ofdm_jrc/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    /*!
     * \brief <+description of block+>
     * \ingroup mimo_ofdm_jrc
     *
     */
    class MIMO_OFDM_JRC_API NDP_Gen_UDP : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<NDP_Gen_UDP> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of mimo_ofdm_jrc::NDP_Gen_UDP.
       *
       * To avoid accidental use of raw pointers, mimo_ofdm_jrc::NDP_Gen_UDP's
       * constructor is in a private implementation
       * class. mimo_ofdm_jrc::NDP_Gen_UDP::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::string& host, int port, int interval);

    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_NDP_GEN_UDP_H */

