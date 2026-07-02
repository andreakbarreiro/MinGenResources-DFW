#!/usr/bin/env python
# coding: utf-8

#THIS RUNS AS A NORMAL, NON-ARRAY JOB FOR THE SCHOOLS DATA 

# In[1]:
print('ughhhhhh I hate slurm')

import geopandas as gpd
import pandas as pd
import numpy as np
import geopy.distance
from shapely.geometry import Point, LineString, Polygon
from shapely.geometry import MultiPoint
import networkx as nx
import osmnx as ox
import osmnx.routing as routing
print('packages loaded yay')


# In[2]:


# loading in files
# datadir = "../Data"
#this should accurately grab the voucher_school file given Rae's file setup on 7/2
sites_with_dup = gpd.read_file("in_data/voucher_schools.geojson")
sites = sites_with_dup.drop_duplicates('Address')
sites.reset_index(inplace = True)
print("Voucher columns:", sites.columns)
print('data loaded yay')


# In[3]:


# define functions for geodesic

# compute geodesic distance between two given points a and b
def get_dist(a, b):
    origin = str(a.y)+','+str(a.x)
    destination = str(b.y)+','+str(b.x)
    dist = geopy.distance.geodesic(origin, destination)
    return dist.meters

print('get dist yay')

# compute geodesic distance (in meters) between every pair in a set of points
def comp_geod_dist_mat(sites):
    dists = np.zeros((len(sites), len(sites)))
    print(len(sites))
    for i, a in sites.iterrows():
        if i % 5 == 0: 
            print(f"geodesic -- i = {i}")
        for j, b in sites.iterrows():
            if i != j:
                dists[i,j] = get_dist(a.geometry,b.geometry)
    return dists

# converts units of a distance matrix from meters to walking time using an average walk speed 
def sec_from_mtr(dists_mtr):
    walk_speed = 1.42 # meters/sec
    dists_sec = dists_mtr / walk_speed
    dists_min = dists_sec
    return dists_min


# In[4]:


# define functions for walk

# load in open street maps
def load_map(network_type, 
             city = "Dallas County",
             use_bbox = False,
             bbox = [-97.1, 32.5, -96.45, 33.1]):
    # use default bbox to include the southern piece of collin county, if desired
    if use_bbox:
        G = ox.graph_from_bbox(bbox, network_type = network_type, simplify = False)
    else: 
        place = city
        G = ox.graph_from_place(place, network_type = network_type, simplify = False)
    return G

def build_pairs_list(nodes, dist_is_symmetric):
    pairs_list = []
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            pairs_list.append((i,j))

        if not dist_is_symmetric:
            for j in range(0,i):
                pairs_list.append((i,j))
    return pairs_list


def comp_walk_dist_mat(nodes, G, dist_is_symmetric):
    # list pairs of indices for distance computation
    # allows individual computations to be farmed out in arbitrary order if parallel processing
    pairs_list = build_pairs_list(nodes, dist_is_symmetric)

    # base matrix for distance calculations
    dists = np.zeros((len(nodes), len(nodes)))

    # compute shortest path length between each node
    # put dist(a,b) as entry (a,b) in distances matrix
    # if dist(a,b) = dist(b,a) then put dist(a,b) as entry in distances matrix

    for p1, p2 in pairs_list:
        if p2 == p1 + 1: 
            print(f"walk -- {p1}, {p2}")
        d = nx.shortest_path_length(G, nodes[p1], nodes[p2], weight='length')
        dists[p1, p2] = d

        if dist_is_symmetric:
            dists[p2, p1] = d

    return dists


# In[5]:


# define functions for drive

# calculates the shortest travel time between two given points
def comp_drive_path(p1, p2, nodes, G):
    print("Is empty:", nx.is_empty(G))
    print("Num nodes:", G.number_of_nodes())
    print(nodes[p1])
    print(nodes[p2])
    
    
    path = routing.shortest_path(G, nodes[p1], nodes[p2], weight = "travel_time")
    gdf_edges = routing.route_to_gdf(G, path, weight = "travel_time")
    return gdf_edges

