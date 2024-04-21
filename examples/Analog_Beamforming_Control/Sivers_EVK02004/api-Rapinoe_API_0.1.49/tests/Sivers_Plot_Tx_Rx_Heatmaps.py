"""
File Name: Sivers_Plot_Tx_Rx_Heatmaps.py
Author: Avhishek Biswas
Date: 01/26/2024

Description:
- This script plots the heatmap of the Tx-Rx beam angles and returns the best beam angle in dBm.
- The function plotheatmap_and_return_best_beam_in_dbm() is used to plot the heatmap and return the best beam angle in dBm.
- The function plotheatmap_and_return_best_beam_in_dbm_selected_beam() is used to plot the heatmap and return the best beam angle in dBm for a selected beam. - In this function there is a try-except block to handle the case when the file cannot be opened/read. And it sets the values to -100 dBm.
- Normally there is no need touch this file unless there is a change in the number of beams or the number of samples per beam.

Dependencies:
- calibrated_PRx.py which contains the function calculate_power_metrics() to calculate the power metrics.

Usage:
- To plot the heatmap and return the best beam angle in dBm, call the function plotheatmap_and_return_best_beam_in_dbm() or plotheatmap_and_return_best_beam_in_dbm_selected_beam().
- Make sure that the file calibrated_PRx.py is in the same directory as this file.
- Also make sure that the files tx_beam_angle_0.dat to tx_beam_angle_63.dat are in the same directory as this file. OR make sure they are directed in the code below.

Current Status:
- Tested  Works.
"""

from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

import Calibrated_PRx as calibration


def plotheatmap_and_return_best_beam_in_dbm():
    # Define the number of beams and samples per beam
    num_beams = 64
    samples_per_beam = 3928
    beam_angles = [-45.0, -43.5, -42.1, -40.6, -39.2, -37.7, -36.3, -34.8, -33.4, -31.9, -30.5, -29.0, -27.6, -26.1, -24.7, -23.2, -21.8, -20.3, -18.9, -17.4, -16.0, -14.5, -13.1, -11.6, -10.2, -8.7, -7.3, -5.8, -4.4, -2.9, -1.5, 0, 1.5, 2.9, 4.4, 5.8, 7.3, 8.7, 10.2, 11.6, 13.1, 14.5, 16.0, 17.4, 18.9, 20.3, 21.8, 23.2, 24.7, 26.1, 27.6, 29.0, 30.5, 31.9, 33.4, 34.8, 36.3, 37.7, 39.2, 40.6, 42.1, 43.5, 45.0]

    # Initialize an empty array to store the signal strength
    signal_strength = np.empty((num_beams, num_beams))

    # Initialize an empty array to store the signal strength
    avg_signal_powers = np.empty((num_beams, num_beams))

    # Initialize an empty array to store the signal strength
    max_signal_powers = np.empty((num_beams, num_beams))
    
    # Loop through each Tx beam file
    for tx_beam in range(num_beams):
        # Initialize an empty list to store mean strength values for each Rx beam
        mean_strengths = []
        avg_powers_in_dBm = []
        max_powers_in_dBm = []
        
        # Open the file for reading
        with open(f'tx_beam_angle_{tx_beam}.dat', 'rb') as f:
            # Loop through each Rx beam
            for rx_beam in range(num_beams):
                # Read samples for the current Rx beam
                data_array = np.fromfile(f, dtype=np.complex64, count=samples_per_beam)
                
                # Get the recieved powers for each sample
                IQ_power_dBm,avg_power_dBm, max_power_dBm = calibration.calculate_power_metrics(data_array)

                # Compute the mean absolute value of the samples
                mean_strength = round(np.mean(np.abs(data_array)), 4)
                avg_power_dBm = round(avg_power_dBm,2)
                max_power_dBm = round(max_power_dBm,2)

                # Append the mean strength and powers to the list
                mean_strengths.append(mean_strength)
                avg_powers_in_dBm.append(avg_power_dBm)
                max_powers_in_dBm.append(max_power_dBm)

        # Store the mean strength values in the signal_strength array
        signal_strength[tx_beam, :] = mean_strengths
        avg_signal_powers[tx_beam, :] = avg_powers_in_dBm
        max_signal_powers[tx_beam, :] = max_powers_in_dBm
        
    print("Signal Strength_array Shape = ",signal_strength.shape)
    print("Avg_power_array Shape = ",avg_signal_powers)
    print("Max_power_array Shape = ",max_signal_powers)

    # Find the index of the maximum value in the signal_strength array
    index_max = np.argmax(signal_strength)

    # Convert the flat index to a 2D index (row, column)
    tx_index, rx_index = np.unravel_index(index_max, signal_strength.shape)

    # Extract the corresponding beam angles using the indices
    tx_beam_angle_max = beam_angles[tx_index]
    rx_beam_angle_max = beam_angles[rx_index]

    # print(f"Maximum signal strength is at TX beam angle: {tx_beam_angle_max} and RX beam angle: {rx_beam_angle_max}")

    '''
    Plot for Max Power
    '''
    sns.set()  # Set the default Seaborn style
    plt.figure(figsize=(20, 10))  # Adjust the figure size

    # Plot the heatmap
    ax = sns.heatmap(max_signal_powers) #vmin=-32, vmax=-29

    # Set all beam_angles as tick labels for x and y axes
    ax.set_xticks(list(range(len(beam_angles))))
    ax.set_yticks(list(range(len(beam_angles))))
    ax.set_xticklabels(beam_angles[::-1], rotation=45)
    ax.set_yticklabels(beam_angles, rotation=0)


    # Add a label to the colorbar
    cbar = ax.collections[0].colorbar
    cbar.set_label('Signal Recieved Power from 3000 IQ Samples/beam in dBm', rotation=270, labelpad=20)
    # Add a label to the colorbar
    cbar = ax.collections[0].colorbar
    # cbar.set_ticks([-30, -31, -32])  # Manually set tick locations
    # cbar.set_ticklabels(['-30', '-31', '-32'])  # Manually set tick labels

    plt.xlabel('RX Beam Angle')
    plt.ylabel('TX Beam Angle')
    plt.title('Tx-Rx Signal Recieved Power Heatmap at 2m without whiteboard')
    plt.tight_layout()  # To ensure everything fits nicely
    # Save the plot to a file
    plt.savefig("RecievedPower_heatmap_2m_withWhiteboard.png", dpi=300, bbox_inches='tight')
    plt.show()



