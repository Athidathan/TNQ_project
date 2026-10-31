#!/usr/bin/env bash
set -euo pipefail

# Parse arguments and optional flags
REASON_FLAG=""
POLICY_FLAG=""
POSITIONAL=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --reason|-r)
      REASON_FLAG="--reason"
      shift
      ;;
    --policy|-p)
      POLICY_FLAG="--policy $2"
      shift 2
      ;;
    *)
      POSITIONAL+=("$1")
      shift
      ;;
  esac
done

if [ "${#POSITIONAL[@]}" -ne 2 ]; then
    echo "Usage: $0 [--reason] [--policy ambiguous|dmy|mdy|infer] <input_folder> <output_csv>" >&2
    exit 2
fi

# Resolve paths to absolute paths before changing directory
INPUT=$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "${POSITIONAL[0]}")
OUTPUT=$(python3 -c 'import os, sys; print(os.path.abspath(sys.argv[1]))' "${POSITIONAL[1]}")

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$REPO_ROOT"

# shellcheck disable=SC2086
PYTHONPATH=src python3 -m received_date.cli "$INPUT" "$OUTPUT" $REASON_FLAG $POLICY_FLAG
