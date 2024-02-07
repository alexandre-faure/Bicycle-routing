'''
This module is used to calculate the turns of a track.
'''

from geographiclib.geodesic import Geodesic

def calculate_azimuth_of_track(track:dict) -> list:
    '''
    This function is used to calculate the azimuth of a track.
    INPUT:
        - track (dict): track to process
    OUTPUT:
        - azimuth (list): azimuth of the track
    '''
    azimuth = []

    for i in range(1, len(track)):
        azimuth.append(Geodesic.WGS84.Inverse(track[f"point{i - 1}"]["lat"],
                                              track[f"point{i - 1}"]["lon"],
                                              track[f"point{i}"]["lat"],
                                              track[f"point{i}"]["lon"])["azi1"])

    # Add the first azimuth
    azimuth.insert(0, azimuth[0])

    # Reduce the number of decimals
    azimuth = [round(x, 1) for x in azimuth]

    return azimuth