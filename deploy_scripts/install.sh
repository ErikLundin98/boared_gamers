#!/bin/bash
ECHO "Installing environment"

test -d venv|| python3 -m venv venv
source venv/bin/activate

make install_unix