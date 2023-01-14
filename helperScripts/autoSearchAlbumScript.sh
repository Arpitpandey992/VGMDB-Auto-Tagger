#!/bin/bash
#tag is an alias for python path_to_albumTagger.py
CWD=$(pwd)
for d in */ ; do
    cd "$d"
    tag "$(pwd)" --yes
    cd "$CWD"
done
