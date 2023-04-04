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

#include "sta.h"
#include <cstring>
#include <iostream>

using namespace gr::mimo_ofdm_jrc::estimator;

void sta::equalize(gr_complex *in, 
                    int n, 
                    gr_complex *symbols, 
                    uint8_t *bits, 
                    gr_complex *d_H, 
                    int fft_len, 
                    std::vector<int> data_carriers, 
                    std::vector<int>  pilot_carriers, 
                    std::vector<int>  nondata_carriers,  
                    const std::vector<std::vector<gr_complex>>& pilot_chips, 
                    boost::shared_ptr<gr::digital::constellation> mod) 
{

		gr_complex H_update[fft_len];
		gr_complex H[fft_len];

		std::vector<gr_complex> p = pilot_chips[(n - 2) % pilot_chips.size()];


		for (int i = 0; i < pilot_carriers.size(); i++){
			H[pilot_carriers[i]] = in[pilot_carriers[i]] / p[i];
		}

		for(int i = 0; i < data_carriers.size(); i++) {
				symbols[i] = in[data_carriers[i]] / d_H[data_carriers[i]];
				bits[i] = mod->decision_maker(&symbols[i]);
				gr_complex point;
				mod->map_to_points(bits[i], &point);
				H[data_carriers[i]] = in[data_carriers[i]] / point;
				// std::cout << "d_H[data_carriers[i]]: " << d_H[data_carriers[i]] << std::endl;

		}

		for(int i = 0; i < fft_len; i++) 
		{
			int n = 0;
			gr_complex s = 0;
			for(int k = i-beta; k <= i+beta; k++) 
			{
				if((k == fft_len/2) || (k < 2) || ( k > fft_len-2)) // || (k == fft_len/2-1) || (k == fft_len/2+1)) 
				{
					continue;
				}
				if(H[k] != gr_complex(0, 0))
				{
					n++;
					s += H[k];
				}
			}
			H_update[i] = s / gr_complex(n, 0);
			// std::cout << "H[k]: " << H[i] << " H_update[i]: " << H_update[i] << " s: " << s << " n: " << n << std::endl;

		}

		for(int i = 0; i < fft_len; i++) 
		{
			if((i == fft_len/2) || (i < 2) || ( i > fft_len-2))// || (i == fft_len/2-1) || (i == fft_len/2+1))
			{ 
				continue;
			}
			d_H[i] = gr_complex(1-alpha,0) * d_H[i] + gr_complex(alpha,0) * H_update[i];
		}
	// }
}

double
sta::get_snr() {
	return d_snr_est;
}
