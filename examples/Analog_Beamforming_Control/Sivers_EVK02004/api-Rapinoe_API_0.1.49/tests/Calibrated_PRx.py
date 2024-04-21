"""
File Name: Calibrated_PRx.py
Author: Avhishek Biswas
Date: 01/26/2024

Description:
- This code calculates the average and maximum power of the received signal and returns the values in dBm.
"""


import numpy as np

def calculate_power_metrics(complex_signal):
    # Extract the I and Q components from the complex signal
    I = complex_signal.real
    Q = complex_signal.imag
    
    # Calculate IQ magnitude for each sample in millivolts (mV) for each sample
    IQ_magnitude = np.sqrt(I**2 + Q**2)
    
    # Calculate IQ power for each sample in milliwatts (mW) for each sample
    IQ_power_mW = (IQ_magnitude**2) / 50.0
    
    # Convert the power values to dBm for each sample
    IQ_power_dBm = 10 * np.log10(IQ_power_mW) + 7 # 7 is the calibration value
    
    # Calculate average and maximum power in dBm for the whole complex signal
    avg_power_dBm = np.mean(IQ_power_dBm)
    max_power_dBm = np.max(IQ_power_dBm)
    
    return IQ_power_dBm,avg_power_dBm, max_power_dBm

# # Test the function
# complex_signal = np.array([complex(1,2), complex(3,4), complex(5,6)])  # Sample input
# avg_power, max_power = calculate_power_metrics(complex_signal)
# print(f"Average Power: {avg_power:.2f} dBm")
# print(f"Maximum Power: {max_power:.2f} dBm")
