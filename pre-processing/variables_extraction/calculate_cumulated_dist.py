'''
This module is used to calculate the cumulated distances of a track.
'''

import numpy as np
from haversine import haversine

def calculate_cumulated_dist(track:dict) -> list:
    '''
    This function is used to calculate the cumulated distances of a track.
    INPUT:
        - track (dict): track to process
    OUTPUT:
        - cumulated_dist (list): cumulated distances of the track
    '''
    cumulated_dist = np.zeros(len(track))

    for i in range(1, len(track)):
        cumulated_dist[i] = cumulated_dist[i - 1] +\
            haversine((track[f"point{i-1}"]["lat"], track[f"point{i-1}"]["lon"]),
                      (track[f"point{i}"]["lat"], track[f"point{i}"]["lon"]),
                       "m")

    # Reduce the precision of the cumulated distances
    cumulated_dist = [round(d, 2) for d in cumulated_dist]

    return cumulated_dist