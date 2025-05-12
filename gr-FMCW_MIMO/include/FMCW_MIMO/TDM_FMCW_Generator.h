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

#ifndef INCLUDED_FMCW_MIMO_TDM_FMCW_GENERATOR_H
#define INCLUDED_FMCW_MIMO_TDM_FMCW_GENERATOR_H

#include <FMCW_MIMO/api.h>
#include <gnuradio/block.h>
#include <gnuradio/gr_complex.h>

namespace gr {
  namespace FMCW_MIMO {

    /*!
     * \brief FMCW TDM Source (general block): multi-TX TDM FMCW
     * \ingroup FMCW_MIMO
     *
     */
    class FMCW_MIMO_API TDM_FMCW_Generator : virtual public gr::block
    {
     public:
      typedef boost::shared_ptr<TDM_FMCW_Generator> sptr;

      /*!
        * @param samp_rate      sample (Hz)
        * @param bandwidth      bandwidth (Hz)
        * @param chirp_duration chirp duration (s)
        * @param tdm_offset     TDM guard time (s)
        * @param num_tx         number of TX channels
        */
      static sptr make(double samp_rate,
                   double bandwidth,
                   double chirp_duration,
                   double tdm_offset,
                   int    num_tx);
      /**
       * Dynamic switch
       * true=create chirp, false= 0 output
       */
      virtual void set_enabled(bool enabled) = 0;
    };

  } // namespace FMCW_MIMO
} // namespace gr

#endif /* INCLUDED_FMCW_MIMO_TDM_FMCW_GENERATOR_H */
