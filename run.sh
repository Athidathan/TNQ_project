#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_folder> <output_csv>" >&2
    exit 2
fi

# Resolve input and output paths to absolute paths before changing directory
INPUT=$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "$1")
OUTPUT=$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "$2")

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

PYTHONPATH=src python3 -m received_date.cli "$INPUT" "$OUTPUT"
