import numpy as np
from datetime import datetime
import folium
import json
import re
from statistics import median
import os
from json_processing import open_json


def date(time: str, format: str = '%Y-%m-%dT%H:%M:%S.%f%z') -> datetime:
    """Converts the string into a datetime object

    Args:
        time (str): The date given by the GPS
        format (_type_, optional): _description_. Defaults to '%Y-%m-%dT%H:%M:%S.%f%z'.

    Returns:
        datetime: the date of the point
    """

    if len(time) == 25:
        # The string contains milliseconds
        format = '%Y-%m-%dT%H:%M:%S%z'

    date_obj = datetime.strptime(time, format)

    return date_obj


def draw_map_from_json(json_files: list, map_name: str = "map_test") -> None:
    '''
    Create a map (htlm file) with the tracks extracted from gpx files on folium

    Input :
        - json_files (list) : list of the path to the several json files
        - map_name (str) : name of the html file to create (containing the map) without ".html"

    Output :
        - None
    '''
    tracks = []

    def colors(x):
        if ('2_juil._08h06_-_08h23.json' in x):
            return 'blue'

        return ("originals" in x)*"red"+("map-matched" in x)*"blue"

    # Add all tracks
    for filename in json_files:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)

        # Track name
        track_name = ("originals" in filename)*"Originals: " + \
            ("map-matched" in filename)*"Map-matched: "
        track_name += re.findall("\/([^\/]*)\.[^\/\.]*$", filename)[0]

        # Extract the dots
        latitudes = []
        longitudes = []
        for point in data.values():
            latitudes.append(point["lat"])
            longitudes.append(point["lon"])

        # Add the line containing all dots
        tracks.append(
            folium.PolyLine(
                locations=list(zip(latitudes, longitudes)),
                popup=folium.Popup(track_name),
                color=colors(filename)
            )
        )

    # Create the map
    lat_med = median([median([point[0] for point in track.locations])
                     for track in tracks])
    long_med = median(
        [median([point[1] for point in track.locations]) for track in tracks])

    map = folium.Map(location=[lat_med, long_med], zoom_start=13.5)

    for track in tracks:
        track.add_to(map)

    # Save the map
    map.save(f'extracted_data/maps/{map_name}.html')


def latlon_to_xyz(latitude: float, longitude: float) -> np.ndarray:
    """Convertit les coordonnées de latitude/longitude en coordonnées cartésiennes x, y, z

    Args:
        latitude (float): Latitude en degrés
        longitude (float): Longitude en degrés

    Returns:
        np.ndarray: Coordonnées cartésiennes x, y, z
    """
    # Rayon de la Terre en mètres
    R = 6371e3

    # Convertit les coordonnées de latitude / longitude en radians
    lat_rad = np.radians(latitude)
    lon_rad = np.radians(longitude)

    # Calcule les coordonnées cartésiennes x, y, z en utilisant une formule de projection
    x = R * np.cos(lat_rad) * np.cos(lon_rad)
    y = R * np.cos(lat_rad) * np.sin(lon_rad)
    z = R * np.sin(lat_rad)

    return np.array([x, y, z])


def list_json_to_dict(filename):
    '''read a json file from its path and convert it into a dictionnary

    Input :
        - filename(str): path towards the json file

    Output :
        - track (dict)
    '''
    dico = {}
    for file in filename:
        with open(file, 'r') as json_file:
            data = json.load(json_file)

        # Track name
        track_name = ("originals" in file)*"Originals: " + \
            ("map-matched" in file)*"Map-matched: "
        track_name += re.findall("\/([^\/]*)\.[^\/\.]*$", file)[0]

        dico[track_name] = data
    return dico


def draw_map_from_dict(dict_files: list, map_name: str = "map_test", points_seg: list = None, points: list = None) -> None:
    '''
    Create a map (htlm file) with the tracks extracted from gpx files on folium

    Input :
        - json_files (list) : list of the path to the several json files
        - map_name (str) : name of the html file to create (containing the map) without ".html"

    Output :
        - None
    '''
    tracks = []

    def colors(x):
        if 'originals_filtered_mm_full' in x:
            return 'red'
        return 'blue'

    # Add all tracks
    for track_name in dict_files.keys():
        data = dict_files[track_name]

        # Extract the dots
        latitudes = []
        longitudes = []

        for point in data.values():
            latitudes.append(point["lat"])
            longitudes.append(point["lon"])

        # Add the line containing all dots

        tracks.append(
            folium.PolyLine(
                locations=list(zip(latitudes, longitudes)),
                color=colors(track_name), popup=folium.Popup(track_name)
            )
        )

    # Create the map
    lat_med = median([median([point[0] for point in track.locations])
                     for track in tracks])
    long_med = median(
        [median([point[1] for point in track.locations]) for track in tracks])

    map = folium.Map(location=[lat_med, long_med], zoom_start=13.5)
    if points_seg is not None:
        for point in points_seg:
            for k in range(3):
                folium.Marker(location=[point['pB'][k+1][0], point['pB'][k+1][1]],
                              tooltip='pB', icon=folium.Icon(color='blue')).add_to(map)
                folium.Marker(location=[point['pF'][k+1][0], point['pF'][k+1][1]],
                              tooltip='pF', icon=folium.Icon(color='green')).add_to(map)
            folium.Marker(location=[point['pC'][0], point['pC'][1]],
                          tooltip='pC', icon=folium.Icon(color='black')).add_to(map)
            folium.Marker(location=[point['pB'][0][0], point['pB'][0][1]],
                          tooltip='pB', icon=folium.Icon(color='darkblue')).add_to(map)
            folium.Marker(location=[point['pF'][0][0], point['pF'][0][1]],
                          tooltip='pF', icon=folium.Icon(color='darkgreen')).add_to(map)

    if points is not None:
        for point in points:
            for key, value in point.items():
                folium.Marker(location=[value['lat'], value['lon']],
                              tooltip=key, icon=folium.Icon(color='blue')).add_to(map)
    for track in tracks:
        track.add_to(map)

    # Save the map
    map.save(f'extracted_data/maps/{map_name}.html')


'''
tracks = os.listdir(os.getcwd()+'/extracted_data/JSON/originals')
for i in range(len(tracks)):
    tracks[i] = os.getcwd()+'/extracted_data/JSON/originals/'+tracks[i]

tracks.append(
    os.getcwd()+'/extracted_data/JSON/originals/02_juil._08h06_-_08h23.json')

draw_map_from_json(tracks, map_name='treck_ref_total')  '''
