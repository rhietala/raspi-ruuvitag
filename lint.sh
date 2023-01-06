#!/usr/bin/env sh

python3 -m isort *.py
python3 -m black *.py
python3 -m pylint *.py
python3 -m mypy *.py
python3 -m flake8 *.py
