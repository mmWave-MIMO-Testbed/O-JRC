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
#include "sync_mimo_trx_impl.h"
#include <iostream>
#include <boost/algorithm/string.hpp>
// #include <thread>

namespace gr {
  namespace mimo_ofdm_jrc {

	sync_mimo_trx::sptr
	sync_mimo_trx::make(int N_mboard, int N_tx, int N_rx, int samp_rate, float center_freq, int num_delay_samps, bool debug, float update_period,
		std::string args_tx, std::string wire_tx, std::string clock_source_tx, std::string time_source_tx, std::string antenna_tx, float gain_tx, 
		float timeout_tx, float wait_tx, float lo_offset_tx,
		std::string args_rx, std::string wire_rx, std::string clock_source_rx,std::string time_source_rx, std::string antenna_rx, float gain_rx, 
		float timeout_rx, float wait_rx, float lo_offset_rx, 
		const std::string& len_key)
	{
		return gnuradio::get_initial_sptr
		(new sync_mimo_trx_impl(N_mboard, N_tx, N_rx, samp_rate, center_freq, num_delay_samps,  debug,  update_period,
			args_tx, wire_tx, clock_source_tx, time_source_tx, antenna_tx, gain_tx, 
			timeout_tx, wait_tx, lo_offset_tx, 
			args_rx, wire_rx, clock_source_rx, time_source_rx, antenna_rx, gain_rx, 
			timeout_rx, wait_rx, lo_offset_rx, 
			len_key));
	}

