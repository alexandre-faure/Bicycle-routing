"""
This module contains functions to clean the JSON files by cuting, removing or filtering the data.
"""

from datetime import datetime
from haversine import haversine, Unit

def check_track_quality(data:dict, min_points:int=10, min_distance:int=10) -> bool:
    '''
    Return True if the track satisfies the conditions (long enough and minimum crossed distance),
    False otherwise.
    INPUT:
        - data (dict) : dictionnary of the track to check.
        - min_points (int) (default: 10) : minimum number of points in a track.
        - min_distance (int) (default: 10) : minimum total distance in meters of a track.
    OUTPUT:
        - (bool) : True if the track satisfies the conditions, False otherwise.
    '''
    # Check if the track is long enough
    if len({(p["lat"], p["lon"]) for p in data.values()}) < min_points:
        return False
    
    # Check if the track crosses enough distance
    if haversine((data["point0"]["lon"], data["point0"]["lat"]),
                    (data[f"point{len(data)-1}"]["lon"], data[f"point{len(data)-1}"]["lat"]),
                    Unit.METERS) < min_distance:
        return False
    
    return True


def clean_data(json_files:dict, max_delay:int=10, min_points:int=10, min_distance:int=10) -> dict:
    '''
    Truncates the tracks of the JSON files in order to have tracks without too long delays
    and only keep tracks with a minimum number of unique points, a minimum total distance
    and a minimum unique distance.
    INPUT:
        - json_files (dict) : dictionary of the JSON files to clean.
        - dest_folder (str) (default: "extracted_data/JSON/originals_mm_full_truncated") : path to the destination folder to save the JSON files
        - max_delay (int) (default: 10) : maximum delay in second between two points
        - min_points (int) (default: 10) : minimum number of points in a track
        - min_distance (int) (default: 10) : minimum total distance in meters of a track
    OUTPUT:
        - final_json_files (dict) : dictionary of the cleaned JSON files.
    '''
    final_json_files = {}
    # For each track
    for filename, data in json_files.items():
        file_content = {}
        track_number, point_number = 0, 0
        previous_date = None
        for point in data.values():
            # Check if the delay between two points is not too long
            if previous_date is not None and (datetime.fromisoformat(point["time"]) - previous_date).total_seconds() > max_delay:
                # If the constituted file satisfies the conditions, we save it
                if check_track_quality(file_content, min_points, min_distance):
                    final_json_files[f"{filename}_{track_number}"] = file_content
                    track_number += 1
                # We reinitialize for the next file
                file_content = {}
                point_number = 0
            # We add the point to the file
            value = {
                "lat" : point["lat"],
                "lon" : point["lon"],
                "time" : point["time"]
            }
            file_content[f"point{point_number}"] = value
            point_number += 1
            previous_date = datetime.fromisoformat(point["time"])
            
        # We check if the last file satisfies the conditions
        if check_track_quality(file_content, min_points, min_distance):
            final_json_files[f"{filename}_{track_number}"] = file_content
        
    return final_json_files
