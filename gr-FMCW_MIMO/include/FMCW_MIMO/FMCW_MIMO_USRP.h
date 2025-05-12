/* -*- c++ -*- */
/*
 * Copyright 2025 Haocheng Zhu.
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

#ifndef INCLUDED_FMCW_MIMO_FMCW_MIMO_USRP_H
#define INCLUDED_FMCW_MIMO_FMCW_MIMO_USRP_H

#include <FMCW_MIMO/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
  namespace FMCW_MIMO {

    /*!
     * \brief <+description of block+>
     * \ingroup FMCW_MIMO
     *
     */
    class FMCW_MIMO_API FMCW_MIMO_USRP : virtual public gr::tagged_stream_block
    {
     public:
      typedef boost::shared_ptr<FMCW_MIMO_USRP> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of FMCW_MIMO::FMCW_MIMO_USRP.
       *
       * To avoid accidental use of raw pointers, FMCW_MIMO::FMCW_MIMO_USRP's
       * constructor is in a private implementation
       * class. FMCW_MIMO::FMCW_MIMO_USRP::make is the public interface for
       * creating new instances.
       */
      static sptr make(int N_mboard, int N_tx, int N_rx, int samp_rate, float center_freq, int num_delay_samps, bool debug,  float update_period,
        std::string args, std::string clock_sources, std::string time_sources, 
        std::string antenna_tx, float gain_tx, float timeout_tx, float wait_tx, std::string wire_tx, 
        std::string antenna_rx, float gain_rx, float timeout_rx, float wait_rx, float lo_offset_rx, std::string wire_rx, 
        const std::string& len_key="packet_len");

        virtual void set_num_delay_samps(int num_samps) = 0;
        virtual void set_rx_gain(float gain) = 0;
        virtual void set_tx_gain(float gain) = 0;
    };

  } // namespace FMCW_MIMO
} // namespace gr

#endif /* INCLUDED_FMCW_MIMO_FMCW_MIMO_USRP_H */

