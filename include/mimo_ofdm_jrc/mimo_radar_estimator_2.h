/* -*- c++ -*- */
/*
 * Copyright 2022 gr-mimo_ofdm_jrc author.
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

#ifndef INCLUDED_MIMO_OFDM_JRC_MIMO_RADAR_ESTIMATOR_2_H
#define INCLUDED_MIMO_OFDM_JRC_MIMO_RADAR_ESTIMATOR_2_H

#include <mimo_ofdm_jrc/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    /*!
     * \brief <+description of block+>
     * \ingroup mimo_ofdm_jrc
     *
     */
    class MIMO_OFDM_JRC_API mimo_radar_estimator_2 : virtual public gr::tagged_stream_block
    {
     public:
      typedef boost::shared_ptr<mimo_radar_estimator_2> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of mimo_ofdm_jrc::mimo_radar_estimator_2.
       *
       * To avoid accidental use of raw pointers, mimo_ofdm_jrc::mimo_radar_estimator_2's
       * constructor is in a private implementation
       * class. mimo_ofdm_jrc::mimo_radar_estimator_2::make is the public interface for
       * creating new instances.
       */
      static sptr make(int fft_len,
                        int N_tx,
                        int N_rx,
                        int N_sym,
                        int N_pre,
                        bool background_removal,
                        bool background_recording,
                        int record_len,
                        int interp_factor,
                        bool enable_tx_interleave,
                        const std::string& len_tag_key = "packet_len",
                        bool debug = false);
      virtual void set_background_record(bool background_record) = 0;
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_MIMO_RADAR_ESTIMATOR_2_H */

