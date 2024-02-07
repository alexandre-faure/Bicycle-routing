'''
This module is used to calculate the elevation of a track.
'''

import json
import requests

def calculate_elevation_of_track(track:dict, n_coords:int=300) -> list:
    '''
    Get the elevation for each point of a track.
    INPUT:
        - track (dict) : dictionnary of a track.
        - n_coords (int) (default: 300) : number of coordinates per request.
    OUTPUT:
        - elevation (list) : list of the elevation for each point of the track.
    '''
    elevations = []
    lon_liste = [str(round(p["lon"],6)) for p in track.values()]
    lat_liste = [str(round(p["lat"],6)) for p in track.values()]

    for i in range(0, len(lon_liste), n_coords):
        lon = "|".join(lon_liste[i:i+n_coords])
        lat = "|".join(lat_liste[i:i+n_coords])

        ign_url = f"https://wxs.ign.fr/calcul/alti/rest/elevation.json?lon={lon}&lat={lat}&zonly=true"
        res = requests.get(ign_url, timeout=10)
        elevations.extend(json.loads(res.text)["elevations"])

    return elevations
    