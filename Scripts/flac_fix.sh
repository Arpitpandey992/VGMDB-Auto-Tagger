#!/bin/bash

# Set the input directory to the current working directory
input_dir="$(pwd)"

# Set the output directory to a subdirectory named "fixed_flacs" of the current working directory
output_dir="$input_dir/fixed_flacs"

# Create the output directory if it doesn't already exist
mkdir -p "$output_dir"

# Loop over all FLAC files in the input directory
for input_file in "$input_dir"/*.flac; do
  # Set the output file path
  output_file="$output_dir/$(basename "$input_file" .flac).flac"

  # Convert the input file to WAV format
  ffmpeg -i "$input_file" -map_metadata 0 -c:a pcm_s16le output.wav

  # Convert the WAV file back to FLAC format
  ffmpeg -i output.wav -map_metadata 0 -c:a flac -compression_level 8 "$output_file"

  # Clean up the intermediate WAV file
  rm output.wav
done
