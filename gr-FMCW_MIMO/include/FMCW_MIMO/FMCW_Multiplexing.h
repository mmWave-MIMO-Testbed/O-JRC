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

#ifndef INCLUDED_FMCW_MIMO_FMCW_MULTIPLEXING_H
#define INCLUDED_FMCW_MIMO_FMCW_MULTIPLEXING_H

#include <FMCW_MIMO/api.h>
#include <gnuradio/tagged_stream_block.h>
#include <gnuradio/gr_complex.h>

namespace gr {
  namespace FMCW_MIMO {

    /*!
     *
     * \brief FMCW TDM Source (general block): 多路 TDM FMCW 扫频源，带开关控制
     * \ingroup FMCW_MIMO
     *
     */
    class FMCW_MIMO_API FMCW_Multiplexing : virtual public gr::tagged_stream_block
    {
     public:
      typedef boost::shared_ptr<FMCW_Multiplexing> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of FMCW_MIMO::FMCW_Multiplexing.
       *
       * To avoid accidental use of raw pointers, FMCW_MIMO::FMCW_Multiplexing's
       * constructor is in a private implementation
       * class. FMCW_MIMO::FMCW_Multiplexing::make is the public interface for
       * creating new instances.
       */
      static sptr make(int N_tx, bool multiplexing_type, float TDM_delay, 
        const std::string& len_key="packet_len");
    };

  } // namespace FMCW_MIMO
} // namespace gr

#endif /* INCLUDED_FMCW_MIMO_FMCW_MULTIPLEXING_H */

