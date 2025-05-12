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

#ifndef INCLUDED_FMCW_MIMO_FMCW_RADAR_H
#define INCLUDED_FMCW_MIMO_FMCW_RADAR_H

#include <FMCW_MIMO/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace FMCW_MIMO {

    /*!
     * \brief <+description of block+>
     * \ingroup FMCW_MIMO
     *
     */
    class FMCW_MIMO_API FMCW_Radar : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<FMCW_Radar> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of FMCW_MIMO::FMCW_Radar.
       *
       * To avoid accidental use of raw pointers, FMCW_MIMO::FMCW_Radar's
       * constructor is in a private implementation
       * class. FMCW_MIMO::FMCW_Radar::make is the public interface for
       * creating new instances.
       */
      static sptr make(int fft_len,
        int N_tx,
        int N_rx,
        const std::string& len_tag_key = "packet_len");
    };

  } // namespace FMCW_MIMO
} // namespace gr

#endif /* INCLUDED_FMCW_MIMO_FMCW_RADAR_H */

