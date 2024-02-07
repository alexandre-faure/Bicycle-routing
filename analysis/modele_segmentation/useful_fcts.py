import numpy as np
from datetime import datetime
import folium
import json
import re
from statistics import median


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
