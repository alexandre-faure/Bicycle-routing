import numpy as np
import json
import pandas as pd


def cartesien(lon: float, lat: float, R: int = 6371e3) -> np.ndarray:
    """Conversion to Cartesian coordinates

    Args:
        lon (float): longitude
        lat (float): latitude
        R (int, optional): Radius of the earth (in m). Defaults to 6371e3.

    Returns:
        np.ndarray: the coordinates of the point in Cartesian coordinates (x, y, z)
    """

    theta = lat * np.pi / 180
    phi = lon * np.pi / 180

    return np.array([R * np.cos(theta) * np.cos(phi), R * np.cos(theta) * np.sin(phi), R * np.sin(theta)])

def thomas(t:dict) -> dict:
    """_summary_

    Args:
        t (dict): fichier JSON d'une trace extrait

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: dictionnaire avec les différentes donnéées de la trace
    """
    speed = []
    distance = []
    distance_cumulée = []
    altitude = []
    diff_alt = []
    liste = []
    list_of_lat = []
    list_of_lon = []
    slope = []
    x1 = [0,0]
    for track in t.values():

        lat, lon = track['lat'], track['lon']
        list_of_lat.append(lat), list_of_lon.append(lon)
        x2 = cartesien(lat=lat, lon=lon)
        a=[(x2[0]-x1[0]),(x2[1]-x1[1])]
        distance.append(a)
        x1 = x2
        d = []
        lat_, lon_ = track['lat'], track['lon']
        d.append(lat_)
        d.append(lon_)
        liste.append(d)
        speed_ = track['speed']
        speed.append(speed_)
        altitude_ = track['alt']
        altitude.append(altitude_)
        diff_alt_ = track['delta_alt']
        diff_alt.append(diff_alt_)
        distance_cumulée_ = track['d_parcourue']
        distance_cumulée.append(distance_cumulée_)
        slope_= track['slope']
        slope.append(slope_)
                

    values = {}
    values['speed'] = np.array(speed)
    values['d_cumulée'] = np.array(distance_cumulée)
    values['altitude'] = np.array(altitude)
    values['diff_alt'] = np.array(diff_alt)
    values['liste'] = np.array(liste)
    values['distance'] = np.array(distance)
    values['slope'] = np.array(slope)

    return values

    

track_ref = 'data/JSON/originals_mm_full_truncated/02_juil._08h06_-_08h23_0.json'
with open(file=track_ref) as f:
    data = json.load(f)


#vitesse du cycliste en chaque point en m/s
VR_= thomas(t=data)['speed']

#Altitude de chaque point en mètre
Altitude_ = thomas(t=data)['altitude']

#Distance cumulée parcourue en m
D_cumulée_ = thomas(t=data)['d_cumulée']

#Liste des coordonées [lat,lon] de tous les points
Liste_ = thomas(t=data)['liste']

#couple de changement de coordonées en x et en y d'un point à l'autre en m
Distance_2 = thomas(t=data)['distance']

#Pente à chaque point en 
Slope = thomas(t=data)['slope']

