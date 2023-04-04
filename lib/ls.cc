/*
 * Copyright (C) 2016 Bastian Bloessl <bloessl@ccs-labs.org>
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

#include "ls.h"
#include <cstring>
#include <iostream>

using namespace gr::mimo_ofdm_jrc::estimator;

void ls::equalize(gr_complex *in, 
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

	
	for(int i = 0; i < data_carriers.size(); i++) 
	{
		symbols[i] = in[data_carriers[i]] / d_H[data_carriers[i]];
        in[data_carriers[i]] = symbols[i];
        // std::cout << "(" << d_H[data_carriers[i]].real() << "," << d_H[data_carriers[i]].imag() << "), ";   
		bits[i] = mod->decision_maker(&symbols[i]);		
	}

    for(int i = 0; i < nondata_carriers.size(); i++) 
	{   
        if(d_H[nondata_carriers[i]] == gr_complex(0.0,0.0))
        {
            in[nondata_carriers[i]] = 0.0;
        }
        else{
            in[nondata_carriers[i]] = in[nondata_carriers[i]] / d_H[nondata_carriers[i]];
        }
        // std::cout << "(" << d_H[data_carriers[i]].real() << "," << d_H[data_carriers[i]].imag() << "), ";   
	}
	
}

double ls::get_snr() {
	return d_snr_est;
}
