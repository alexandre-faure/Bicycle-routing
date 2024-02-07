import json
import re
from statistics import median
import folium
import os

def draw_map_from_json(json_files:list, output_file_path:str, map_name:str = "map_test") -> None:
    """_summary_

    Args:
        json_files (list): _description_
        output_file_path (str): _description_
        map_name (str, optional): _description_. Defaults to "map_test".
    """
    tracks = []
    colors = lambda x: ("originals" in x)*"blue"+("map-matched-GH" in x)*"red" + ("map-matched-OSRM" in x)*"green"

    # Add all tracks
    for filename in json_files:
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
        # Track name
        track_name = ("originals" in filename)*"Originals: " + ("map-matched-GH" in filename)*"Map-matched with GH: " + ("map-matched-OSRM" in filename)*"Map-matched with OSRM: "
        track_name += re.findall("\/([^\/]*)\.[^\/\.]*$", filename)[0]

        # Extract the dots
        latitudes = []
        longitudes = []
        for track in data.values():
            for seg in track.values():
                for point in seg.values():
                    latitudes.append(point["lat"])
                    longitudes.append(point["lon"])

        # Add the line containing all dots
        tracks.append(
            folium.PolyLine(
                locations = list(zip(latitudes, longitudes)),
                popup = folium.Popup(track_name),
                color = colors(filename)
                )
            )
    
    # Create the map
    lat_med = median([median([point[0] for point in track.locations]) for track in tracks])
    long_med = median([median([point[1] for point in track.locations]) for track in tracks])

    map = folium.Map(location=[lat_med, long_med], zoom_start=13.5)

    for track in tracks:
        track.add_to(map)

    # Save the map
    map.save(output_file_path + map_name + '.html')

def draw_all_files_from_folder(folder_path:str, output_file_path:str, map_name:str) -> None:
    """_summary_

    Args:
        folder_path (str): _description_
        output_file_path (str): _description_
        map_name (str): _description_
    """
    files = [] 
    for filename in os.listdir(path=folder_path):
        if filename.endswith('json'):
            files.append(folder_path + filename)
    
    draw_map_from_json(json_files=files, output_file_path=output_file_path, map_name=map_name)

"""folder_path = 'extracted_data/JSON/map-matched-GH/'
output_file_path = 'images/'
map_name = 'map_matched_with_GH'
draw_all_files_from_folder(folder_path=folder_path, output_file_path=output_file_path, map_name=map_name)"""

def compare_files(filename:str, GH:bool, OSRM:bool, original:bool = True) -> None:
    """_summary_

    Args:
        filename (str): _description_
        GH (bool): _description_
        OSRM (bool): _description_
        original (bool, optional): _description_. Defaults to True.
    """
    GH = f'extracted_data/JSON/map-matched-GH/{filename}'
    OSRM = f'extracted_data/JSON/map-matched-OSRM/{filename}'
    original = f'extracted_data/JSON/originals/{filename}'
    files = [GH, OSRM, original]
    output_file_path = 'images/'
    draw_map_from_json(json_files=files, output_file_path=output_file_path, map_name=f'comparison_{filename[:-4]}')

"""compare_files(filename='01_déc._08h08_-_08h28.json', GH = True, OSRM = True)"""