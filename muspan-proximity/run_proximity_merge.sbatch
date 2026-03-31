#!/bin/bash
#SBATCH --job-name=muspan_merge
#SBATCH --output=logs/muspan_merge_%j.out
#SBATCH --error=logs/muspan_merge_%j.err
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --time=01:00:00

set -euo pipefail

# -----------------------------
# User settings
# -----------------------------
OUTPUT_DIR="/path/to/output"
PROXIMITY_SCRIPT="/path/to/muspan-hpc_proximity.py"

source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate muspan_env

echo "Starting merge..."

python "${PROXIMITY_SCRIPT}" \
    --output "${OUTPUT_DIR}" \
    --merge_only

echo "Merge completed"