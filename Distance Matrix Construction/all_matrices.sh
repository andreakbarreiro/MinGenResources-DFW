#!/bin/bash
#SBATCH -J walk_osm_matrix
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH -o walk_osm_matrix-%j.out
#SBATCH -p standard-s
#SBATCH --mem=10G

module purge
module load conda
conda activate geo_env

python 'test.py'
