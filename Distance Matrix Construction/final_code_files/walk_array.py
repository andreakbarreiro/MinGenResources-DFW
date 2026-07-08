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
    origin = (a.y, a.x)
    #str(a.y)+','+str(a.x)
    destination = (b.y, a.y)
    #str(b.y)+','+str(b.x)
    dist = geopy.distance.geodesic(origin, destination)
    return dist.meters

print('get dist yay')

# compute geodesic distance (in meters) between the task site and all other sites in the data frame
#check data frame syntax
def comp_geod_dist_col(col):
    dists = np.zeros(len(sites))
    for i, dest in sites.iterrows():
        dists[i] = get_dist(col.geometry,dest.geometry)
    return dists

# converts units of a distance matrix from meters to walking time using an average walk speed 
def sec_from_mtr(dists_mtr):
    walk_speed = 1.42 # meters/sec
    dists_sec = dists_mtr / walk_speed
    dists_min = dists_sec
    return dists_min
    
#GEODESIC MODIFIED FOR ARRAY JOB

# In[4]:

# define functions for walk
# load in open street maps
# def load_map(network_type, 
#              city = "Dallas County",
#              use_bbox = True,
#              bbox = [-97.1, 32.5, -96.45, 33.1]):
#     # use default bbox to include the southern piece of collin county, if desired
#     if use_bbox:
#         G = ox.graph_from_bbox(bbox, network_type = network_type, simplify = False)
#     else: 
#         place = city
#         G = ox.graph_from_place(place, network_type = network_type, simplify = False)
        
#     #now map each site location to the nearest node (aka street) 
#     nodes = ox.distance.nearest_nodes(G, sites["geometry"].x, sites["geometry"].y)
#     return nodes, G

def load_map(mapp):
    #mapp is the filepath to the multidi graph
    # G = nx.read_gpickle(mapp)
    with open(mapp, 'rb') as f:
        G = pickle.load(f)
    nodes = ox.distance.nearest_nodes(G, sites["geometry"].x, sites["geometry"].y)
    return nodes, G

def comp_walk_dist_col(nodes, G):
    # list pairs of indices for distance computation
    # allows individual computations to be farmed out in arbitrary order if parallel processing
    # pairs_list = list(range(len(sites)))

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

    #MODIFIED WALK TO USE IN ARRAY JOB
# In[5]:


# define functions for drive

# calculates the shortest travel time between two given points
def comp_drive_path(p, nodes, G):
    path = routing.shortest_path(G, nodes[task_id], nodes[p], weight = "travel_time")
    gdf_edges = routing.route_to_gdf(G, path, weight = "travel_time")
    
    return gdf_edges

# computes drive time for a given path
def comp_drive_time(gdf_edges):
    return gdf_edges["travel_time"].sum()

# ccomputes distance of a given path
def comp_drive_dist(gdf_edges):
    return gdf_edges["length"].sum()

# computes matrix of driving times between points
def comp_all_drive_col(nodes, G):
    # list pairs of indices for distance computation
    # allows individual computations to be farmed out in arbitrary order if parallel processing
    pairs_list = range(len(sites))

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
    for p in pairs_list:
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

#MODIFIED FOR ARRAY JOB


# In[6]:

def comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1]):

    # # geodesic
    # #walk_speed = 1.42
    # dists_geod = comp_geod_dist_col(sites_task)
    # time_geod = sec_from_mtr(dists_geod)
    # print("finished geodesic matrix")

    # file_path_geod = Path(f"../../Schools/out_data_{job_id}/geod_cols")
    # file_path_geod.mkdir(parents=True, exist_ok=True)
    
    # np.savez(f"{file_path_geod}/geod_col_{task_id}", walk_speed = walk_speed, dists_geod = dists_geod, time_geod = time_geod)


    # walk
    nodes_walk, G_walk = load_map("../Dallas_bbox_walk.pkl")
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

    # try: 
    #     print('started driving calculations')
    #     # drive
    #     nodes_drive, G_drive = load_map("../Dallas_bbox_drive.pkl")
    #     print('drive: map + nodes loaded')
        
    #     dists_drive, time_drive = comp_all_drive_col(nodes_drive, G_drive)
        
    #     print("finished drive matrix")

    # except Exception as E: 
    #     print(f"Error: {E}")

    # file_path_drive = Path(f"../../Schools/out_data_{job_id}/drive_cols")
    # file_path_drive.mkdir(parents=True, exist_ok=True)
    
    # np.savez(f"{file_path_drive}/drive_col_{task_id}", dists_drive = dists_drive, time_drive = time_drive)


# In[8]:


#computes all matrices for full sample set
comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1])

print('COMPLETE')

# In[ ]:




