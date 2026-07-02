#!/bin/bash
#SBATCH --job-name=parks_sample
#SBATCH -A abarreiro_topology_reu2026_0001
#SBATCH --output=parks_sample_%j.log
#SBATCH --error=parks_sample_%j.log
#SBATCH -p standard-s
#SBATCH --mem=10G
#SBATCH --cpus-per-task=2
#SBATCH --time=12:00:00
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=rtraverfallick@smu.edu

set -x  
set -e  

# Execute using the direct path to your geo_env python binary
/users/rtraverfallick/.conda/envs/geo_env/bin/python -u test_parks.py
