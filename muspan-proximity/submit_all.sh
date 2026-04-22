#!/usr/bin/env bash
set -euo pipefail

mkdir -p logs

# Default values (optional)
INPUT_DIR=""
OUTPUT_DIR=""
CLASSES=""
DOMAIN_LIST=""
MAX_EDGE_DISTANCE=20
SAVE_DOMAIN=false
SKIP_MERGE=false

# -----------------------------
# Parse named arguments
# -----------------------------
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --input_dir) INPUT_DIR="$2"; shift 2 ;;
        --output_dir) OUTPUT_DIR="$2"; shift 2 ;;
        --classes) CLASSES="$2"; shift 2 ;;
        --domain_list) DOMAIN_LIST="$2"; shift 2 ;;
        --max_edge_distance) MAX_EDGE_DISTANCE="$2"; shift 2 ;;
        --save_domain) SAVE_DOMAIN=true; shift 1 ;;
        --skip_merge) SKIP_MERGE=true; shift 1 ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
done

# -----------------------------
# Validate required arguments
# -----------------------------
: "${INPUT_DIR:?Missing --input_dir}"
: "${OUTPUT_DIR:?Missing --output_dir}"
: "${CLASSES:?Missing --classes}"
: "${DOMAIN_LIST:?Missing --domain_list}"
: "${MAX_EDGE_DISTANCE:?Missing --max_edge_distance}"

# -----------------------------
# Submit jobs
# -----------------------------
ARRAY_JOB_ID=$(sbatch run_proximity_array.sbatch \
    "${INPUT_DIR}" "${OUTPUT_DIR}" "${CLASSES}" "${DOMAIN_LIST}" "${MAX_EDGE_DISTANCE}" "${SAVE_DOMAIN}" \
    | awk '{print $4}')

echo "Submitted array job: ${ARRAY_JOB_ID}"

if [ "${SKIP_MERGE}" = "false" ]; then
    MERGE_JOB_ID=$(sbatch \
        --dependency=afterok:${ARRAY_JOB_ID} \
        run_proximity_merge.sbatch "${OUTPUT_DIR}" \
        | awk '{print $4}')
    echo "Submitted merge job: ${MERGE_JOB_ID}"
else
    echo "Skipping merge step (--skip_merge was set)."
fi
