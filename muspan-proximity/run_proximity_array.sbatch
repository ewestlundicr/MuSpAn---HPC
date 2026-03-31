#!/bin/bash
#SBATCH --job-name=muspan_array
#SBATCH --output=logs/muspan_array_%A_%a.out
#SBATCH --error=logs/muspan_array_%A_%a.err
#SBATCH --array=0-139%40
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00

set -euo pipefail

# -----------------------------
# User settings
# -----------------------------
INPUT_DIR="$1"
OUTPUT_DIR="$2"
CLASSES="$3"
DOMAIN_LIST="$4" # the .txt file that contains the list of domain path
MAX_EDGE_DISTANCE="$5"

PROXIMITY_SCRIPT="muspan-hpc_proximity.py"

# Initialise conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate environment
# here I consider that muspan_env is an environment that is already created and available on Alma
conda activate muspan_env

mkdir -p "${OUTPUT_DIR}"
mkdir -p logs

# -----------------------------
# Read one domain name from file
# -----------------------------
DOMAIN_NAME=$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "${DOMAIN_LIST}")

if [ -z "${DOMAIN_NAME}" ]; then
    echo "No domain found for SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}"
    exit 1
fi

DOMAIN_PATH="${INPUT_DIR}/${DOMAIN_NAME}"

if [ ! -e "${DOMAIN_PATH}" ]; then
    echo "Domain path does not exist: ${DOMAIN_PATH}"
    exit 1
fi

echo "=================================================="
echo "Job ID: ${SLURM_JOB_ID}"
echo "Array Task ID: ${SLURM_ARRAY_TASK_ID}"
echo "Domain: ${DOMAIN_NAME}"
echo "Domain path: ${DOMAIN_PATH}"
echo "Start time: $(date)"
echo "=================================================="

# run the proximity script without attempting a merge step
python "${PROXIMITY_SCRIPT}" \
    --inputs "${INPUT_DIR}" \
    --output "${OUTPUT_DIR}" \
    --path_classes_to_investigate "${CLASSES}" \
    --max_edge_distance "${MAX_EDGE_DISTANCE}" \
    --create_total_arrays 0 \
    --domain "${DOMAIN_PATH}"

echo "Finished domain: ${DOMAIN_NAME}"
echo "End time: $(date)"
