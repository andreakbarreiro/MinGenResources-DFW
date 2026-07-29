#!/bin/bash
#SBATCH -J array_job_iso
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -a 0-163
#SBATCH --output=../../logs_%A/%x.o%A.%a.log
#SBATCH --error=../../logs_%A/%x.o%A.%a.log
#SBATCH -p standard-s
#SBATCH --mem=50G
#SBATCH --cpus-per-task=2
#SBATCH -t 12:00:00

module purge
module load conda
conda activate geo_env

set -x  
set -e  

DATA_FILE=$1

# $DATA_FILE is the name of the data file with the resource locations 
# This runs population calculations for the hole Multipolygons produced at every epsilon value 

# replace 'rtraverfallick' with your username, ensure that you've created the geo_env virtual environment 
# Execute using the direct path to your geo_env python binary
/users/rtraverfallick/.conda/envs/geo_env/bin/python -u 'minscaf_geod.py' $DATA_FILE ${SLURM_ARRAY_TASK_ID}