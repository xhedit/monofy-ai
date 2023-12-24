#!/bin/bash

export CUDA_LAUNCH_BLOCKING=1

# Check if NVIDIA GPU driver is installed
if command -v nvidia-smi &> /dev/null; then
    echo "NVIDIA GPU driver detected. Using CUDA."
    USE_CUDA=True
    TORCH_INDEX_URL=https://download.pytorch.org/whl/cu121
else
    echo "NVIDIA GPU driver not found. Assuming ROCm."
    USE_CUDA=False
    TORCH_INDEX_URL=https://download.pytorch.org/whl/nightly/rocm5.7
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    source venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt --extra-index-url $TORCH_INDEX_URL
    if [ "$USE_CUDA" = "False" ]; then
        ./venv/bin/python run.py "$@"
        exit
    fi
    # echo "Running accelerate config..."
    # accelerate config
else
    source venv/bin/activate
fi

./venv/bin/python run.py "$@"

# Experimental
# accelerate launch --num_processes=1 --num_machines=1 --mixed_precision=no --dynamo_backend=no run.py "$@"

deactivate