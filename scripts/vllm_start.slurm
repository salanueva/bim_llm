#!/bin/bash
#SBATCH --job-name=vllm-server
#SBATCH --cpus-per-task=1
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --mem=64GB
#SBATCH --gres=gpu:1
#SBATCH --output=vllm_server.log
#SBATCH --error=vllm_server.err

# Activate the virtual environment with the vllm package
source "$PYTHONPATH/bin/activate"

# Set cache directory
# export HF_HOME="/ncache/hub"

vllm serve Qwen/Qwen3-8B --port 8008 --gpu-memory-utilization 0.9 # To verbalize output and generate code for the sandbox
