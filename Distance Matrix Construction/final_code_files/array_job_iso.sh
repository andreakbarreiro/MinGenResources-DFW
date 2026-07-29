#!/bin/bash
#SBATCH -J array_job_iso
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -a 0-10
#SBATCH --output=../../logs_%A/%x.o%A.%a.log
#SBATCH --error=../../logs_%A/%x.o%A.%a.log
#SBATCH -p htc
#SBATCH --mem=50G
#SBATCH --cpus-per-task=2
#SBATCH -t 12:00:00

module purge
module load conda
conda activate geo_env

set -x  
set -e  

DATA_FILE=$2
WALK_DRIVE=$1

# running isochrone calculations for every resource site (for every row in DATA_FILE)
# $DATA_FILE is the name of the data file with the resource locations 
# $WALK_DRIVE will either be 'walk' or 'drive' which will determine whether the script runs the walk of drive isochrones (when writing 'walk' or 'drive' in the shell command do NOT put quotes)

# Execute using the direct path to your geo_env python binary
#replace 'rtraverfallick' path with your name/username, ensure that you've created the geo_env virtual environment 
/users/rtraverfallick/.conda/envs/geo_env/bin/python -u '../../Minimal Scaffold/iso_slurm.py' $WALK_DRIVE $DATA_FILE ${SLURM_ARRAY_TASK_ID}