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

#ifndef INCLUDED_MIMO_OFDM_JRC_GUI_HEATMAP_PLOT_H
#define INCLUDED_MIMO_OFDM_JRC_GUI_HEATMAP_PLOT_H

#include <mimo_ofdm_jrc/api.h>
#include <gnuradio/tagged_stream_block.h>

namespace gr {
  namespace mimo_ofdm_jrc {

    /*!
     * \brief <+description of block+>
     * \ingroup mimo_ofdm_jrc
     *
     */
    class MIMO_OFDM_JRC_API gui_heatmap_plot : virtual public gr::tagged_stream_block
    {
     public:
      typedef boost::shared_ptr<gui_heatmap_plot> sptr;

      /*!
       * \brief Return a shared_ptr to a new instance of mimo_ofdm_jrc::gui_heatmap_plot.
       *
       * To avoid accidental use of raw pointers, mimo_ofdm_jrc::gui_heatmap_plot's
       * constructor is in a private implementation
       * class. mimo_ofdm_jrc::gui_heatmap_plot::make is the public interface for
       * creating new instances.
       */
      static sptr make(int vlen,
                     bool digital_control,
                     const std::string& sivers_angle_log,
                     int interval,
                     std::string xlabel,
                     std::string ylabel,
                     std::string label,
                     std::vector<float> axis_x,
                     std::vector<float> axis_y,
                     float dynamic_range_db,
                     std::vector<float> x_axis_ticks,
                     std::vector<float> y_axis_ticks,
                     bool autoscale_z,
                     bool db_scale,
                     std::string len_key = "packet_len");
    };

  } // namespace mimo_ofdm_jrc
} // namespace gr

#endif /* INCLUDED_MIMO_OFDM_JRC_GUI_HEATMAP_PLOT_H */

