#!/bin/bash
#SBATCH -J walk_osm_matrix
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -o walk_osm_matrix-%j.out
#SBATCH -p standard-s
#SBATCH --mem=500M

module purge
module load conda
conda activate TDAEnv

python comp_travel_time_mat.py