#!/bin/bash
#SBATCH -J multi_input
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -a 1-3
#SBATCH --output=../../%x_%A/%x.o%A.%a.log
#SBATCH --error=../../%x_%A/%x.o%A.%a.log
#SBATCH -p standard-s
#SBATCH --mem=30G
#SBATCH --cpus-per-task=2
#SBATCH -t 12:00:00

module purge
module load conda
conda activate geo_env

set -x  
set -e  

# Create an array of your input values (files, numbers, or parameters)
inputs=("geod-array.py" "walk_array.py" "drive_array.py")

# Map SLURM_ARRAY_TASK_ID to bash array index (arrays are 0-indexed, so we subtract 1)
INDEX=$((SLURM_ARRAY_TASK_ID - 1))
CURRENT_INPUT=${inputs[$INDEX]}

DATA_FILE=$2

echo "Running task $SLURM_ARRAY_TASK_ID with input: $CURRENT_INPUT and data file: $DATA_FILE"

# Execute using the direct path to your geo_env python binary
sbatch ./array_job_test.sh $CURRENT_INPUT $DATA_FILE

echo "Job task $SLURM_ARRAY_TASK_ID completed successfully. Deleting logs..."
sleep 5 && rm -f "../../${SLURM_ARRAY_JOB_NAME}_${SLURM_ARRAY_JOB_ID}/${SLURM_ARRAY_JOB_NAME}.o${SLURM_ARRAY_JOB_ID}.${SLURM_ARRAY_TASK_ID}.log
