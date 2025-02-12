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

#ifndef INCLUDED_MIMO_OFDM_JRC_MAC_HEADER_IMPL_H
#define INCLUDED_MIMO_OFDM_JRC_MAC_HEADER_IMPL_H

#include <mimo_ofdm_jrc/MAC_header.h>
#include <vector>
#include <pmt/pmt.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    class MAC_header_impl : public MAC_header
    {
     private:
      uint16_t d_sequence_number; // sequence number
      std::vector<uint8_t> d_addr1; // Destination Address
      std::vector<uint8_t> d_addr2; // Source Address
      std::vector<uint8_t> d_addr3; // BSSID

     public:
      MAC_header_impl(const std::vector<uint8_t> &addr1,
                      const std::vector<uint8_t> &addr2,
                      const std::vector<uint8_t> &addr3);
      ~MAC_header_impl();
      
      // set address
      void set_addr1(const std::vector<uint8_t> &addr1);
      void set_addr2(const std::vector<uint8_t> &addr2);
      void set_addr3(const std::vector<uint8_t> &addr3);

      int general_work(int noutput_items,
           gr_vector_int &ninput_items,
           gr_vector_const_void_star &input_items,
           gr_vector_void_star &output_items);

    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_MAC_HEADER_IMPL_H */

