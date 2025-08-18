/* -*- c++ -*- */
/*
 * Copyright 2025 HaochengZhu.
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

#ifndef INCLUDED_MIMO_OFDM_JRC_COMM_TARGET_SIMULATOR_H
#define INCLUDED_MIMO_OFDM_JRC_COMM_TARGET_SIMULATOR_H

#include <mimo_ofdm_jrc/api.h>
#include <gnuradio/sync_block.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    /*!
     * \brief <+description of block+>
     * \ingroup mimo_ofdm_jrc
     *
     */
    class MIMO_OFDM_JRC_API comm_target_simulator : virtual public gr::sync_block
    {
     public:
      typedef boost::shared_ptr<comm_target_simulator> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of mimo_ofdm_jrc::comm_target_simulator.
       *
       * To avoid accidental use of raw pointers, mimo_ofdm_jrc::comm_target_simulator's
       * constructor is in a private implementation
       * class. mimo_ofdm_jrc::comm_target_simulator::make is the public interface for
       * creating new instances.
       * input：num_tx；output：1 complex stream
       * coefficients： (λ / 4πR) * exp(j * k * base * sin(theta)), base=π or 2π
       * hot update via message port "cfg": theta_deg (degrees), distance_m (meters)
       */
      static sptr make(int num_tx,
                     double center_freq_hz,
                     double min_distance_m = 1e-2,
                     bool use_two_pi = false);

          // optional: manually set
      virtual void set_theta_deg(double th_deg) = 0;
      virtual void set_distance_m(double dist_m) = 0;
      virtual void set_center_freq(double fc_hz) = 0;
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_COMM_TARGET_SIMULATOR_H */

