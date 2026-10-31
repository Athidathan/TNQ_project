#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# Verify python3 is installed
if ! command -v python3 >/dev/null 2>&1; then
    echo "Error: python3 is not installed or not found in PATH." >&2
    exit 1
fi

VENV_DIR="$REPO_ROOT/.venv"

# Setup virtual environment for running tests
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment for tests at $VENV_DIR..."
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        echo "Error: Failed to create virtual environment using 'python3 -m venv'." >&2
        echo "On Ubuntu/Debian systems, please install python3-venv:" >&2
        echo "  sudo apt-get update && sudo apt-get install -y python3-venv" >&2
        exit 1
    fi
fi

# Activate virtual environment
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Install test framework dependencies (pytest)
echo "Installing test dependencies from requirements.txt..."
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# Run test suite
echo "Executing pytest suite and generating test_report.csv..."
python -m pytest

echo "All tests finished successfully. test_report.csv updated."

