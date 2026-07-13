#!/bin/bash

VENV_DIR="venv"

echo "Setting up Banter IDE..."

# Create virtual environment
python3 -m venv "$VENV_DIR"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

# Activate venv
source "$VENV_DIR/bin/activate"

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install requirements."
    exit 1
fi

echo ""
echo "Setup complete. Run './run.sh' to start Banter IDE."