# computes drive time for a given path
def comp_drive_time(gdf_edges):
    return gdf_edges["travel_time"].sum()

# ccomputes distance of a given path
def comp_drive_dist(gdf_edges):
    return gdf_edges["length"].sum()

# computes matrix of driving times between points
def comp_drive_time_mat(nodes, G, dist_is_symmetric):
    # list pairs of indices for distance computation
    # allows individual computations to be farmed out in arbitrary order if parallel processing
    pairs_list = build_pairs_list(nodes, dist_is_symmetric)

    # base matrix for distance calculations
    dists = np.zeros((len(nodes), len(nodes)))

    # add speed limit information to graph G
    G = routing.add_edge_speeds(G, agg = np.mean)
    G = routing.add_edge_travel_times(G)

    # compute shortest path length between each node
    # put dist(a,b) as entry (a,b) in distances matrix
    # if dist(a,b) = dist(b,a) then put dist(a,b) as entry in distances matrix
    for p1, p2 in pairs_list:
        if p2 == p1 + 1: 
            print(f"walk -- {p1}, {p2}")
        gdf_edges = comp_drive_path(p1, p2, nodes, G)
        d = comp_drive_time(gdf_edges)
        dists[p1, p2] = d

        if dist_is_symmetric:
            dists[p2, p1] = d

    return dists

# computes matrix of driving distances between points
def comp_drive_dist_mat(nodes, G, dist_is_symmetric):
    # list pairs of indices for distance computation
    # allows individual computations to be farmed out in arbitrary order if parallel processing
    pairs_list = build_pairs_list(nodes, dist_is_symmetric)

    # base matrix for distance calculations
    dists = np.zeros((len(nodes), len(nodes)))

    # add speed limit information to graph G
    G = routing.add_edge_speeds(G, agg = np.mean)
    G = routing.add_edge_travel_times(G)

    # compute shortest path length between each node
    # put dist(a,b) as entry (a,b) in distances matrix
    # if dist(a,b) = dist(b,a) then put dist(a,b) as entry in distances matrix
    for p1, p2 in pairs_list:
        if p2 == p1 + 1: 
            print(f"walk -- {p1}, {p2}")
            
        gdf_edges = comp_drive_path(p1, p2, nodes, G)
        d = comp_drive_dist(gdf_edges)
        dists[p1, p2] = d

        if dist_is_symmetric:
            dists[p2, p1] = d

    return dists


# In[6]:


# combined function to compute full matrix for a specific metric
def comp_mat(sites, 
             network_type = "walk", 
             city = "Dallas County",
             use_bbox = False, 
             dist_is_symmetric = False,
             bbox = [-97.1, 32.5, -96.45, 33.1]):

    # determins if given distance measure is symmetric
    if network_type == "geodesic" or network_type == "walk":
        dist_is_symmetric = True

    if network_type == "geodesic":
        dists_mtr = comp_geod_dist_mat(sites)
        dists = min_from_mtr(dists_mtr)

    elif network_type == "walk":
        # load street network
        # use bbox to include the southern piece of collin county, if desired
        G = load_map(network_type, city, use_bbox, bbox)

        # maps sites onto nearest nodes on street network
        nodes = ox.distance.nearest_nodes(G, sites["geometry"].x, sites["geometry"].y)

        # computes distance between all pairs of distinct sites
        dists_mtr = comp_walk_dist_mat(nodes, G, dist_is_symmetric)
        dists = min_from_mtr(dists_mtr)

    elif network_type == "drive":
        # load street network
        # use bbox to include the southern piece of collin county, if desired
        G = load_map(network_type, city, use_bbox, bbox)

        # maps sites onto nearest nodes on street network
        nodes = ox.distance.nearest_nodes(G, sites["geometry"].x, sites["geometry"].y)
        dists_sec = comp_drive_time_mat(nodes, G, dist_is_symmetric)
        dists = dists_sec / 60

    return dists


