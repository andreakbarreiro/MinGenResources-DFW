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
print('packages loaded')


# In[2]:


# loading in files
#replace the file path below with the file path for the data we want to run
#this should be correct to access the parks centroids
sites = gpd.read_file("../Parks/centroids.shp")
print("Parks columns:", sites.columns)
print('data loaded')

#assigning and printing task id
task_id = int(sys.argv[1])
print(f"Running task {task_id}")

#creating a data frame with only the row corresponding to the task_id
sites_task = pd.DataFrame(sites.iloc[task_id]).transpose()
print('created task site data')


# In[3]:


# define functions for geodesic

# compute geodesic distance between two given points a and b
#didn't change for array job
def get_dist(a, b):
    origin = str(a.y)+','+str(a.x)
    destination = str(b.y)+','+str(b.x)
    dist = geopy.distance.geodesic(origin, destination)
    return dist.meters

print('get dist yay')

# compute geodesic distance (in meters) between the task site and all other sites in the data frame
#check data frame syntax
def comp_geod_dist_col(col: pandas.core.frame.DataFrame):
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
def load_map(network_type, 
             city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1]):
    # use default bbox to include the southern piece of collin county, if desired
    if use_bbox:
        G = ox.graph_from_bbox(bbox, network_type = network_type, simplify = False)
    else: 
        place = city
        G = ox.graph_from_place(place, network_type = network_type, simplify = False)
        
    #now map each site location to the nearest node (aka street) 
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
        if nodes[task_id] == nodes[p]: 
            continue
        #is nodes[track_id] the same as the node associated with sites[track_id]??
        d = nx.shortest_path_length(G, nodes[task_id], nodes[p], weight='length')
        
        dists[p] = d
    return dists

    #MODIFIED WALK TO USE IN ARRAY JOB
# In[5]:


# define functions for drive

# calculates the shortest travel time between two given points
def comp_drive_path(p, nodes, G):
    # print("Is empty:", nx.is_empty(G))
    # print("Num nodes:", G.number_of_nodes())
    if nodes[task_id] == nodes[p]: 
            continue
    path = routing.shortest_path(G, nodes[task_id], nodes[p], weight = "travel_time")
    print(len(path))
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

    # compute shortest path length between each node
    # put dist(a,b) as entry (a,b) in distances matrix
    # if dist(a,b) = dist(b,a) then put dist(a,b) as entry in distances matrix
    for p in pairs_list:
   
        gdf_edges = comp_drive_path(p, nodes, G)
        
        d = comp_drive_dist(gdf_edges)
        t = comp_drive_time(gdf_edges)
    
        dists[p] = d
        times[p] = t
        
    return dists, times

#MODIFIED FOR ARRAY JOB


# In[6]:

def comp_all_mats(city = "Dallas County",
             use_bbox = True,
             bbox = [-97.1, 32.5, -96.45, 33.1]):

    # geodesic
    walk_speed = 1.42
    dists_geod = comp_geod_dist_col(sites_task)
    time_geod = sec_from_mtr(dists_geod)
    print("finished geodesic matrix")

    np.savez(f"geod_cols/geod_{task_id}", walk_speed = walk_speed, dists_geod = dists_geod, time_geod = time_geod)


    # walk
    nodes_walk, G_walk = = load_map(network_type = "walk", city = city, use_bbox = use_bbox, bbox = bbox)
    dists_walk = comp_walk_dist_mat(nodes_walk, G_walk)
    time_walk = sec_from_mtr(dists_walk)
    print("finished walk matrix")

    np.savez(f"walk_cols/walk_{task_id}", walk_speed = walk_speed, dists_walk = dists_walk, time_walk = time_walk)

    try: 
        print('started driving calculations')
        # drive
        nodes_drive, G_drive = load_map(network_type = "drive", city = city, use_bbox = use_bbox, bbox = bbox)
        print('map + nodes loaded')
        
        drive_dists, drive_times = comp_all_drive_col(nodes_drive, G_drive)
        
        print("finished drive matrix")

    except Exception as E: 
        print(f"Error: {E}")
    
    np.savez(f"drive_cols/drive_{task_id}", dists_drive = dists_drive, time_drive = time_drive)


# In[8]:


#computes all matrices for full sample set
comp_all_mats(city = "Dallas County",
             use_bbox = True
             bbox = [-97.1, 32.5, -96.45, 33.1])

print('COMPLETE')

# In[ ]:




