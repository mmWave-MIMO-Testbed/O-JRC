#!/bin/bash -x 
echo "This is a script to generate packets"

# Find Qt Creator
qtcreator_path=$(which qtcreator)

# Set the correct project path
project_path="./step_2_packet_generate/mimo-ofdm-packet-generator.pro"


# Open the project in Qt Creator
$qtcreator_path $project_path

