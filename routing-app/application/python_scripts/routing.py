'''
Script for routing
'''
import warnings
import math

## for simple routing
import osmnx as ox  #1.2.2
import networkx as nx  #3.0

## for data
import pandas as pd  #1.1.5
from time import time
from haversine import haversine

warnings.filterwarnings("ignore")


def middle(start, end):
    '''
    Return the middle point between two points.
    '''
    return [(start[0]+end[0])/2, (start[1]+end[1])/2]

def size_window(start, end):
    '''
    Return the size of the window to get the graph.
    '''
    height_lat = haversine(start, (start[0], end[1]), "m")
    width_lon = haversine(start, (end[0], start[1]), "m")
    return max(height_lat, width_lon) + 500

def get_full_route(G, path_length):
    '''
    Return the list of coordinates of the route.
    '''
    # Get the edges of the route
    edges = ox.graph_to_gdfs(G, nodes=False, edges=True)
    # Get the coordinates of the route and the length
    coordinates = []
    length = 0
    estimated_time = 0
    for i in range(len(path_length)-1):
        edge = edges.loc[path_length[i], path_length[i+1]]
        list_edge_coords = list(edge["geometry"].apply(lambda row: list(row.coords)))[0][:-1]
        coordinates.extend(list_edge_coords)
        length += edge["length"]

        # Convert the edge to calculate the time (weight)
        edge_for_weight = [{key: value[0] for key, value in edge.to_dict().items()}]
        estimated_time += custom_weight(path_length[i], path_length[i+1], edge_for_weight)

    # Add the last point
    coordinates.append(list(edge["geometry"].apply(lambda row: list(row.coords)))[0][-1])
    
    # Get the names of the streets
    start_street = edges.loc[path_length[0], path_length[1]]["name"][0]
    end_street = edges.loc[path_length[-2], path_length[-1]]["name"][0]
    # Check if the street is not nan
    if isinstance(start_street, float) and math.isnan(start_street):
        start_street = "Rue inconnue"
    if isinstance(end_street, float) and math.isnan(end_street):
        end_street = "Rue inconnue"

    # Check if the estimated time is infinity
    if math.isinf(estimated_time):
        estimated_time = -1

    return coordinates, int(length), start_street, end_street, estimated_time

def custom_weight(u, v, data):
    '''
    Return the weight of the edge.
    '''
    if data[0]["highway"] in ["busway", "motorway", "trunk",
                              "motorway_link", "trunk_link"]:
        return float('inf')

    return data[0]["length"] / (min(data[0]["speed_kph"], 15) / 3.6)


def get_routing(start, end):
    '''
    Handle the routing.
    '''
    dbt = time()
    print(size_window(start, end))
    G = ox.graph_from_point(middle(start, end), dist=size_window(start, end), network_type="bike", simplify=False)  #'drive', 'bike', 'walk'
    dbt, delay = time(), time()-dbt
    print("Temps de récupération du graphe : ", delay)
    G = ox.add_edge_speeds(G)
    dbt, delay = time(), time()-dbt
    print("Temps d'ajout des vitesses : ", delay)

    # find the nearest node to the start/end location
    start_node = ox.distance.nearest_nodes(G, start[1], start[0])
    end_node = ox.distance.nearest_nodes(G, end[1], end[0])
    dbt, delay = time(), time()-dbt
    print("Temps de recherche des noeuds les plus proches : ", delay)

    path_length = nx.shortest_path(G, source=start_node, target=end_node, method='dijkstra', weight=custom_weight)
    dbt, delay = time(), time()-dbt
    print("Temps de calcul du chemin : ", delay)

    coordinates, length, start_street, end_street, estimated_time = get_full_route(G, path_length)
    dbt, delay = time(), time()-dbt
    print("Temps de récupération du chemin complet : ", delay)
    
    return {"coordinates":coordinates,
            "length":length,
            "start_street":start_street,
            "end_street": end_street,
            "estimated_time": estimated_time}