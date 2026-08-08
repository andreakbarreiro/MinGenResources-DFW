### Data Descriptions

#### holes_no_parks.geojson - isochrone geometries used in coverage_plots.ipynb
   - eps: the walking distances for which the isochrones are included in the dataset. This data contains holes/coverage for areas that are within a 10-, 15-, and 20-minute walk.
   - holes: geometries for the "holes" where there is no access to parks at the "eps" value
   - geometry: geometries for the "coverage" where there is no access to parks at the "eps" value

#### demographic_data/

1. age.csv - from data.census.gov table P15 | POPULATION IN HOUSEHOLDS BY AGE

U.S. Census Bureau. "POPULATION IN HOUSEHOLDS BY AGE." Decennial Census, DEC Demographic and Housing Characteristics, Table P15, https://data.census.gov/table/DECENNIALDHC2020.P15?q=p15&t=Age+and+Sex&g=050XX00US48113$1500000. Accessed on 15 Jul 2026.

2. median_income.csv - from data.census.gov table B19013 | Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars)

U.S. Census Bureau. "Median Household Income in the Past 12 Months (in 2024 Inflation-Adjusted Dollars)." American Community Survey, ACS 5-Year Estimates Detailed Tables, Table B19013, https://data.census.gov/table/ACSDT5Y2024.B19013?t=Income+and+Poverty&g=050XX00US48113$1500000. Accessed on 15 Jul 2026.

3. poverty.csv - from data.census.gov table B17010 | Poverty Status in the Past 12 Months of Families by Family Type by Presence of Related Children Under 18 Years by Age of Related Children

U.S. Census Bureau. "Poverty Status in the Past 12 Months of Families by Family Type by Presence of Related Children Under 18 Years by Age of Related Children." American Community Survey, ACS 5-Year Estimates Detailed Tables, Table B17010, https://data.census.gov/table/ACSDT5Y2024.B17010?t=Income+and+Poverty&g=050XX00US48113$1500000. Accessed on 15 Jul 2026.

4. tl_2020_48_bg.shp - census block groups in Texas. It is a large file that isn't included here but can be found using the link in the following citation

U.S. Census Bureau, “tl_2020_48_bg”, TIGER/Line Shapefiles, 2020, https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.2020.html, accessed on July 15, 2026.

5. dallas_county_block_groups.geojson - census block groups in Dallas County only using tl_2020_48_bg.shp

6. geo_age.csv - population age data merged with the corresponding block group geometries
   - GEO_ID: GEO ID associated with the census block group
   - INTPTLAT, INTPTLON: latitude and longitude associated with the census block group
   - Total: Total number of individuals in the block group
   - Children: Number of individuals under 18 in the block group
   - Adults: Number of individuals who are 18 and older in the block group
   - percent_child: Percent of individuals in the block group who are under 18
   - geometry: geometry of the block group for plotting

7. geo_income.csv - income data merged with the corresponding block group geometries
   - GEO_ID: GEO ID associated with the census block group
   - INTPTLAT, INTPTLON: latitude and longitude associated with the census block group
   - Median_Income: Median Household Income in the Past 12 Months in 2024 Inflation-Adjusted Dollars for the block group
   - geometry: geometry of the block group for plotting

8. geo_poverty.csv - poverty status data merged with the corresponding block group geometries
   - GEO_ID: GEO ID associated with the census block group
   - INTPTLAT, INTPTLON: latitude and longitude associated with the census block group
   - households: total number of households in the block group
   - households_below_poverty: number of households below the poverty level in the block group
   - married_with_children: number of households that are a married-couple with related children under 18 and under the poverty level in the block group
   - male_with_children: number of households that are a male householder with related children under 18 and under the poverty level in the block group
   - female_with_children: number of households that are a female householder with related children under 18 and under the poverty level in the block group
   - percent_below: percent of households in the block group that are below the poverty level
   - households_with_children: number of households in the block group who have related children under 18 and under the poverty level
   - child_poverty_percent: percent of households in the block group who have related children under 18 and under the poverty level
   - geometry: geometry of the block group for plotting

#### grid_intersection
1. grid_intersect_centroids.shp - (and other required file formats for the .shp) contains the centroids of the subdivisions of the park polygons after intersection with the grid
2. grid_intersect.geojson - contains the geometries and park information for the parks subdivided from the grid intersection

#### original_centroids
1. centroids.shp - (and other required file formats for the .shp) contains centroids for the parks (One centroids for each park, before the intersection with the grid took place.)

#### parks_data
1. Counties.geojson - dataset of counties in Texas from REU python bootcamp (https://github.com/SMUREU/python_bootcamp/tree/main/data).
2. dallas_county_parks.shp - dataset of only the existing parks within dallas county
3. Parks_(2024).geojson - dataset of parks from North Central Texas Council of Governments (NCTCOG). NCTCOG copyright notice concering the data:
"Data, products, and services contained herein are copyright North Central Texas Council of Governments (NCTCOG). All reproduced or redistributed information should include the original NCTCOG copyright notice in an appropriate place. Any derivative work that makes use of NCTCOG data,
products, or services should include an appropriately placed credit reference in substantial conformity with the following: “Data from the North Central Texas Council of Governments were used in the preparation of this product.” 
