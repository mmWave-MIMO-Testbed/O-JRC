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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "mimo_radar_estimator_2_impl.h"

namespace gr {
namespace mimo_ofdm_jrc {

    mimo_radar_estimator_2::sptr
    mimo_radar_estimator_2::make(int fft_len,
                                    int N_tx,
                                    int N_rx,
                                    int N_sym,
                                    int N_pre,
                                    bool background_removal,
                                    bool background_recording,
                                    int record_len,
                                    int interp_factor,
                                    bool enable_tx_interleave,
                                    const std::string& len_tag_key,
                                    bool debug)
    {
      return gnuradio::get_initial_sptr
        (new mimo_radar_estimator_2_impl(fft_len,
                                            N_tx,
                                            N_rx,
                                            N_sym,
                                            N_pre,
                                            background_removal,
                                            background_recording,
                                            record_len,
                                            interp_factor,
                                            enable_tx_interleave,
                                            len_tag_key,
                                            debug));
    }


    /*
     * The private constructor
     */
    mimo_radar_estimator_2_impl::mimo_radar_estimator_2_impl(
                int fft_len,
				int N_tx,
				int N_rx,
				int N_sym,
                int N_pre,
                bool background_removal,
                bool background_recording,
                int record_len,
                int interp_factor,
                bool enable_tx_interleave,
				const std::string& len_tag_key,
                bool debug
    )
      : gr::tagged_stream_block("mimo_radar_estimator_2",
                gr::io_signature::make(N_tx+N_rx, N_tx+N_rx, sizeof(gr_complex) * fft_len),
                gr::io_signature::make(1, 1, sizeof(gr_complex) * fft_len * interp_factor), len_tag_key),
                    d_fft_len(fft_len),
                    d_N_tx(N_tx),
                    d_N_rx(N_rx),
                    d_N_sym(N_sym),
                    d_N_pre(N_pre),
                    d_background_removal(background_removal),
                    d_background_recording(background_recording),
                    d_record_len(record_len),
                    d_interp_factor(interp_factor),
                    d_enable_tx_interleave(enable_tx_interleave),
                    d_debug(debug)
    {
        //TODO Add sanity checks!
        radar_chan_est = new gr_complex[d_N_tx*d_N_rx*d_fft_len];

        // radar_chan_est_buffer.resize(d_record_len);
        // for (int i = 0; i < d_record_len; ++i)
        //     radar_chan_est_buffer[i].resize(d_fft_len*d_N_tx*d_N_rx);

        radar_chan_est_buffer.set_capacity(d_record_len);
        radar_chan_est_temp.resize(d_N_tx*d_N_rx*d_fft_len);

        set_tag_propagation_policy(TPP_DONT); // does not apply on stream tags!
    }

    /*
     * Our virtual destructor.
     */
    mimo_radar_estimator_2_impl::~mimo_radar_estimator_2_impl()
    {
        
    }

    int
    mimo_radar_estimator_2_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
    {
        // int nin0 = ninput_items[0];
        int nin_rx0 = ninput_items[d_N_tx];

        int noutput_items = d_N_rx*d_N_tx;

        if (nin_rx0 == 0)
        {
            return 0;
        }
        else
        {
            return noutput_items;
        }
    }

