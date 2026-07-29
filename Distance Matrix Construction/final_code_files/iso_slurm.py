#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# needed for geodesic matrix computation
import geopandas as gpd
import geopy.distance
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# needed for graphing over osm
# import contextily as ctx
# import gpd as geopandas  # safely using geopandas
from shapely.geometry import Point, MultiPoint, LineString, Polygon, MultiPolygon

# needed for minscaffold
import math
from random import random
import shapely
import pandas as pd

# needed for isocrones
import osmnx as ox
import osmnx.routing as routing
import random
import sys
import os
from pathlib import Path
import time
import pickle as pk

# import src
# import sys
sys.path.append('../../src') 
# import Driver
import Geometry
# import Scaffold


# In[ ]:


# # load in data
# sites = gpd.read_file("../Distance Matrix Construction/in_data/tefa_schools.geojson")
# print("read file")


job_id = os.environ.get("SLURM_ARRAY_JOB_ID")
print(f"Job ID: {job_id}")

#get task id from .sh file
task_id = int(sys.argv[3])
print(f"Running task {task_id}")

#take file name from .sh file
file_name = str(sys.argv[2])
print(f"File_name: {file_name}")

walk_or_drive = str(sys.argv[1])
print(f"Type: {walk_or_drive}")

#load in data
sites = gpd.read_file(file_name)
print('data loaded yay')

sites_task = pd.DataFrame(sites.iloc[task_id]).transpose().reset_index()

#turning the single row back into a gpd data frame
sites_task = gpd.GeoDataFrame(sites_task, 
                            geometry = "geometry", 
                            crs = 'EPSG:4326'
                           ).iloc[0]
print('created task site data')


# In[ ]:

# file_start = file_name.split("/")
# last_file_title = file_start[-1].split(".")[0]
# full_folder_path = f"{'/'.join(file_start[:-1])}/{last_file_title}"

# # load in previously saved matrices
# data = np.load(f"{full_folder_path}/drive_full.npz")
# print(f"{full_folder_path}/drive_full.npz")
# print("loaded matrix")

# # extract just the desired matrix
# W_orig = data["time"]

# # symmmetrize it
# W_mod = W_orig + np.transpose(W_orig)

# # convert seconds to minutes
# W_mod = W_mod / 60


# # In[ ]:


# def cut_off(W, dist_type):
#     if dist_type == "geod":
#         W = np.where(W < 180, np.round(W), 0)
#     elif dist_type == "walk":
#         W = np.where(W < 180, np.round(W), 0)
#     elif dist_type == "drive":
#         W = np.where(W < 15, np.round(W, 1), 0)
#     return W

# W = cut_off(W_mod, "walk")


# In[ ]:


# load in open street maps data with stored walking time information
def load_file(file):
    with open(file, "rb") as f:
        G = pk.load(f)
    return G

G = load_file(f"Dallas_bbox_{walk_or_drive}.pkl")
print("loaded bbox")

#do this earlier in the code!!
node = ox.distance.nearest_nodes(G, sites_task["geometry"].x, sites_task["geometry"].y)
# sites["nodes"] = nodes
print('grabbed node', type(node))

# In[ ]:


# compute minscaffold
# create list of filtration parameters
# eps_list = Geometry.genFullEpsList(W)
eps_list = [5, 10, 15, 20]
print('computed eps')

# In[ ]:


# for a given site and radius (time), computes the isocrone around the site with the given radius
# time measured in minutes
def calc_iso_poly(G, center_node, time, edge_att = "travel_time"):
    # returns a subgraph of G centered at the specified site with a given radius
    subgraph = nx.ego_graph(G, 
                            center_node, 
                            radius = time * 60, 
                            distance = edge_att)

    # extracts the nodes from the subgraph
    node_points = [Point((data["x"], data["y"])) 
                   for node, data in subgraph.nodes(data = True)]

    # turns the nodes into a polygon
    # returns the convex hull of that polygon (since convexity is a necessary assumtion for VR complex)
    polygon = Polygon(gpd.GeoSeries(node_points).union_all().convex_hull)

    return polygon

# computes isocrone for all sites and all filtration values

def iso_array_job(G, node, eps_list):
    poly_df = gpd.GeoDataFrame(data = [], columns = ['node', 'eps', 'geometry'])
    
    for time in eps_list: 
        poly = calc_iso_poly(G, node, time)
        new_row = gpd.GeoDataFrame(
                {'node': [node], 
                'eps':[time]}, geometry = [poly], 
                crs="EPSG:4326"
                )
        print('made new row', time)
    
        poly_df = pd.concat([poly_df, new_row], ignore_index=True)
    return poly_df

# def run_full_iso(G, sites, eps_list):
#     #calculate the nearest nodes for all points in the sites df

#     poly_df = gpd.GeoDataFrame(data = [], columns = ['node', 'eps', 'geometry'])

#     for node in nodes:    
#         print('working on node:',node)
#         for time in eps_list:
#             poly = calc_iso_poly(G, node, time)

#             new_row = gpd.GeoDataFrame(
#             {'node': [node], 
#             'eps':[time]}, geometry = [poly], 
#             crs="EPSG:4326"
#             )

#             poly_df = pd.concat([poly_df, new_row], ignore_index=True)
#     return poly_df


# In[ ]:


poly_df = iso_array_job(G, node, eps_list[1:])

file_path_as_list = file_name.split('/')[:-1]
file_title = file_name.split('/')[-1]
file_title = file_title.split('.')[0]
file_path = '/'.join(file_path_as_list)
file_path = Path(f"{file_path}/{file_title}/isochrones_{walk_or_drive}")
print('file_path', file_path)
# file_path_drive = Path(f"../../Schools/out_data_{job_id}/drive_cols")
file_path.mkdir(parents=True, exist_ok=True)

poly_df.to_file(f"{file_path}/node{task_id}.geojson", driver = "GEOJSON")

