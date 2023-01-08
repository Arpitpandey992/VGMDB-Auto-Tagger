#!/bin/bash

CWD=$(pwd)
for d in */ ; do
    cd "$d"
    python "/home/arpit/Programming/Python/VGMDB-Auto-Tagger/albumTagger.py" "$(pwd)" -en
    cd "$CWD"
done
