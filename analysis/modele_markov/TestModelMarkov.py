import numpy as np
from useful_fcts import date, latlon_to_xyz
import pandas as pd
import json
import pandas as pd
import rasterio

# tableau numpy de coordonnées latitude / longitude

# 37_03 : Latitude 0N - 5N et Longitude 45E - 50E
# 36_03 : Latitude 5S - 0N et Longitude 45E - 50E


def thomas(t: dict) -> dict:
    """_summary_

    Args:
        t (dict): _description_

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: _description_
    """
    list_of_lat, list_of_lon = [], []
    speed = []
    distance = []
    t1, x1 = None, None
    for track in t.values():
        for seg in track.values():
            for point in seg.values():
                t2 = date(time=point['time'])
                lat, lon = point['lat'], point['lon']
                list_of_lat.append(lat), list_of_lon.append(lon)
                x2 = latlon_to_xyz(latitude=lat, longitude=lon)
                if t1 != None:
                    dx = np.linalg.norm(x2 - x1)
                    dt = (t2 - t1).total_seconds()
                    if dt == 0:
                        speed.append(None)
                    else:
                        v = dx / dt
                        speed.append(v)
                    distance.append(dx)
                t1, x1 = t2, x2

    alt = []
    path36 = 'srtm_37_03.tif'

    with rasterio.open(path36) as src:
        # création d'une liste pour stocker les altitudes
        elevations = []

        # boucle sur les coordonnées
        for i in range(len(list_of_lat)):
            # conversion des coordonnées en coordonnées de pixels
            row, col = src.index(list_of_lon[i], list_of_lat[i])

            # lecture de l'altitude à partir du pixel correspondant
            elevation = src.read(1, window=((row, row+1), (col, col+1)))

            # ajouter l'altitude à la liste
            elevations.append(elevation[0][0])

    slope = []
    for i in range(len(list_of_lat) - 1):
        alt1 = elevations[i]
        alt2 = elevations[i + 1]
        dist = distance[i]
        if dist == 0:
            slope.append(0)
        else:
            slope.append((alt2 - alt1) / dist)

    values = {}
    values['speed'] = np.array(speed)
    values['distance'] = np.array(distance)
    values['slope'] = np.array(slope)
    values['elevation'] = np.array(elevations)

    return values


track_ref = 'extracted_data/JSON/originals/02_juil._08h06_-_08h23.json'
with open(file=track_ref) as f:
    data = json.load(f)

print(thomas(t=data))
