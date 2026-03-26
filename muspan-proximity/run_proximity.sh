#!/bin/bash
#SBATCH --job-name=muspan_single
#SBATCH --output=muspan_%j.out
#SBATCH --error=muspan_%j.err
#SBATCH --time=06:00:00
#SBATCH --cpus-per-task=48
#SBATCH --partition=compute
#SBATCH --mail-user=insert-email
#SBATCH --mail-type=FAIL


# Fail fast if anything breaks
set -euo pipefail

# Initialise conda
source "$(conda info --base)/etc/profile.d/conda.sh"

# Activate environment
# here I consider that muspan_env is an environment that is already created and available on Alma
conda activate muspan_env

# Run Muspan
python muspan-hpc_proximity.py \
  --inputs /data/path/samples \
  --output /data/path/results \
  --path_classes_to_investigate /data/path/classes \
  --max_edge_distance integer_for_proximity_network \
  --create_total_arrays boolean_true_false