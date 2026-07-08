#!/bin/bash
#SBATCH -J array_job_test
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -a 0-1007
#SBATCH --output=../../logs_%A/%x.o%A.%a.log
#SBATCH --error=../../logs_%A/%x.o%A.%a.log
#SBATCH -p standard-s
#SBATCH --mem=20G
#SBATCH --cpus-per-task=2
#SBATCH -t 12:00:00

module purge
module load conda
conda activate geo_env

set -x  
set -e  

PYTHON_FILE=$1
DATA_FILE=$2

# Execute using the direct path to your geo_env python binary
/users/rtraverfallick/.conda/envs/geo_env/bin/python -u $PYTHON_FILE $DATA_FILE ${SLURM_ARRAY_TASK_ID}