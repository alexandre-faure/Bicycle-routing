'''
This module is used to calculate the turns of a track.
'''

from geographiclib.geodesic import Geodesic
import numpy as np

def calculate_turns_of_track(track:dict) -> list:
    '''
    This function is used to calculate the turns of a track with a simple 
    discrete derivation.
    INPUT:
        - track (dict): track to process
    OUTPUT:
        - turns (list): turns of the track
    '''
    turns = []

    for i in range(1, len(track)):
        turn = track[f"point{i}"]["azimuth"] - track[f"point{i - 1}"]["azimuth"]

        if abs(turn) > 180:
            turn = turn - np.sign(turn) * 360

        turns.append(turn)


    # Add the first turn
    turns.insert(0, turns[0])

    # Reduce the number of decimals
    turns = [round(x, 1) for x in turns]

    return turns