# In[7]:


# compute distance and time matrices for all geodesic, walk, and drive
# returns npz file with each matrix as a column


def comp_all_mats(sites, 
             city = "Dallas County",
             use_bbox = True, 
             dist_is_symmetric = False,
             bbox = [-97.1, 32.5, -96.45, 33.1]):

    # geodesic
    walk_speed = 1.42
    dists_geod = comp_geod_dist_mat(sites)
    time_geod = sec_from_mtr(dists_geod)
    print("finished geodesic matrix")

    np.savez("test_schools_geod", walk_speed = walk_speed, dists_geod = dists_geod, time_geod = time_geod)


    # walk
    G_walk = load_map(network_type = "walk", city = city, use_bbox = use_bbox, bbox = bbox)
    nodes_walk = ox.distance.nearest_nodes(G_walk, sites["geometry"].x, sites["geometry"].y)

    dists_walk = comp_walk_dist_mat(nodes_walk, G_walk, dist_is_symmetric)
    time_walk = sec_from_mtr(dists_walk)
    print("finished walk matrix")

    np.savez("test_schools_walk", walk_speed = walk_speed, dists_walk = dists_walk, time_walk = time_walk)

    try: 
        print('hello, driving')
        # drive
        G_drive = load_map(network_type = "drive", city = city, use_bbox = use_bbox, bbox = bbox)
        print('map loaded')
        nodes_drive = ox.distance.nearest_nodes(G_drive, sites["geometry"].x, sites["geometry"].y)
        print('nearest nodes')
        
        # list pairs of indices for distance computation
        # allows individual computations to be farmed out in arbitrary order if parallel processing
        pairs_list = build_pairs_list(nodes_drive, dist_is_symmetric)
        print('pairs_list yay')
    
        # base matrix for distance calculations
        dists_drive = np.zeros((len(nodes_drive), len(nodes_drive)))
        time_drive = np.zeros((len(nodes_drive), len(nodes_drive)))
        print('zeroes')
    
        # add speed limit information to graph G
        G_drive = routing.add_edge_speeds(G_drive, agg = np.mean)
        G_drive = routing.add_edge_travel_times(G_drive)
        print('speed limits')
    
        # compute shortest path length between each node
        # put dist(a,b) as entry (a,b) in distances matrix
        # if dist(a,b) = dist(b,a) then put dist(a,b) as entry in distances matrix
        for p1, p2 in pairs_list:
            if p2 == p1 + 1: 
                print(p1, p2)
            try: 
                gdf_edges = comp_drive_path(p1, p2, nodes_drive, G_drive)
            except Exception as e: 
                print("Error:", e)
                print("p1, p2", p1, p2)
                print("nodes drive is empty", nx.is_empty(nodes_drive))
                print("G drive is empty", nx.is_empty(G_drive))
                print("nodes drive num nodes", nodes_drive.number_of_nodes())
                print("G drive num nodes", G_drive.number_of_nodes())
            print('gdf_edges')
            d_dist = comp_drive_dist(gdf_edges)
            print('d_dist')
            d_time = comp_drive_time(gdf_edges)
            print('time')
            dists_drive[p1, p2] = d_dist
            time_drive[p1, p2] = d_time
    
            if dist_is_symmetric:
                dists_drive[p2, p1] = d_dist
                time_drive[p2, p1] = d_time
    
        print("finished drive matrix")

    except Exception as E: 
        print(f"Error: {E}")
    
    np.savez("test_schools_drive", dists_drive = dists_drive, time_drive = time_drive)


# In[8]:


#computes all matrices for full sample set
comp_all_mats(sites, 
             city = "Dallas County",
             use_bbox = False,
             dist_is_symmetric = False,
             bbox = [-97.1, 32.5, -96.45, 33.1])



# In[ ]:




