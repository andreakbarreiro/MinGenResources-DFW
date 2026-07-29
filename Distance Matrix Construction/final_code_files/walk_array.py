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

def load_map(mapp):
    """
    Loads the OSM street map from your directory/saved files (see grabbing_osm_maps.ipynb to pull and save the OSM maps) 
    
    Args:
    mapp (str): the filepath to the multidi graph

    Returns: 
    G (nx.MultiDiGraph): the street network
    nodes (list): a list of the nodes to which each the resource locations are mapped 

    """    
    with open(mapp, 'rb') as f:
        G = pickle.load(f)
    nodes = ox.distance.nearest_nodes(G, sites["geometry"].x, sites["geometry"].y)
    return nodes, G

def comp_walk_dist_col(nodes, G):

    """
    For every resource location, calculate the shortest path from and to the task_id resource location

    Args: 
    G (nx.MultiDiGraph): the street network
    nodes (list): a list of the nodes to which each the resource locations are mapped 

    Returns: 
    
    dists (np.array): contains walking distances between the task_id resource location and every other resource
    """

    # base matrix for distance calculations
    dists = np.zeros((len(nodes),1))

    # compute shortest path length between each node
    # put dist(a,b) as entry (a,b) in distances matrix
    # if dist(a,b) = dist(b,a) then put dist(a,b) as entry in distances matrix

    for p in range(len(sites)):
        if nodes[task_id] != nodes[p]: 
            #is nodes[track_id] the same as the node associated with sites[track_id]??
            d = nx.shortest_path_length(G, nodes[task_id], nodes[p], weight='length')
            dists[p] = d
        else: 
            dists[p] = 0
    return dists

# In[6]:

def comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1]):

    """
    Runs all functions defined above.
    """
    
    nodes_walk, G_walk = load_map("Dallas_bbox_walk.pkl")
    print('walk: map + nodes loaded')
    dists_walk = comp_walk_dist_col(nodes_walk, G_walk)
    time_walk = sec_from_mtr(dists_walk)
    print("finished walk matrix")

    file_path_as_list = file_name.split('/')[:-1]
    file_title = file_name.split('/')[-1]
    file_title = file_title.split('.')[0]
    file_path = '/'.join(file_path_as_list)
    file_path = Path(f"{file_path}/{file_title}/walk_cols")
    file_path.mkdir(parents=True, exist_ok=True)
    
    np.savez(f"{file_path}/walk_col_{task_id}", dists_walk = dists_walk, time_walk = time_walk)


# In[8]:


#computes all matrices for full sample set
comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1])

print('COMPLETE')

# In[ ]:




