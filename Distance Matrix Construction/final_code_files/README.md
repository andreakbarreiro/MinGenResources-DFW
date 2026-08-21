# Distance Matrix Construction Organization 
- Dr.B_files/ : all original files provided by Dr. Barreiro
- final_code_files/ : all files created by Rae in Summer 2026 and used in production of final 3MT analyses
- comp_travel_time_mat.ipynb: functionalized version of Dr. B code, written by Maia in Summer 2026; used as the basis for .py and .sh scripts

## final_code_files/
### Shell scripts
1. array_block_labeler: running block_labeler.py file for permutation testing purposes
2. array_job_iso: running isochrone calculations for every resource site (for every row in DATA_FILE)
3. array_job_minscaf: runs population calculations for the hole Multipolygons produced at every epsilon value
4. array_job_test: runs geodesic, walk, or drive distance calculations

### Notebeooks
1. concat_isochrones: takes the individual isochrone matrices returned by array_job_iso.sh/iso_slurm.py and concatonates them into a single data frame where each row is a single resource location/point in the original resource data frame
2. concat_matrices: takes the distance matrix for each resource location that is returned by array_job_distance.sh and concatonate them into a single matrix
3. concat_pop: take in the population df for the hole at each epsilon value (returned by array_job_pop.sh) and concatonate them into a df
4. grabbing_osm_maps: load and save the osm street map for driving or walking distance and isochrone calculations
5. osm_holes: runs demographic calculations on 35 largest holes for parks data

### Python script
1. drive_array: creating drive matrix for a single resource site
2. walk_array: creating walk matrix for a single resource site
3. geod-array: creating geodesic matrix for a single resource site
5. iso_slurm: returns 10, 15, 20 minute isochrones around  a single resource site
6. minscaf_geod: takes the hole MultiPolygon produced at a single epsilon vlaue and finds relevant population information

### YAML file
1.  geo_env: file for creating CONDA environment 
