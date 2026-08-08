### Research Question

How are greens spaces distributed in Dallas County? What demographic patterns might be related to access to these spaces?

### Park Repository Organization

#### data/

1. demographic_data/ - contains demographic data related to income, poverty, and census block groups
2. grid_intersection/ - contains the parks subdivided following intersection with a grid and centroids for these polygons
3. notebooks/ - contains source code
4. parks_data/ - contains original data used to build the dataset of parks in dallas county
5. holes_no_parks.geojson - isochrone geometries. "no_parks" is in reference to the fact that we removed parks that were included in the "hole" area mistakenly as a result of how the isochrones are created.

For more information, data sources, and descriptions of the datasets please see the file titled "data_descriptions.md" in the data/ folder.

#### figures/
The naming convention for the figures is as follows: The first figure contains only the demographic data. The next three with "10", "15", and "20" place on top of the demographic data, the park coverage - areas that have a park within a 10-, 15-, and 20-minute walk respectively according to the isochrones produced.
1. children.png - number of children in each block group
2. children_10.png
3. children_15.png
4. children_20.png
5. households_below_poverty_level.png - number of households below the poverty level in each block group
6. households_below_poverty_level_10.png
7. households_below_poverty_level_15.png
8. households_below_poverty_level_20.png
9. households_children_below_poverty_level.png - number of households in each block group who have related children
10. households_children_below_poverty_level_10.png
11. households_children_below_poverty_level_15.png
12. households_children_below_poverty_level_20.png
13. income.png - median income for each block group
14. income_10.png
15. income_15.png
16. income_20.png
17. map_with_centroids.png - map of parks in Dallas County with centroids of each park plotted
18. percent_children.png - percent of households in each block group with children
19. percent_children_10.png
20. percent_children_15.png
21. percent_children_20.png
22. percent_households_below_poverty_level.png - percent of households in each block group who are below the poverty level
23. percent_households_below_poverty_level_10.png
24. percent_households_below_poverty_level_15.png
25. percent_households_below_poverty_level_20.png
26. percent_households_children_below_poverty_level.png - percent of households in each block group who have related children and are below the poverty level
27. percent_households_children_below_poverty_level_10.png
28. percent_households_children_below_poverty_level_15.png
29. percent_households_children_below_poverty_level_20.png
30. trinity_river_greenbelt_centroid.png - map showing the Trinity River Greenbelt with its centroid plotted
31. trinity_river_greenbelt_grid_intersection.png - map showing the Trinity River Greenbelt with the polygons that have been intersected with a grid
32. trinity_river_greenbelt_grid_intersection_centroids.png - map showing the Trinity River Greenbelt with the centroids of the polygons that have been intersected of the grid plotted

#### notebooks/

1. census_data_block_groups.ipynb - Cleaning demographic data and merging with corresponding block groups to create geo_age.geojson, geo_income.geojson, and geo_poverty.geojson in the data/census_data folder The process was first attempted with just census blocks but was unsuccessful as the census block data contained missing geometries.
2. coverage_plots.ipynb - Used for producing the figures for demographic data with isochrone coverage
3. intersection_centroids.ipynb - Having intersected the parks with a grid (see Process in ArcGIS Pro below), this computes the centroids for the new subdivided park areas
4.  park_centroids.ipynb - This was the first attempt at representing the parks as individual points by simply calculating the centroid of each park to create the centroids.shp data in the data/original_centroids/ folder. This also includes the code to narrow the parks down to existing parks in Dallas County to create the dallas_county_parks.shp data in the data/parks_data/ folder.
5. park_entrances.ipynb - an attempt to find the entrance points of parks

#### presentation/

three_minute_thesis_presentation.pdf - PDF of Three Minute Thesis Presentation

### Process in ArcGIS Pro
Recognizing in the park_centroids.ipynb that simply calculating the centroids of each park wasn't an accurate approach, we decided to intersect the parks with a grid, and then take the centroids of those intersected geometries to better represent the park area. Using the dallas_county_parks.shp data, we uploaded this to ArcGISPro and used the Geoprocessing Tool called "Create Fishnet". We selected "Extent of a Layer" for the grid extent and then set "Number of Rows" to 100 and "Number of Columns" to 100 for a 100 x 100 square grid. We then took the intersection between the dallas_county_parks and the grid using the Geoprocessing Tool called "Intersect". Using the output of this, we used the "Features to JSON" Geoprocessing Tool to obtain data/grid_intersection/grid_intersect.geojson which is used in intersection_centroids.ipynb.