    int
    mimo_radar_estimator_2_impl::work (int noutput_items,
                       gr_vector_int &ninput_items,
                       gr_vector_const_void_star &input_items,
                       gr_vector_void_star &output_items)
    {
        const gr_complex *in_tx;
        const gr_complex *in_rx;

        // const gr_complex* in = reinterpret_cast<const gr_complex*>(input_items[0]);
        gr_complex* out = (gr_complex *) output_items[0];

        dout << "================================================================================" << std::endl;        
        dout << "[MIMO RADAR]: input_items.size: " << input_items.size() << std::endl;
        dout << "[MIMO RADAR]: ninput_items tx0: " << ninput_items[0] << std::endl;
        dout << "[MIMO RADAR]: ninput_items rx0: " << ninput_items[d_N_tx] << std::endl;
        dout << "[MIMO RADAR]: nitems_read tx0: " << nitems_read(0) << std::endl;
        dout << "[MIMO RADAR]: nitems_read rx0: " << nitems_read(d_N_tx) << std::endl;
        dout << "[MIMO RADAR]: noutput_items: " << noutput_items << std::endl;

        std::vector<tag_t> tags;
        get_tags_in_range(tags, d_N_tx, nitems_read(d_N_tx), nitems_read(d_N_tx) + ninput_items[d_N_tx], pmt::mp("rx_time"));
        if (tags.size() != 1) {
            dout << "[MIMO RADAR]: no rx_time tag found! " << std::endl;
        }else
        {
            dout << "[MIMO RADAR]: rx_time: " << pmt::to_double(tags[0].value) << std::endl;
        }


        // MCS mcs = (MCS)pmt::to_long(tags[0].value);
        // dout << "[MIMO PRECODER] MCS from encoder: " << mcs << std::endl;

        // for (int i_tx = 0; i_tx < d_N_tx; i_tx++)
        // {
        //     in = reinterpret_cast<const gr_complex*>(input_items[i_tx]);
        // }

        memset(out, 0, d_fft_len*d_N_tx*d_N_rx*d_interp_factor*sizeof(gr_complex));
        memset(radar_chan_est, 0, d_fft_len*d_N_tx*d_N_rx*sizeof(gr_complex) );       
        
        int i_chan_indx;

        gr_complex buffer_elem_mean(0.0, 0.0);

        for (int i_sc = 0; i_sc < d_fft_len; i_sc++)
        {
            for (int i_rx = 0; i_rx < d_N_rx; i_rx++)
            {
                in_rx = reinterpret_cast<const gr_complex*>(input_items[i_rx + d_N_tx]);
                in_rx += d_fft_len*d_N_pre;
                for (int i_tx = 0; i_tx < d_N_tx; i_tx++)
                {
                    in_tx = reinterpret_cast<const gr_complex*>(input_items[i_tx]);
                    in_tx += d_fft_len*d_N_pre;

                    if (d_enable_tx_interleave)
                    {
                        i_chan_indx = i_sc + d_fft_len * (i_tx*d_N_rx+i_rx); // col + width * (row)
                    }
                    else
                    {
                        i_chan_indx = i_sc + d_fft_len * (i_rx*d_N_tx+i_tx); // col + width * (row)
                    }

                    for (int i_sym = 0; i_sym < d_N_sym; i_sym++)
                    {
                        // radar_chan_est[i_rx*d_N_tx+i_tx][i_sc] = radar_chan_est[i_rx*d_N_tx+i_tx][i_sc] + in[i_sc+i_ltf*d_fft_len]*std::conj(d_P_ltf[i_tx][i_ltf]*d_ltf_seq[i_sc]);
                        // radar_chan_est[i_chan_indx] = radar_chan_est[i_chan_indx] + in[i_sc+i_sym*d_fft_len]*std::conj(d_P_ltf[i_tx][i_sym]*d_ltf_seq[i_sc]);
                        
                        radar_chan_est[i_chan_indx] = radar_chan_est[i_chan_indx] + in_rx[i_sc+i_sym*d_fft_len]*std::conj(in_tx[i_sc+i_sym*d_fft_len]);
                    }

                    if (d_background_recording)
                    {
                        memcpy(&radar_chan_est_temp[i_chan_indx], radar_chan_est+i_chan_indx, sizeof(gr_complex));
                    }

                    if (d_background_removal)
                    {
                        int curr_buffer_size = radar_chan_est_buffer.size();
                        buffer_elem_mean = 0.0;

                        for (int i_buffer = 0; i_buffer < curr_buffer_size; i_buffer++)
                        {
                            buffer_elem_mean += radar_chan_est_buffer[i_buffer][i_chan_indx]/(float)curr_buffer_size;
                        }

                        radar_chan_est[i_chan_indx] = radar_chan_est[i_chan_indx] - buffer_elem_mean;
                    }
                }
            }
        }

        if (d_background_removal)
        {
            radar_chan_est_buffer.push_back(radar_chan_est_temp);
        }

        dout << "[MIMO RADAR]: curr_buffer_size = " << radar_chan_est_buffer.size() << std::endl;

        // Update len key tag
        noutput_items = d_N_tx*d_N_rx;
        update_length_tags(noutput_items,0);

        for(int i_pair = 0; i_pair < d_N_tx*d_N_rx; i_pair++){
            memcpy(out+i_pair*d_fft_len*d_interp_factor, radar_chan_est+i_pair*d_fft_len, d_fft_len*sizeof(gr_complex));
        }
        // dout << "[PILOT PROCESSOR] pc_work_time_total: " << this->pc_work_time_total()  << std::endl;
        // dout << "[PILOT PROCESSOR] pc_input_buffers_full: " << pc_input_buffers_full(0) << "  pc_output_buffers_full: "  << pc_output_buffers_full(0) << std::endl;

        // int N;
        // std::vector<gr_complex> x(N);
        // vector<gr_complex> y(N);
        // vector<gr_complex> z(N);
        // // fill x and y with stuff
        // volk_32fc_x2_dot_prod_32fc(&z[0], &x[0], &y[0], N);

        // Tell runtime system how many output items we produced.
        return noutput_items;
    }

    void mimo_radar_estimator_2_impl::set_background_record(bool background_recording)
    {
        std::cout << "[MIMO RADAR] Background recording set to  " << background_recording << std::endl;
        d_background_recording = background_recording;
    }
} /* namespace mimo_ofdm_jrc */
} /* namespace gr */

