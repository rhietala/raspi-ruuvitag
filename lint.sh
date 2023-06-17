#!/usr/bin/env sh

python3 -m black -l 79 *.py
python3 -m mypy *.py
ruff *.py
