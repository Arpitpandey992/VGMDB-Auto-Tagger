#!/bin/bash

CWD=$(pwd)

# Define a function to run the command for a given directory in a new terminal window
function run_command {
    dir="$1"
    abs_dir=$(realpath "$dir") # Convert relative path to absolute path
    konsole --workdir "$abs_dir" -e bash -c "source /home/arpit/Programming/Python/VGMDB-Auto-Tagger/.venv/bin/activate && python ~/Programming/Python/VGMDB-Auto-Tagger/albumTagger.py \"$abs_dir\" --yes"
    wait
    sleep 20
    kill $(jobs -p) # Close the terminal window
}

# Export the function to make it available to xargs
export -f run_command

# Call the function for each directory in a separate terminal window
find . -maxdepth 1 -type d -print0 | xargs -0 -n 1 -P 4 -I {} bash -c 'run_command "{}"'
