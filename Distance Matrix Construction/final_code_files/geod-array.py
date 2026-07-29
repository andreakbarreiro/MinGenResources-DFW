#!/usr/bin/env python
# coding: utf-8

# In[1]:

print('file running')

import geopandas as gpd
import pandas as pd
import numpy as np
import geopy.distance
from shapely.geometry import Point, LineString, Polygon
from shapely.geometry import MultiPoint
import networkx as nx
import osmnx as ox
import osmnx.routing as routing
import random
import sys
import os
from pathlib import Path
import time
import pickle

print('packages loaded')


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

#load in data
sites = gpd.read_file(file_name)
print('data loaded yay')


#creating a data frame with only the row corresponding to the task_id
sites_task = pd.DataFrame(sites.iloc[task_id]).transpose().reset_index()

#turning the single row back into a gpd data frame
sites_task = gpd.GeoDataFrame(sites_task, 
                            geometry = "geometry", 
                            crs = 'EPSG:4326'
                           ).iloc[0]
print('created task site data')

# In[3]:

# define functions for geodesic

# compute geodesic distance between two given points a and b
def get_dist(a, b):
    """
    Compute geodesic distance between two given points a and b.
    """
    
    origin = (a.y, a.x)
    #str(a.y)+','+str(a.x)
    destination = (b.y, b.x)
    #str(b.y)+','+str(b.x)
    dist = geopy.distance.geodesic(origin, destination)
    return dist.m

print('Get dist complete.')

def comp_geod_dist_col(col):
    """
    Compute geodesic distance (in meters) between the task site and all other sites in the data frame
    """
    dists = np.zeros(len(sites))
    for i, dest in sites.iterrows():
        dists[i] = get_dist(col.geometry,dest.geometry)
    return dists

def sec_from_mtr(dists_mtr):
    """
    Converts units of a distance matrix from meters to walking time using an average walk speed 
    """
    walk_speed = 1.42 # meters/sec
    dists_sec = dists_mtr / walk_speed
    dists_min = dists_sec
    return dists_min

# In[6]:

def comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1]):

    """
    Runs all functions defined above and saves the resultant matrix.
    """
    dists_geod = comp_geod_dist_col(sites_task)
    time_geod = sec_from_mtr(dists_geod)
    print("finished geodesic matrix")

    #define file path and create directory for saving
    file_path_as_list = file_name.split('/')[:-1]
    file_title = file_name.split('/')[-1]
    file_title = file_title.split('.')[0]
    file_path = '/'.join(file_path_as_list)
    file_path = Path(f"{file_path}/{file_title}/geod_cols")
    file_path.mkdir(parents=True, exist_ok=True)

    #saving
    np.savez(f"{file_path}/geod_col_{task_id}", dists_geod = dists_geod, time_geod = time_geod)

# In[8]:


#computes all matrices for full sample set
comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1])

print('COMPLETE')

# In[ ]:




