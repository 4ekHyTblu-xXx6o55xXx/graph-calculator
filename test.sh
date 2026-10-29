#!/bin/sh
set -e
python3 -m unittest discover -s tests -p "test_*.py" -v
