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

    # map each resource location to the nearest location on the street network
    nodes = ox.distance.nearest_nodes(G, sites["geometry"].x, sites["geometry"].y)
    return nodes, G

# calculates the shortest travel time between two given points
def comp_drive_path(p, nodes, G):
    """
    Calculates the shortest travel time between two given points

    Args: 
    p (int): the index of a single node in list nodes
    nodes (list): list of all locations in street network that we're interested in 
    G(nx.MutliDiGraph): the street network

    Returns: 
    gdf_edges (gpd.GeoDataFrame): df for which each row is a single edge within the driving path between two points 
    
    """
    path = routing.shortest_path(G, nodes[task_id], nodes[p], weight = "travel_time")
    
    #produce a gdf of the shortest path
    gdf_edges = routing.route_to_gdf(G, path, weight = "travel_time")
    
    return gdf_edges

def comp_drive_time(gdf_edges):
    """
    Computes drive time for a given path.
    
    """
    return gdf_edges["travel_time"].sum()

# ccomputes distance of a given path
def comp_drive_dist(gdf_edges):
    """
    Computes drive distance for a given path.
    
    """
    return gdf_edges["length"].sum()

# computes matrix of driving times between points
def comp_all_drive_col(nodes, G):

    """
    Computes matrix of driving times between the task_id resource location (i.e. the single location in sites) and every other resource 

    Args: 
    nodes (list): list of all locations in street network that we're interested in 
    G(nx.MutliDiGraph): the street network

    Returns: 
    dists (np.array): contains driving distances between the task_id resource location and every other resource 
    times (np.array): contains driving times between the task_id resource location and every other resource 
   
    """
    # base matrix for distance calculations
    dists = np.zeros(len(nodes))
    times = np.zeros(len(nodes))
    
    # add speed limit information to graph G
    G = routing.add_edge_speeds(G, agg = np.mean)
    G = routing.add_edge_travel_times(G)
    print('added travel speeds and times')
    
    # compute shortest path length between each node
    # put dist(a,b) as entry (a,b) in distances matrix
    # if dist(a,b) = dist(b,a) then put dist(a,b) as entry in distances matrix
    for p in range(len(sites)):
        if nodes[task_id] != nodes[p]:
            gdf_edges = comp_drive_path(p, nodes, G)
            print('got_path')
            d = comp_drive_dist(gdf_edges)
            print('comped_drive')
            t = comp_drive_time(gdf_edges)
            print('comped_time')
        
            dists[p] = d
            times[p] = t
        else: 
            dists[p] = 0
            times[p] = 0
        
    return dists, times


# In[6]:

def comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1]):
    """
    Runs all functions defined above. 
    """
    
    try: 
        print('started driving calculations')
        # drive
        nodes_drive, G_drive = load_map("Dallas_bbox_drive.pkl")
        print('drive: map + nodes loaded')
        
        dists_drive, time_drive = comp_all_drive_col(nodes_drive, G_drive)
        
        print("finished drive matrix")

    except Exception as E: 
        print(f"Error: {E}")

    #defining file path and directory to save the data to  
    file_path_as_list = file_name.split('/')[:-1]
    file_title = file_name.split('/')[-1]
    file_title = file_title.split('.')[0]
    file_path = '/'.join(file_path_as_list)
    file_path = Path(f"{file_path}/{file_title}/drive_cols")
    # file_path_drive = Path(f"../../Schools/out_data_{job_id}/drive_cols")
    file_path.mkdir(parents=True, exist_ok=True)

    #saving
    np.savez(f"{file_path}/drive_col_{task_id}", dists_drive = dists_drive, time_drive = time_drive)


# In[8]:

#computes all matrices for full sample set
comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1])

print('COMPLETE')

# In[ ]:




