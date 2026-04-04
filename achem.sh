#!/bin/bash
# ACHEM Runner Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.achem-venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
pip install -q -e "$SCRIPT_DIR" 2>/dev/null
achem "$@"
