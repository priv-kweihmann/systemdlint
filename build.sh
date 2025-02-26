#!/bin/sh
python3 -m pip install --upgrade pip build
python3 -m build --sdist --wheel
