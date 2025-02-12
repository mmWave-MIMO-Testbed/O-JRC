/* -*- c++ -*- */
/*
 * Copyright 2024 gr-mimo_ofdm_jrc author.
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

#ifndef INCLUDED_MIMO_OFDM_JRC_MAC_HEADER_H
#define INCLUDED_MIMO_OFDM_JRC_MAC_HEADER_H

#include <mimo_ofdm_jrc/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    /*!
     * \brief <+description of block+>
     * \ingroup mimo_ofdm_jrc
     *
     */
    class MIMO_OFDM_JRC_API MAC_header : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<MAC_header> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of mimo_ofdm_jrc::MAC_header.
       *
       * To avoid accidental use of raw pointers, mimo_ofdm_jrc::MAC_header's
       * constructor is in a private implementation
       * class. mimo_ofdm_jrc::MAC_header::make is the public interface for
       * creating new instances.
       */
      static sptr make(const std::vector<uint8_t> &addr1,
                       const std::vector<uint8_t> &addr2,
                       const std::vector<uint8_t> &addr3);

      virtual void set_addr1(const std::vector<uint8_t> &addr1)= 0;
      virtual void set_addr2(const std::vector<uint8_t> &addr2)= 0;
      virtual void set_addr3(const std::vector<uint8_t> &addr3)= 0;
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_MAC_HEADER_H */

