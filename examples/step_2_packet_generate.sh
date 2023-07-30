#!/bin/bash -x 
echo "This is a script to generate packets"  

# Assign the output of `which qtcreator` to qtcreator_path
qtcreator_path=$(which qtcreator)

# Path to your .pro file. Replace this with the correct path.
project_path="./step_2_packet_generate/mimo-ofdm-packet-generator.pro"

# Use Qt Creator to open the .pro file
"$qtcreator_path" "$project_path" &