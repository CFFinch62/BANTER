#!/bin/bash

VENV_DIR="venv"

# Check if venv exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Running setup..."
    if [ -f "./setup.sh" ]; then
        chmod +x ./setup.sh
        ./setup.sh
        if [ $? -ne 0 ]; then
            echo "Setup failed. Exiting."
            exit 1
        fi
    else
        echo "Error: setup.sh not found. Please verify project files."
        exit 1
    fi
fi

# Activate venv and run
source "$VENV_DIR/bin/activate"
python3 main.py