	/*
		* The private constructor
		*/
	sync_mimo_trx_impl::sync_mimo_trx_impl(int N_mboard, int N_tx, int N_rx, int samp_rate, float center_freq, int num_delay_samps, bool debug,  float update_period,
		std::string args_tx, std::string wire_tx, std::string clock_source_tx, std::string time_source_tx, std::string antenna_tx, float gain_tx, 
		float timeout_tx, float wait_tx, float lo_offset_tx,
		std::string args_rx, std::string wire_rx, std::string clock_source_rx,std::string time_source_rx, std::string antenna_rx, float gain_rx, 
		float timeout_rx, float wait_rx, float lo_offset_rx, 
		const std::string& len_key)
		: gr::tagged_stream_block("sync_mimo_trx",
				gr::io_signature::make(N_tx, N_tx, sizeof(gr_complex)),
				gr::io_signature::make(N_rx, N_rx, sizeof(gr_complex)), len_key),
				d_debug(debug)
	{

        d_N_mboard = N_mboard;
        d_N_tx = N_tx;
        d_N_rx = N_rx;

		d_samp_rate = samp_rate;
		d_center_freq = center_freq;
		d_num_delay_samps = num_delay_samps;

        d_out_buffer.resize(d_N_rx);
        d_out_recv_ptrs.resize(d_N_rx);
        for (size_t i_rx = 0; i_rx < d_N_rx; i_rx++)
        {
            d_out_buffer[i_rx].resize(0);
            d_out_recv_ptrs[i_rx] = &d_out_buffer[i_rx].front();
        }
        // d_out_buffer.resize(0);

    
		prev_tx_time = 0.0;
		d_update_period = update_period;

		//===========================================================================================================
		//= Setup USRP TX ===========================================================================================
		//===========================================================================================================
		d_args_tx = args_tx;
		d_wire_tx = wire_tx;


        clock_source_tx.erase(std::remove_if(clock_source_tx.begin(), clock_source_tx.end(), isspace), clock_source_tx.end());
		std::cout << "clock_source_tx: " << clock_source_tx << std::endl;

        boost::split(d_clock_source_tx, clock_source_tx, boost::is_any_of(","));
        for (auto i : d_clock_source_tx){
            // std::cout << "clock_source_tx: " << i << std::endl;
        }

        time_source_tx.erase(std::remove_if(time_source_tx.begin(), time_source_tx.end(), isspace), time_source_tx.end());
        boost::split(d_time_source_tx, time_source_tx, boost::is_any_of(","));

        antenna_tx.erase(std::remove_if(antenna_tx.begin(), antenna_tx.end(), isspace), antenna_tx.end());
        boost::split(d_antenna_tx, antenna_tx, boost::is_any_of(","));

        // std::string segment;
        // std::stringstream ss(time_source_tx);

        // while(std::getline(ss, segment, ','))
        // {
        //     d_time_source_tx.push_back(segment);
        // }
        // ss.str("");
        // ss.clear();

        // ss.str(antenna_tx);
        // while(std::getline(ss, segment, ','))
        // {
        //     d_antenna_tx.push_back(segment);
        // }
        // ss.str("");
        // ss.clear();

		d_lo_offset_tx = lo_offset_tx;
		d_gain_tx = gain_tx;
		d_timeout_tx = timeout_tx; // timeout for sending
		d_wait_tx = wait_tx; // secs to wait befor sending

        // TODO do we need two USRP objects?

		// Setup USRP TX: args (addr,...)
		d_usrp_tx = uhd::usrp::multi_usrp::make(d_args_tx);
		std::cout << "Using USRP Device (TX): " << std::endl << d_usrp_tx->get_pp_string() << std::endl;
		std::cout << "Number of MBoards (TX): " << std::endl << d_usrp_tx->get_num_mboards() << std::endl;

		// d_usrp_tx->set_tx_subdev_spec(uhd::usrp::subdev_spec_t("A:0"));

        d_usrp_tx->set_tx_lo_source("external", "lo1", 0);
        d_usrp_tx->set_tx_lo_source("external", "lo1", 1);

        d_usrp_tx->set_tx_lo_export_enabled(true, "lo1", 0);

        std::cout << "Using Master Clock Rate (TX): " << std::endl << d_usrp_tx->get_master_clock_rate() << std::endl;
        // Setup USRP TX: clock source
        for (int i_mboard = 0; i_mboard < d_N_mboard; i_mboard++ ){
            d_usrp_tx->set_clock_source(d_clock_source_tx[i_mboard], i_mboard);  // Set TX clock, TX is master
            std::cout << "USRP Clock Source (TX-" << i_mboard << "): " << d_usrp_tx->get_clock_source(i_mboard) << std::endl;
        }
        
        // Setup USRP TX: time source
        for (int i_mboard = 0; i_mboard < d_N_mboard; i_mboard++ ){
            std::cout << "Trying to set USRP Time Source (TX-" << i_mboard << "): " << d_time_source_tx[i_mboard] << std::endl;
            d_usrp_tx->set_time_source(d_time_source_tx[i_mboard], i_mboard);  // Set TX time, TX is master 
            std::cout << "USRP Time Source (TX-" << i_mboard << "): " << d_usrp_tx->get_time_source(i_mboard) << std::endl;
        }

		// Setup USRP TX: sample rate
		std::cout << "Setting TX Rate: " << d_samp_rate << std::endl;
		d_usrp_tx->set_tx_rate(d_samp_rate);
		std::cout << "Actual TX Rate: " << d_usrp_tx->get_tx_rate() << std::endl;

        // Setup USRP TX: antenna
        for (int i_tx = 0; i_tx < d_N_tx; i_tx++ ){
            d_usrp_tx->set_tx_antenna(d_antenna_tx[i_tx], i_tx);
        }

		// Setup USRP TX: gain
		set_tx_gain(d_gain_tx);

        // d_usrp_tx->set_tx_dc_offset(0.02, 0);
        // d_usrp_tx->set_tx_dc_offset(0.05, 1);

		// Setup USRP TX: time sync
        d_usrp_tx->set_time_now(uhd::time_spec_t(0.0)); // Do set time on startup if not gpsdo is activated.
        
        // d_usrp_tx->set_time_next_pps(uhd::time_spec_t(0.0));
        // boost::this_thread::sleep(boost::posix_time::milliseconds(500));
        

        d_usrp_tx->clear_command_time();
        d_usrp_tx->set_command_time(d_usrp_tx->get_time_now() + uhd::time_spec_t(0.1)); //set cmd time for .1s in the future

		// Setup USRP TX: tune request
		d_tune_request_tx = uhd::tune_request_t(d_center_freq); 
		// d_tune_request_tx = uhd::tune_request_t(d_center_freq, 0, dsp_policy=uhd.tune_request.POLICY_MANUAL, dsp_freq=LO-d_center_freq, lo_freq_policy=uhd.tune_request.POLICY_MANUAL, lo_freq=LO);
		
        for (int i_tx = 0; i_tx < d_N_tx; i_tx++ ){
            d_usrp_tx->set_tx_freq(d_tune_request_tx, i_tx);
        }
        boost::this_thread::sleep(boost::posix_time::milliseconds(150));
        d_usrp_tx->clear_command_time();

		// Setup transmit streamer
		uhd::stream_args_t stream_args_tx("fc32", d_wire_tx); // complex floats
        for (int i_tx = 0; i_tx < d_N_tx; i_tx++ ){
            stream_args_tx.channels.push_back(i_tx);
        }
		d_tx_stream = d_usrp_tx->get_tx_stream(stream_args_tx);
        std::cout << "Number of Total Channels (TX): " << d_usrp_tx->get_tx_num_channels() << std::endl;
        std::cout << "Number of Stream Channels (TX): " << d_tx_stream->get_num_channels() << std::endl;


		//===========================================================================================================
		//= Setup USRP RX ===========================================================================================
		//===========================================================================================================
		d_args_rx = args_rx;
		d_wire_rx = wire_rx;

        clock_source_rx.erase(std::remove_if(clock_source_rx.begin(), clock_source_rx.end(), isspace), clock_source_rx.end());
        boost::split(d_clock_source_rx, clock_source_rx, boost::is_any_of(","));

        time_source_rx.erase(std::remove_if(time_source_rx.begin(), time_source_rx.end(), isspace), time_source_rx.end());
        boost::split(d_time_source_rx, time_source_rx, boost::is_any_of(","));

        antenna_rx.erase(std::remove_if(antenna_rx.begin(), antenna_rx.end(), isspace), antenna_rx.end());
        boost::split(d_antenna_rx, antenna_rx, boost::is_any_of(","));

		d_lo_offset_rx = lo_offset_rx;
		d_gain_rx = gain_rx;
		d_timeout_rx = timeout_rx; // timeout for receiving
		d_wait_rx = wait_rx; // secs to wait befor receiving


		// Setup USRP RX: args (addr,...)
		d_usrp_rx = uhd::usrp::multi_usrp::make(d_args_rx);
        std::cout << "Using USRP Device (RX): " << std::endl << d_usrp_rx->get_pp_string() << std::endl;

        std::cout << "Using Master Clock Rate (RX): " << std::endl << d_usrp_rx->get_master_clock_rate() << std::endl;

        d_usrp_rx->set_rx_lo_source("external", "lo1", 0);
        d_usrp_rx->set_rx_lo_source("external", "lo1", 1);

        d_usrp_rx->set_rx_lo_export_enabled(true, "lo1", 0);
            


        // Setup USRP RX: clock source
        for (int i_mboard = 0; i_mboard < d_N_mboard; i_mboard++ ){
            d_usrp_rx->set_clock_source(d_clock_source_rx[i_mboard], i_mboard);   // RX is slave, clock is set on TX
            std::cout << "USRP Clock Source (RX-" << i_mboard << "): " << d_usrp_rx->get_clock_source(i_mboard) << std::endl;
        }
        
        // Setup USRP RX: time source
        for (int i_mboard = 0; i_mboard < d_N_mboard; i_mboard++ ){
            d_usrp_rx->set_time_source(d_time_source_rx[i_mboard], i_mboard); 
            std::cout << "USRP Time Source (RX-" << i_mboard << "): " << d_usrp_rx->get_time_source(i_mboard) << std::endl;
        }

		// Setup USRP RX: sample rate
		std::cout << "Setting RX Rate: " << d_samp_rate << std::endl;
		d_usrp_rx->set_rx_rate(d_samp_rate);
		std::cout << "Actual RX Rate: " << d_usrp_rx->get_rx_rate() << std::endl;

		// d_usrp_rx->set_rx_subdev_spec(uhd::usrp::subdev_spec_t("A:0"));
		
        // Setup USRP RX: antenna
        for (int i_rx = 0; i_rx < d_N_rx; i_rx++ ){
            d_usrp_rx->set_rx_antenna(d_antenna_rx[i_rx], i_rx);
        }

		// Setup USRP RX: gain
		set_rx_gain(d_gain_rx);

		// Setup USRP TX: time sync
        // d_usrp_rx->set_time_now(uhd::time_spec_t(0.0));
        // d_usrp_rx->set_time_next_pps(uhd::time_spec_t(0.0));

        d_usrp_rx->clear_command_time();
        d_usrp_rx->set_command_time(d_usrp_rx->get_time_now() + uhd::time_spec_t(0.1)); //set cmd time for .1s in the future
            
		// Setup USRP RX: tune request
		d_tune_request_rx = uhd::tune_request_t(d_center_freq, d_lo_offset_rx); 

        for (int i_rx = 0; i_rx < d_N_rx; i_rx++ ){
            d_usrp_rx->set_rx_freq(d_tune_request_rx, i_rx);
        }
        boost::this_thread::sleep(boost::posix_time::milliseconds(150));
        d_usrp_rx->clear_command_time();

		// Setup receive streamer
		uhd::stream_args_t stream_args_rx("fc32", d_wire_rx); // complex floats
        for (int i_rx = 0; i_rx < d_N_rx; i_rx++ ){
            stream_args_rx.channels.push_back(i_rx);
        }
		// std::vector<size_t> channel_nums; channel_nums.push_back(0); // define channel!
		// stream_args_rx.channels = channel_nums;
		d_rx_stream = d_usrp_rx->get_rx_stream(stream_args_rx);
        std::cout << "Number of Total Channels (RX): " << d_usrp_rx->get_rx_num_channels() << std::endl;
        std::cout << "Number of Stream Channels (RX): " << d_rx_stream->get_num_channels() << std::endl;

		//===========================================================================================================
		//= Other Setup =============================================================================================
		//===========================================================================================================

        std::vector<std::string> tree_list = d_usrp_tx->get_tree()->list("blocks/0/Radio#0/dboard/tx_frontends/0/los/lo1/lo_distribution");
        for (auto i : tree_list){
            std::cout << "USRP get_tree: " << i << std::endl;
        }
        
        // TODO Test with 2 USRPs and Add parameters to block for UI control

        // LO Output Switch for other USRP N320
        // d_usrp_tx->get_device()->get_tree()->access<bool>("blocks/0/Radio#0/dboard/tx_frontends/0/los/lo1/lo_distribution/LO_OUT_0/export").set(true);

        // LO Output Switch to loop back
        d_usrp_tx->get_device()->get_tree()->access<bool>("blocks/0/Radio#0/dboard/tx_frontends/0/los/lo1/lo_distribution/LO_OUT_1/export").set(true);

        // LO Output Switch for other USRP N320
        // d_usrp_rx->get_device()->get_tree()->access<bool>("blocks/0/Radio#0/dboard/rx_frontends/0/los/lo1/lo_distribution/LO_OUT_0/export").set(true);

        // LO Output Switch to loop back
        d_usrp_rx->get_device()->get_tree()->access<bool>("blocks/0/Radio#0/dboard/rx_frontends/0/los/lo1/lo_distribution/LO_OUT_1/export").set(true);


		// Setup rx_time pmt
		d_time_key = pmt::string_to_symbol("rx_time");
		d_srcid = pmt::string_to_symbol("mimo_sync_trx");

		// Setup thread priority
		//uhd::set_thread_priority_safe(); // necessary? doesnt work...

		// Sleep to get sync done
		boost::this_thread::sleep(boost::posix_time::milliseconds(1000)); // FIXME: necessary?

        std::vector<uhd::time_spec_t> current_time_specs_tx(d_N_mboard);
        std::vector<uhd::time_spec_t> current_time_specs_rx(d_N_mboard);

        for (int i_mboard = 0; i_mboard < d_N_mboard; i_mboard++ )
        {
            current_time_specs_tx[i_mboard] = d_usrp_tx->get_time_now(i_mboard);
            current_time_specs_rx[i_mboard] = d_usrp_rx->get_time_now(i_mboard);
        }

        for (int i_mboard = 0; i_mboard < d_N_mboard; i_mboard++ )
        {
            double current_time_tx = current_time_specs_tx[i_mboard].get_full_secs()+current_time_specs_tx[i_mboard].get_frac_secs();
            double current_time_rx = current_time_specs_rx[i_mboard].get_full_secs()+current_time_specs_rx[i_mboard].get_frac_secs();

            std::cout << "USRP Current Time Source (TX-" << i_mboard << "): " << current_time_tx << std::endl;
            std::cout << "USRP Current Time Source (RX-" << i_mboard << "): " << current_time_rx << std::endl;
        }
	}

