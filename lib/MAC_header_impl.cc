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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "MAC_header_impl.h"

namespace gr {
  namespace mimo_ofdm_jrc {

    MAC_header::sptr
    MAC_header::make(const std::vector<uint8_t> &addr1,
                     const std::vector<uint8_t> &addr2,
                     const std::vector<uint8_t> &addr3)
    {
      return gnuradio::get_initial_sptr
        (new MAC_header_impl(addr1, addr2, addr3));
    }


    /*
     * The private constructor
     */
    MAC_header_impl::MAC_header_impl(const std::vector<uint8_t> &addr1,
                                     const std::vector<uint8_t> &addr2,
                                     const std::vector<uint8_t> &addr3)
      : gr::block("MAC_header",
              gr::io_signature::make(0, 0, 0),
              gr::io_signature::make(0, 0, 0)),
        d_sequence_number(0),
        d_addr1(addr1), d_addr2(addr2), d_addr3(addr3)  // init address
    {
      if (d_addr1.size() != 6 || d_addr2.size() != 6 || d_addr3.size() != 6) {
        throw std::invalid_argument("MAC addresses must be 6 bytes long");
      }
      
      message_port_register_in(pmt::mp("pdu_in"));
      message_port_register_out(pmt::mp("pdu_in"));
    }

    /*
     * Our virtual destructor.
     */
    MAC_header_impl::~MAC_header_impl()
    {
    }

    // set address
    void MAC_header_impl::set_addr1(const std::vector<uint8_t> &addr1) {
      if (addr1.size() == 6) {
        d_addr1 = addr1;
      } else {
        throw std::invalid_argument("addr1 must be 6 bytes");
      }
    }

    void MAC_header_impl::set_addr2(const std::vector<uint8_t> &addr2) {
      if (addr2.size() == 6) {
        d_addr2 = addr2;
      } else {
        throw std::invalid_argument("addr2 must be 6 bytes");
      }
    }

    void MAC_header_impl::set_addr3(const std::vector<uint8_t> &addr3) {
      if (addr3.size() == 6) {
        d_addr3 = addr3;
      } else {
        throw std::invalid_argument("addr3 must be 6 bytes");
      }
    }

    int
    MAC_header_impl::general_work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const char *in = (const char *) input_items[0];
        char *out = (char *) output_items[0];

        // define MAC header structure
        struct mac_header_t {
            uint16_t frame_control;
            uint16_t duration;
            uint8_t addr1[6];  // Destination Address
            uint8_t addr2[6];  // Source Address
            uint8_t addr3[6];  // BSSID
            uint16_t seq_control;  // Sequence Control
            uint8_t beamforming_control[4];  // reserved beamforming control field, 4 bytes
        };

        // create MAC header and initialize
        mac_header_t mac_header;
        mac_header.frame_control = 0x0801;  // example Frame Control
        mac_header.duration = 0x003c;       // example Duration

        // set address
        std::memcpy(mac_header.addr1, d_addr1.data(), 6);  // Destination Address
        std::memcpy(mac_header.addr2, d_addr2.data(), 6);  // Source Address
        std::memcpy(mac_header.addr3, d_addr3.data(), 6);  // BSSID
        //std::memcpy(mac_header.addr4, d_addr4.data(),6); // Reserved address for wireless direbution system

        // sequence number and fragment number(default: 0)
        mac_header.seq_control = (d_sequence_number & 0xfff) << 4;  // sequence number
        d_sequence_number = (d_sequence_number + 1) % 4096;  // increment

        std::memcpy(mac_header.beamforming_control, "\x01\x02\x03\x04", 4);  // beamforming control, 4 bytes, read from data

        // need a function to read info from pdu_input
        // set value to destination address
        // set beamforming control field info
        // beamforming packet type (TX/RX), beamforming index
        
        // {
        // // save bit_value (0 (TX) or 1 (RX)) to beamforming_control first bype
        // mac_header.beamforming_control[0] = bit_value & 0x01;
        // // save number (0-100) to beamforming_control second byte
        // mac_header.beamforming_control[1] = number & 0xFF;  // range from 0 to 255 maximum

        // // reserve（beamforming_control[2], beamforming_control[3])
        // mac_header.beamforming_control[2] = 0;  // reserve
        // mac_header.beamforming_control[3] = 0;  // reserve
        // }

        // add MAC header to mem
        std::memcpy(out, &mac_header, sizeof(mac_header_t));

        // add data after MAC header
        std::memcpy(out + sizeof(mac_header_t), in, ninput_items[0]);

        // calculate the total length
        int total_length = sizeof(mac_header_t) + ninput_items[0];

        //convert to PMT Blob
        pmt::pmt_t pdu_data = pmt::make_blob(out, total_length);
        pmt::pmt_t pdu_msg = pmt::cons(pmt::PMT_NIL, pdu_data);

        // convert to PDU
        message_port_pub(pmt::mp("pdu_out"), pdu_msg);


        consume_each(ninput_items[0]);
        return 0;
    }

  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

