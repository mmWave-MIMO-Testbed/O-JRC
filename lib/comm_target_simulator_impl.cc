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

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include <gnuradio/io_signature.h>
#include "comm_target_simulator_impl.h"
#include <algorithm>
#include <cmath>

namespace gr {
  namespace mimo_ofdm_jrc {

    // ---------------helper：calculate coefficients for every TX----------------
    void comm_target_simulator_impl::recompute_coeffs_unlocked()
    {
        // λ = c / f
        d_lambda_m = (d_center_freq_hz > 0.0) ? (C / d_center_freq_hz) : 0.0;

        const double R   = std::max(d_distance_m, d_min_dist);
        const double amp = (d_lambda_m > 0.0) ? (d_lambda_m / (4.0 * M_PI * R)) : 0.0;

        const double theta_rad = d_theta_deg * M_PI / 180.0;
        const double base      = d_use_two_pi ? (2.0 * M_PI) : M_PI;

        d_coeffs.resize(d_num_tx);
        for (int k = 0; k < d_num_tx; ++k) {
            const double phase = k * base * std::sin(theta_rad);
            d_coeffs[k] = std::complex<float>(std::cos(phase), std::sin(phase)) * static_cast<float>(amp);
        }
    }

    // --------------- helper：process cfg messages ----------------
    void comm_target_simulator_impl::handle_cfg_msg_(pmt::pmt_t msg)
    {
        std::lock_guard<std::mutex> lk(d_mu);
        bool changed = false;

        // support：Socket PDU 's PDU(pair) + u8vector(PMT)
        if (pmt::is_pair(msg) && pmt::is_u8vector(pmt::cdr(msg))) {
            std::vector<uint8_t> bytes = pmt::u8vector_elements(pmt::cdr(msg));
            try {
                msg = pmt::deserialize_str(std::string(bytes.begin(), bytes.end()));
            } catch (...) {
                return; // no PMT serialization data，ignore
            }
        }

        // support：direct PMT dictionary
        if (pmt::is_dict(msg)) {
            if (pmt::dict_has_key(msg, pmt::intern("theta_deg"))) {
                const double th = pmt::to_double(pmt::dict_ref(msg, pmt::intern("theta_deg"), pmt::PMT_NIL));
                if (std::isfinite(th) && std::abs(th - d_theta_deg) > 1e-12) { d_theta_deg = th; changed = true; }
            }
            if (pmt::dict_has_key(msg, pmt::intern("distance_m"))) {
                const double R = pmt::to_double(pmt::dict_ref(msg, pmt::intern("distance_m"), pmt::PMT_NIL));
                if (std::isfinite(R) && std::abs(R - d_distance_m) > 1e-12) { d_distance_m = R; changed = true; }
            }
        }
        // accept direct value: <theta_deg>
        else if (pmt::is_real(msg) || pmt::is_integer(msg)) {
            const double th = pmt::to_double(msg);
            if (std::isfinite(th) && std::abs(th - d_theta_deg) > 1e-12) { d_theta_deg = th; changed = true; }
        }

        if (changed) {
            recompute_coeffs_unlocked();
            // If ACK is needed, you can publish the state here: message_port_pub(pmt::mp("state"), dict)
        }
    }

    // --------------- constructor / destructor / factory ----------------
    comm_target_simulator_impl::comm_target_simulator_impl(int num_tx,
                                                          double center_freq_hz,
                                                          double min_distance_m,
                                                          bool use_two_pi)
    : gr::sync_block("comm_target_simulator",
                    gr::io_signature::make(num_tx, num_tx, sizeof(gr_complex)),
                    gr::io_signature::make(1, 1, sizeof(gr_complex))),
      d_num_tx(num_tx),
      d_use_two_pi(use_two_pi),
      d_min_dist(std::max(1e-6, min_distance_m)),
      d_center_freq_hz(center_freq_hz),
      d_coeffs(num_tx, std::complex<float>(0.0f, 0.0f))
    {
        // cfg message port
        message_port_register_in(pmt::mp("cfg"));
        set_msg_handler(pmt::mp("cfg"), [this](pmt::pmt_t m){ this->handle_cfg_msg_(m); });

        // Optional: state port
        // message_port_register_out(pmt::mp("state"));

        std::lock_guard<std::mutex> lk(d_mu);
        recompute_coeffs_unlocked();
    }

    comm_target_simulator_impl::~comm_target_simulator_impl() = default;

    comm_target_simulator::sptr
    comm_target_simulator::make(int num_tx,
                            double center_freq_hz,
                            double min_distance_m,
                            bool use_two_pi)
    {
      return gnuradio::get_initial_sptr
        (new comm_target_simulator_impl(num_tx, center_freq_hz, min_distance_m, use_two_pi));
    }

    // --------------- setters ----------------
    void comm_target_simulator_impl::set_theta_deg(double th_deg)
    {
        std::lock_guard<std::mutex> lk(d_mu);
        if (std::isfinite(th_deg) && std::abs(th_deg - d_theta_deg) > 1e-12) {
            d_theta_deg = th_deg;
            recompute_coeffs_unlocked();
        }
    }

    void comm_target_simulator_impl::set_distance_m(double dist_m)
    {
        std::lock_guard<std::mutex> lk(d_mu);
        if (std::isfinite(dist_m) && std::abs(dist_m - d_distance_m) > 1e-12) {
            d_distance_m = dist_m;
            recompute_coeffs_unlocked();
        }
    }

    void comm_target_simulator_impl::set_center_freq(double fc_hz)
    {
        std::lock_guard<std::mutex> lk(d_mu);
        if (std::isfinite(fc_hz) && fc_hz > 0.0 && std::abs(fc_hz - d_center_freq_hz) > 1e-3) {
            d_center_freq_hz = fc_hz;
            recompute_coeffs_unlocked();
        }
    }

    // --------------- work ----------------
    int comm_target_simulator_impl::work(int noutput_items,
                                        gr_vector_const_void_star &input_items,
                                        gr_vector_void_star &output_items)
    {
        auto *out = reinterpret_cast<gr_complex*>(output_items[0]);

        // copy one coeff to stack to avoid long lock hold
        std::vector<std::complex<float>> coeffs;
        { std::lock_guard<std::mutex> lk(d_mu); coeffs = d_coeffs; }

        for (int n = 0; n < noutput_items; ++n) {
            std::complex<float> acc(0.0f, 0.0f);
            for (int k = 0; k < d_num_tx; ++k) {
                const auto *in_k = reinterpret_cast<const gr_complex*>(input_items[k]);
                acc += coeffs[k] * in_k[n];
            }
            out[n] = acc;
        }
        return noutput_items;
    }

  } /* namespace mimo_ofdm_jrc */
} /* namespace gr */