	/*
		* Our virtual destructor.
		*/
	sync_mimo_trx_impl::~sync_mimo_trx_impl()
	{
	}

	int
	sync_mimo_trx_impl::work (int noutput_items,
						gr_vector_int &ninput_items,
						gr_vector_const_void_star &input_items, // hold vector of pointers for multiple channels
						gr_vector_void_star &output_items) // hold vector of pointers for multiple channels
	{
		// gr_complex *in = (gr_complex *) input_items[0]; // remove const
		
		// std::cout  << "[USRP] active_thread_priority : " << gr::block::active_thread_priority()	<< std::endl;
		// std::cout  << "[USRP] thread_priority : " << gr::block::thread_priority()	<< std::endl;
		gr::block::set_thread_priority(32);
        
        boost::recursive_mutex::scoped_lock lock(d_mutex);

		// Set output items on packet length
		noutput_items = ninput_items[0];
        dout << "[USRP] noutput_items: " << noutput_items << std::endl;
        dout << "[USRP] output_items.size(): " << output_items.size() << std::endl;

        for (size_t i_rx = 0; i_rx < d_N_rx; i_rx++)
        {
            if(d_out_buffer[i_rx].size() != noutput_items)
            {
                d_out_buffer[i_rx].resize(noutput_items);
                dout << "[USRP] Receive Buffer " << i_rx << " resized to " << noutput_items << std::endl;
                d_out_recv_ptrs[i_rx] = &d_out_buffer[i_rx].front();
            }
        }

        d_in_send_ptrs = input_items;

		// Get time from USRP TX
		// d_time_now_tx = d_usrp_tx->get_time_now();
		uhd::time_spec_t current_time_spec = d_usrp_tx->get_time_now();
		double current_time = current_time_spec.get_full_secs()+current_time_spec.get_frac_secs();

		if (current_time >= prev_tx_time + d_update_period) // TX/RX MODE
		{
            prev_tx_time = current_time_spec.get_full_secs()+current_time_spec.get_frac_secs();
                
            d_noutput_items_send = noutput_items;
            d_noutput_items_recv = noutput_items;
                
            d_time_now_tx = d_usrp_tx->get_time_now();
            d_time_now_rx = d_time_now_tx;

            // Trasnmit thread
            d_thread_send = gr::thread::thread(boost::bind(&sync_mimo_trx_impl::transmit, this));
            // Receive thread
            d_thread_recv = gr::thread::thread(boost::bind(&sync_mimo_trx_impl::receive, this));
            
            // Wait for threads to complete
            d_thread_send.join();
            d_thread_recv.join();
        }
        else
        {
            d_noutput_items_send = noutput_items;
			d_noutput_items_recv = 0;
            
            // Send thread
            d_thread_send = gr::thread::thread(boost::bind(&sync_mimo_trx_impl::transmit, this));

            d_thread_send.join();
			
			return 0;
        }
        
        // std::cout << "[USRP] d_metadata_tx: " << d_metadata_tx.time_spec.get_real_secs() << std::endl;
        // std::cout << "[USRP] d_metadata_rx: " << d_metadata_rx.time_spec.get_real_secs() << std::endl;
        // std::cout << "[USRP] d_out_buffer[0][0]: " << d_out_buffer[0][0] << std::endl;
        // std::cout << "[USRP] d_out_buffer[1][0]: " << d_out_buffer[1][0] << std::endl;

        gr_complex *out;
        for (int i_rx = 0; i_rx < d_N_rx; i_rx++) {
            out = (gr_complex*) output_items[i_rx];

            memcpy(out, &d_out_buffer[i_rx][0] + d_num_delay_samps, (noutput_items - d_num_delay_samps)*sizeof(gr_complex)); // push buffer to output
            memset(out + (noutput_items-d_num_delay_samps), 0, d_num_delay_samps*sizeof(gr_complex)); // set zeros
            
            // Setup rx_time tag
            add_item_tag(i_rx, nitems_written(0), d_time_key, d_time_val, d_srcid);
        }

        // gr_complex* out = (gr_complex*)output_items[0];

        // memcpy(out, &d_out_buffer[0] + d_num_delay_samps, (noutput_items - d_num_delay_samps)*sizeof(gr_complex)); // push buffer to output
        // memset(out + (noutput_items - d_num_delay_samps), 0, d_num_delay_samps * sizeof(gr_complex)); // set zeros

        // // Setup rx_time tag
        // add_item_tag(0, nitems_written(0), d_time_key, d_time_val, d_srcid);

		// Tell runtime system how many output items we produced.
		return noutput_items;
	}