def plotheatmap_and_return_best_beam_in_dbm_selected_beam():
    # Define the number of beams and samples per beam
    num_beams = 63
    samples_per_beam = 3928
    beam_angles = [-45.0, -43.5, -42.1, -40.6, -39.2, -37.7, -36.3, -34.8, -33.4, -31.9, -30.5, -29.0, -27.6, -26.1, -24.7, -23.2, -21.8, -20.3, -18.9, -17.4, -16.0, -14.5, -13.1, -11.6, -10.2, -8.7, -7.3, -5.8, -4.4, -2.9, -1.5, 0, 1.5, 2.9, 4.4, 5.8, 7.3, 8.7, 10.2, 11.6, 13.1, 14.5, 16.0, 17.4, 18.9, 20.3, 21.8, 23.2, 24.7, 26.1, 27.6, 29.0, 30.5, 31.9, 33.4, 34.8, 36.3, 37.7, 39.2, 40.6, 42.1, 43.5, 45.0]

    # Initialize arrays to store the signal strength and power
    signal_strength = np.empty((num_beams, num_beams))
    avg_signal_powers = np.empty((num_beams, num_beams))
    max_signal_powers = np.empty((num_beams, num_beams))
    
    # Loop through each Tx beam file
    for tx_beam in range(num_beams):
        try:
            # Initialize lists to store mean strength values and powers for each Rx beam
            mean_strengths = []
            avg_powers_in_dBm = []
            max_powers_in_dBm = []
            
            # Try to open the file for reading
            with open(f'tx_beam_angle_{tx_beam}.dat', 'rb') as f:
                # Loop through each Rx beam
                for rx_beam in range(num_beams):
                    # Read samples for the current Rx beam
                    data_array = np.fromfile(f, dtype=np.complex64, count=samples_per_beam)
                    
                    # Get the received powers for each sample
                    IQ_power_dBm, avg_power_dBm, max_power_dBm = calibration.calculate_power_metrics(data_array)

                    # Compute the mean absolute value of the samples
                    mean_strength = round(np.mean(np.abs(data_array)), 4)
                    avg_power_dBm = round(avg_power_dBm, 2)
                    max_power_dBm = round(max_power_dBm, 2)

                    # Append the mean strength and powers to the lists
                    mean_strengths.append(mean_strength)
                    avg_powers_in_dBm.append(avg_power_dBm)
                    max_powers_in_dBm.append(max_power_dBm)
                    
        except Exception as e:
            print(f"An error occurred while processing tx_beam_angle_{tx_beam}.dat: {e}")
            # Fill the lists with -100 dBm if the file cannot be opened/read
            mean_strengths = [-100] * num_beams
            avg_powers_in_dBm = [-100] * num_beams
            max_powers_in_dBm = [-100] * num_beams

        # Store the mean strength values and powers in the respective arrays
        signal_strength[tx_beam, :] = mean_strengths
        avg_signal_powers[tx_beam, :] = avg_powers_in_dBm
        max_signal_powers[tx_beam, :] = max_powers_in_dBm

        print("Signal Strength_array Shape = ",signal_strength.shape)
    print("Avg_power_array Shape = ",avg_signal_powers)
    print("Max_power_array Shape = ",max_signal_powers)

    # Find the index of the maximum value in the signal_strength array
    index_max = np.argmax(signal_strength)

    # Convert the flat index to a 2D index (row, column)
    tx_index, rx_index = np.unravel_index(index_max, signal_strength.shape)

    # Extract the corresponding beam angles using the indices
    tx_beam_angle_max = beam_angles[tx_index]
    rx_beam_angle_max = beam_angles[rx_index]

    # print(f"Maximum signal strength is at TX beam angle: {tx_beam_angle_max} and RX beam angle: {rx_beam_angle_max}")


    '''
    Save the recieved powers to a CSV file and plot the heatmap
    '''
    # Prepare the data
    # Create a DataFrame from the max_signal_powers array
    df = pd.DataFrame(max_signal_powers)

    # Add Tx and Rx beam angles as the index and column names
    df.index = beam_angles  # Assuming beam_angles is a list of Tx beam angles
    df.columns = beam_angles  # Assuming the same angles are used for Rx

    # Optionally, if you want to "melt" the DataFrame to have a long-form DataFrame with Tx, Rx, and Power columns, you can do:
    df_melted = df.reset_index().melt(id_vars='index', var_name='Rx', value_name='Power')
    df_melted.rename(columns={'index': 'Tx'}, inplace=True)

    # Save to CSV
    df.to_csv("max_signal_powers_2.4m_RFM06009.csv", index=True)  # Save the original matrix form
    # df_melted.to_csv("max_signal_powers_longform.csv", index=False)  # Save the long-form data


    '''
    Plot for Max Power with Custom Colormap
    '''
    # Custom colormap from black (lowest power) to blue (medium power) to red (highest power)
    colors = ["black", "blue", "red"]  # Black to Blue to Red
    n_bins = 10000  # Use 200 bins to make the transition smooth
    cmap_name = "custom_black_blue_red"
    custom_black_blue_red = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bins)

    sns.set()  # Set the default Seaborn style
    plt.figure(figsize=(20, 10))  # Adjust the figure size

    # Plot the heatmap with the custom black-to-blue-to-red colormap
    ax = sns.heatmap(max_signal_powers, cmap=custom_black_blue_red, vmin=-80, vmax=-25)
    # Set all beam_angles as tick labels for x and y axes
    ax.set_xticks(list(range(len(beam_angles))))
    ax.set_yticks(list(range(len(beam_angles))))
    ax.set_xticklabels(beam_angles[::-1], rotation=45)
    ax.set_yticklabels(beam_angles, rotation=0)

    # Add a label to the colorbar
    cbar = ax.collections[0].colorbar
    cbar.set_label('Signal Received Power from 3000 IQ Samples/beam in dBm', rotation=270, labelpad=20)

    plt.xlabel('RX Beam Angle')
    plt.ylabel('TX Beam Angle')
    plt.title('Exhaustive Beam Sweeping of Tx-Rx Angles Signal Received Power Heatmap at 2.4m')
    plt.tight_layout()  # To ensure everything fits nicely

    # Save the plot to a file
    plt.savefig("ReceivedPower_heatmap_2.4m_RFM6005.png", dpi=300, bbox_inches='tight')
    plt.show()




# plotheatmap_and_return_best_beam_in_dbm_selected_beam()