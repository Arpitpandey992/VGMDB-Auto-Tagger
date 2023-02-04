#!/bin/bash

CWD=$(pwd)
for d in */ ; do
    cd "$d"
    source /home/arpit/Programming/Python/VGMDB-Auto-Tagger/venv/bin/activate
    python ~/Programming/Python/VGMDB-Auto-Tagger/albumTagger.py "$(pwd)" --yes
    cd "$CWD"
done
