/*
 * Copyright (C) 2015 Bastian Bloessl <bloessl@ccs-labs.org>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef INCLUDED_MIMO_OFDM_JRC_ESTIMATOR_STA_H
#define INCLUDED_MIMO_OFDM_JRC_ESTIMATOR_STA_H

#include "base.h"
#include <vector>

namespace gr {
	namespace mimo_ofdm_jrc {
		namespace estimator {
			class sta: public base {
			public:
				virtual void equalize(gr_complex *in, 
                    int n, 
                    gr_complex *symbols, 
                    uint8_t *bits, 
                    gr_complex *d_H, 
                    int fft_len, 
                    std::vector<int> data_carriers, 
                    std::vector<int>  pilot_carriers,  
                    std::vector<int>  nondata_carriers,  
                    const std::vector<std::vector<gr_complex>>& pilot_chips, 
                    boost::shared_ptr<gr::digital::constellation> mod);
				double get_snr();

			private:
				double d_snr_est;

				const double alpha = 0.5;
				const int beta = 1;
			};

		} /* namespace estimator */
	} /* namespace ofdm_radar */
} /* namespace gr */

#endif /* INCLUDED_OFDM_RADAR_ESTIMATOR_STA_H */
