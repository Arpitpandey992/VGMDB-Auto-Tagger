#!/bin/bash

CWD=$(pwd)
for d in */ ; do
    cd "$d"
    python ~/Programming/Python/VGMDB-Auto-Tagger/albumTagger.py "$(pwd)" --yes
    cd "$CWD"
done
