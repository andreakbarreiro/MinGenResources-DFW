#!/bin/bash
#SBATCH -J array_job_test
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -a 0-83
#SBATCH --output=logs/%x.o%A.%a.log
#SBATCH --error=logs/%x.o%A.%a.log
#SBATCH -p standard-s
#SBATCH --mem=10G
#SBATCH --cpus-per-task=2
#SBATCH -t 12:00:00

module purge
module load conda
conda activate geo_env

set -x  
set -e  

# Execute using the direct path to your geo_env python binary
/users/rtraverfallick/.conda/envs/geo_env/bin/python -u test_parks_whole.py ${SLURM_ARRAY_TASK_ID}
