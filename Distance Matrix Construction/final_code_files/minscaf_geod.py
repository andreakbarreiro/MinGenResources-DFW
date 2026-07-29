#!/usr/bin/env python
# coding: utf-8
"""
This script takes the hole MultiPolygon produced at a single epsilon vlaue and finds relevant population information 
"""

# In[109]:

#importing packages
import geopandas as gpd
import pandas as pd
from pathlib import Path
import os 
import sys

# In[2]:


# getting job id and printing
job_id = os.environ.get("SLURM_ARRAY_JOB_ID")
print(f"Job ID: {job_id}")

#get task id from .sh file
task_id = int(sys.argv[2])
print(f"Running task {task_id}")

#take file name from .sh file
file_name = str(sys.argv[1])
print(f"File_name: {file_name}")

#reading in file
file = gpd.read_file(file_name)
file = file.reset_index()

#grabbing a single hole Multiploygon (aka the Multiploygon for a single eps value) 
county_holes = file.iloc[[task_id]]


# In[14]:

#defining some important parameters

sqm_to_sqmi = 2589988

# approximate number of meters in a mile
m_to_mi = 1609.34

# walk speed
walk_speed = 1.42

# coordinate systems
crs = {
    'census': 'EPSG:4269'  , # degrees: used by Census
    'projected': 'EPSG:3083', # projected: needed for map
    'area'  : 'ESRI:102003', # square meters
    'length': 'ESRI:102005', # meters
}


# In[19]:

#reading in the census block data
block_df = gpd.read_file("../../Data/dal_tx_block.shp")
print('loaded block data')

# removes all census blocks that had zero area
# turns out that these were bodies of water (checked by mapping)
# will this be an issue when we intersect things????? shouldnt matter i think???????
blocks = block_df[block_df["ALAND20"] != 0]

# compute population density of each census block
# add to block_df
blocks["pop_dens"] = (blocks["POP20"] / blocks["ALAND20"]) * sqm_to_sqmi


# project all of our data into projected crs
# apparently this is needed for mapping??? we should double check this probably...

blocks.geometry = blocks.geometry.to_crs(crs["projected"])

# establish placeholder lists to store population and area for each hole
county_area = []
county_pops = []

# grabbing the epsilon values and the actual hole Multipolygon
eps = county_holes['eps'].iloc[0]
shape = county_holes['geometry'].iloc[0]

#this should give me a series with all of the intersections between the hole and the census blocks
intersection_series = shape.intersection(blocks["geometry"])


# In[36]:
#checking whether the intersections are non-empty and are polygons/multipolygons
intersection_nonempty = intersection_series[~intersection_series.is_empty & (intersection_series.geom_type.isin(["Polygon", "MultiPolygon"]))]



# In[38]:

# print(len(intersection_series))
# print(len(intersection_nonempty))


# In[ ]:

# takes intersections series object and turns it into a geo data frame
intersection_gdf = gpd.GeoDataFrame(intersection_nonempty, geometry = 'geometry', crs = 'EPSG:3038')


# In[40]:
#get the area of the intersection chuncks
block_area = intersection_nonempty.area

# computes the population in the hole
pop = []

for index, value in block_area.items():
    #block area is a list?
    # block_dens = blocks.loc[index]["POP20"]
    # block_a = blocks.loc[index]["ALAND20"]
    # # intersect_area = value
    intersect_pop = value * (blocks.loc[index]["POP20"] / blocks.loc[index]["ALAND20"])
    pop.append(intersect_pop)


# In[99]:
#creating empty data frame for saving population information
output = pd.DataFrame([])
output.index = block_area.index


# In[103]:

output['eps'] = eps
output['pop'] = pop
output['area'] = block_area
output['intersection'] = intersection_nonempty

#defining path name and establishing directory
file_path_as_list = file_name.split('/')[:-1]
file_title = file_name.split('/')[-1]
file_title = file_title.split('.')[0]
file_path = '/'.join(file_path_as_list)
file_path = Path(f"{file_path}/{file_title}")
print(file_path)
file_path.mkdir(parents=True, exist_ok=True)

#we only needed the aggregate populatioin information for a single eps value
output_grouped = output.groupby('eps').agg({
    'pop': 'sum',         # Total sales per category
    'area': 'sum',     # Average quantity per category
    # 'Rating': 'max'         # Maximum rating per category
}).reset_index()

#saving
output_grouped.to_csv(f"{file_path}/pop_res{task_id}.csv")

# In[ ]:




