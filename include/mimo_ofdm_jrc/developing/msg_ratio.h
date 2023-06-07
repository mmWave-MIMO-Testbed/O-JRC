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

#ifndef INCLUDED_MIMO_OFDM_JRC_MSG_RATIO_H
#define INCLUDED_MIMO_OFDM_JRC_MSG_RATIO_H

#include <mimo_ofdm_jrc/api.h>
#include <gnuradio/block.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    /*!
     * \brief <+description of block+>
     * \ingroup mimo_ofdm_jrc
     *
     */
    class MIMO_OFDM_JRC_API msg_ratio : public gr::block
    {
     protected:
      int count_1, count_2;
      msg_ratio();
      void set_counts();
     
     public:
      
      msg_ratio(const std::string &name);
      typedef boost::shared_ptr<msg_ratio> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of mimo_ofdm_jrc::msg_ratio.
       *
       * To avoid accidental use of raw pointers, mimo_ofdm_jrc::msg_ratio's
       * constructor is in a private implementation
       * class. mimo_ofdm_jrc::msg_ratio::make is the public interface for
       * creating new instances.
       */
      static sptr make();
      
      virtual void handle_msg(pmt::pmt_t msg) = 0;
      virtual void calculate_ratio() = 0;
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_MSG_RATIO_H */

