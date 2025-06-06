#!/bin/bash

echo "Running checks..."

echo "BLACK"
black . --line-length=79 --exclude=".venv"

echo "FLAKE8"
flake8 . --exclude=".venv"

echo "PYLINT"
pylint . --recursive=y --ignore-paths=".venv"

echo "MYPY"
mypy . --strict --exclude=".venv"

echo "PYDOCLINT"
pydoclint . --style=sphinx --check-class-attributes=False --skip-checking-short-docstrings=False  --exclude=".venv"

echo "SEMGREP"
semgrep scan --error --config auto --exclude=".venv"

echo "PYTEST"
pytest

echo "Checks complete!"