	void
	sync_mimo_trx_impl::transmit()
	{
	// Setup metadata for first package
		d_metadata_tx.start_of_burst = true;
		d_metadata_tx.end_of_burst = false;
		d_metadata_tx.has_time_spec = true;
		// std::cout << "[SEND] d_noutput_items_recv: " << d_noutput_items_recv << std::endl;

					
		if (d_noutput_items_recv == 0) // TX Only -> No RX Scheduled
		{
            d_time_now_tx = d_usrp_tx->get_time_now();
            d_metadata_tx.time_spec = d_time_now_tx + uhd::time_spec_t(d_wait_tx); 
        }
        else
        {
            d_metadata_tx.time_spec = d_time_now_tx + uhd::time_spec_t(d_wait_tx);
        }

		// Send input buffer
		size_t num_tx_samps, total_num_samps;
		total_num_samps = d_noutput_items_send;
		
        // Data to USRP
		num_tx_samps = d_tx_stream->send(d_in_send_ptrs, total_num_samps, d_metadata_tx, total_num_samps/(float)d_samp_rate+d_timeout_tx);
        // num_tx_samps = d_tx_stream->send(d_in_send, total_num_samps, d_metadata_tx, total_num_samps/(float)d_samp_rate+d_timeout_tx);

		// Get timeout
		if (num_tx_samps < total_num_samps){
            std::cerr << "Send timeout..." << std::endl;
        }

		//send a mini EOB packet
		d_metadata_tx.start_of_burst = false;
		d_metadata_tx.end_of_burst = true;
		d_metadata_tx.has_time_spec = false;
		d_tx_stream->send("", 0, d_metadata_tx);
	}

