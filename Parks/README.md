### Park Repository Organization

#### Original_Data

Contains the original datasets.

Counties.geojson : File containing all counties in Texas, taken from Python bootcamp lecture

Parks_(2024).geojson : File of parks in North Texas from North Texas Central Council of Governments (https://data-nctcoggis.hub.arcgis.com/datasets/997fd22166de42ee962cae1c8e2c3d4b_3/explore)

### Original_Park_Centroids

park_centroids.ipynb - Narrows parks down to Dallas County, calculates centroids for each park
centroids.*** - Data for the parks' centroids
dallas_county_parks.geojson - Data for parks within Dallas County 
map_with_centroids.png - image of parks in Dallas county with centroids plotted

### Process in ArcGIS Pro
Using the dallas_county_parks data, we uploaded this to ArcGISPro and used the GeoProcessing Tool called "Create Fishnet". We selected "Extent of a Layer" for the grid extent and then set "Number of Rows" to 100 and "Number of Columns" to 100.

#### Grid_Intersection_Centroids

grid_intersect_centroids.***
