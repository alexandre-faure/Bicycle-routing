import numpy as np
from datetime import datetime


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