	void
	sync_mimo_trx_impl::receive()
	{
		// Setup RX streaming
		size_t total_num_samps = d_noutput_items_recv;
		uhd::stream_cmd_t stream_cmd(uhd::stream_cmd_t::STREAM_MODE_NUM_SAMPS_AND_DONE);
		// std::cout << "[USRP] Total Number of Samples for TX/RX : " << total_num_samps << std::endl;
		stream_cmd.num_samps = total_num_samps;
		stream_cmd.stream_now = false;
		stream_cmd.time_spec = d_time_now_rx + uhd::time_spec_t(d_wait_rx);

		d_current_time_now = d_usrp_tx->get_time_now();
		double current_time = d_current_time_now.get_full_secs() + d_current_time_now.get_frac_secs();
		double planned_rx_time = stream_cmd.time_spec.get_full_secs() + stream_cmd.time_spec.get_frac_secs();
		// std::cout << "[RX] RX scheduled: " << planned_rx_time << std::endl;

		if (planned_rx_time >= current_time)
		{
			d_rx_stream->issue_stream_cmd(stream_cmd);
			size_t num_rx_samps;
			// Receive a packet
			num_rx_samps = d_rx_stream->recv(d_out_recv_ptrs, total_num_samps, d_metadata_rx, total_num_samps/(float)d_samp_rate+d_timeout_rx);
            // num_rx_samps = d_rx_stream->recv(d_out_recv, total_num_samps, d_metadata_rx, total_num_samps/(float)d_samp_rate+d_timeout_rx);

			// Save timestamp
			// d_time_val = pmt::make_tuple(pmt::from_uint64(d_metadata_rx.time_spec.get_full_secs()),pmt::from_double(d_metadata_rx.time_spec.get_frac_secs()));
            d_time_val = pmt::from_double( d_metadata_rx.time_spec.get_full_secs() + d_metadata_rx.time_spec.get_frac_secs() );

			// Handle the error code
			if (d_metadata_rx.error_code != uhd::rx_metadata_t::ERROR_CODE_NONE)
			{
                std::cerr << "[USRP] Receiver Error: " << d_metadata_rx.strerror() << std::endl;
				// throw std::runtime_error(str(boost::format("Receiver error %s") % d_metadata_rx.strerror()));
			}

			if (num_rx_samps < total_num_samps)
            {
                std::cerr << "[USRP] Receive timeout before all samples received..." << std::endl;
                std::cerr << "[USRP] Receiver Error: " << d_metadata_rx.strerror() << std::endl;
                std::cout << "[USRP] fragment_offset: " << d_metadata_rx.fragment_offset<< std::endl;
            }

            // std::cout << "[USRP] num_rx_samps : " << num_rx_samps << std::endl;
            // std::cout << "[USRP] error_code: " << d_metadata_rx.error_code << std::endl;
            // std::cout << "[USRP] fragment_offset: " << d_metadata_rx.fragment_offset<< std::endl;
            // std::cout << "[USRP] more_fragments: " << d_metadata_rx.more_fragments<< std::endl;
            // std::cout << "[USRP] out_of_sequence: " << d_metadata_rx.out_of_sequence<< std::endl;
		}
		else
		{
			std::cout << "[USRP] current_time: " << current_time << std::endl;
			std::cout <<  "[USRP] Planned RX Time: " << planned_rx_time << std::endl;
			std::cout << "[USRP] Timing requirements cannot be met!! USRP lacking -> Time Diff: " << current_time - planned_rx_time << std::endl;
			d_noutput_items_recv = 0;
		}
	}

	int sync_mimo_trx_impl::calculate_output_stream_length(const gr_vector_int &ninput_items)
	{
		int noutput_items = ninput_items[0];
		return noutput_items ;
	}

	void sync_mimo_trx_impl::set_num_delay_samps(int num_samps){
		d_num_delay_samps = num_samps;
	}

	void sync_mimo_trx_impl::set_rx_gain(float gain){
        for (int i_rx = 0; i_rx < d_N_rx; i_rx++ ){
            d_usrp_rx->set_rx_gain(gain, i_rx);
        }
	}

	void sync_mimo_trx_impl::set_tx_gain(float gain){
        for (int i_tx = 0; i_tx < d_N_tx; i_tx++ ){
            d_usrp_tx->set_tx_gain(gain, i_tx);
        }
	}

  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

