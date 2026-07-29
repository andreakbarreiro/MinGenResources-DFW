#!/bin/bash
#SBATCH -J array_job_aubrey
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -a 0-163
#SBATCH --output=../../%x_%A/%x.o%A.%a.log
#SBATCH --error=../../%x_%A/%x.o%A.%a.log
#SBATCH -p standard-s
#SBATCH --mem=50G
#SBATCH --cpus-per-task=2
#SBATCH -t 12:00:00

module purge
module load conda
conda activate geo_env

set -x  
set -e  

#running block_labeler.py file for permutation testing purposes

# Execute using the direct path to your geo_env python binary
/users/rtraverfallick/.conda/envs/geo_env/bin/python -u '../../Schools/block_labeler.py' ${SLURM_ARRAY_TASK_ID}