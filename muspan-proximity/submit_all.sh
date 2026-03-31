#!/usr/bin/env bash
set -euo pipefail

mkdir -p logs

ARRAY_JOB_ID=$(sbatch run_promixity_array.sbatch | awk '{print $4}')
echo "Submitted array job: ${ARRAY_JOB_ID}"

MERGE_JOB_ID=$(sbatch --dependency=afterok:${ARRAY_JOB_ID} run_proximity_merge.sbatch | awk '{print $4}')
echo "Submitted merge job: ${MERGE_JOB_ID}"
