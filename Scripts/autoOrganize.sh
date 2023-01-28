#!/bin/bash

CWD=$(pwd)
for d in */ ; do
    cd "$d"
    python ~/Programming/Python/VGMDB-Auto-Tagger/organize.py "$(pwd)"
    cd "$CWD"
done
