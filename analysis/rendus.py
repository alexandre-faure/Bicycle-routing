import folium
from json_processing import *
from map_creation import *
from useful_fcts import *
import re
from statistics import median
from useful_fcts import list_json_to_dict
from os import getcwd

############################### Illustration du map-matching ######################################
def generate_map_matching():
    tracks = []
    markers = []

    colors = ['green', 'orange', 'beige', 'lightgray', 'darkred', 'lightgreen', 'blue', 'gray', 'lightred', 'white', 'lightblue', 'cadetblue', 'purple', 'pink', 'darkgreen', 'darkblue', 'red', 'darkpurple', 'black']
    n_colors = len(colors)

    files_o = ["extracted_data/JSON/originals/12_juil._18h56_-_19h08.json"]
    files_mm = ["extracted_data/JSON/map-matched-full-GH/12_juil._18h56_-_19h08.json"]
    data_o = open_json(files_o)
    data_mm = open_json(files_mm)

    # Add all tracks
    for data_dict, title, color in [(data_o, "Trace initiale", "blue"), (data_mm, "Trace map-matchée", "red")]:
        for data in data_dict.values():
            # Track name
            track_name = f"{title} : le 2 juillet à 8h06"

            # Extract the dots
            latitudes = []
            longitudes = []
            for track in data.values():
                for seg in track.values():
                    for point in seg.values():
                        latitudes.append(point["lat"])
                        longitudes.append(point["lon"])

            coords = list(zip(latitudes, longitudes))

            # Add the line containing all dots
            tracks.append(
                folium.PolyLine(
                    locations = coords,
                    popup = folium.Popup(track_name),
                    color = color
                    )
                )

            k = 10
            for i in range(len(coords)):
                if i%k == 0:
                    markers.append(folium.Marker(coords[i], icon=folium.Icon(color=colors[i//k % n_colors])))
            
    
    # Create the map
    lat_med = median([median([point[0] for point in track.locations]) for track in tracks])
    long_med = median([median([point[1] for point in track.locations]) for track in tracks])

    new_map = folium.Map(location=[lat_med, long_med], zoom_start=20)

    for track in tracks:
        track.add_to(new_map)
    
    for marker in markers:
        marker.add_to(new_map)

    # Save the map
    new_map.save('extracted_data/maps/affichage_rendu_map-matching.html')

    return None






def type_color(data, track_name):

    return ("Originals" in track_name)*"green"+("Map-matched" in track_name)*"red"

def lat_color(data, track_name):
    latitudes = []
    for track in data.values():
        for seg in track.values():
            for point in seg.values():
                latitudes.append(point["lat"])
    return latitudes[1:]


def lon_color(data, track_name):
    longitudes = []
    for track in data.values():
        for seg in track.values():
            for point in seg.values():
                longitudes.append(point["lon"])
    return longitudes[1:]


def alt_color(data, track_name):
    return [67,  67,  68,  67,  64,  64,  64,  64,  64,  64,  64,  64,
            64,  64,  64,  64,  64,  64,  64,  65,  65,  65,  65,  65,  65,
            65,  65,  67,  67,  67,  67,  67,  67,  67,  65,  65,  65,  65,
            65,  65,  65,  65,  65,  65,  65,  65,  65,  65,  65,  65,  65,
            65,  65,  65,  65,  65,  58,  55,  55,  55,  55,  55,  55,  62,
            62,  62,  62,  62,  62,  62,  62,  62,  62,  62,  62,  62,  62,
            62,  62,  61,  61,  61,  61,  61,  61,  61,  61,  61,  61,  63,
            63,  63,  63,  63,  63,  63,  63,  63,  63,  63,  63,  63,  63,
            71,  71,  71,  71,  71,  71,  71,  71,  71,  72,  72,  72,  72,
            72,  72,  72,  72,  72,  72,  72,  72,  71,  71,  71,  71,  71,
            71,  71,  71,  71,  71,  73,  73,  73,  73,  73,  73,  78,  78,
            78,  78,  78,  75,  75,  75,  75,  75,  75,  75,  75,  75,  75,
            75,  84,  84,  84,  84,  84,  82,  82,  82,  82,  82,  82,  82,
            82,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,
            79,  79,  79,  79,  79,  79,  79,  81,  81,  81,  81,  81,  81,
            81,  81,  80,  80,  80,  80,  80,  80,  80,  80,  79,  79,  79,
            79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  80,
            80,  80,  80,  80,  80,  80,  80,  80,  80,  80,  80,  80,  80,
            80,  80,  80,  80,  80,  80,  80,  82,  82,  82,  82,  82,  82,
            82,  82,  82,  82,  81,  81,  81,  81,  81,  81,  81,  81,  81,
            79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,  79,
            79,  79,  79,  79,  79,  79,  79,  79,  88,  88,  88,  88,  88,
            88,  88,  88,  88,  88,  88,  88,  88,  88,  88,  88,  89,  89,
            89,  89,  89,  89,  89,  89,  89,  88,  88,  88,  88,  88,  88,
            88,  88,  88,  88,  88,  88,  88,  88,  88,  88,  88,  88,  88,
            88,  88,  87,  87,  87,  87,  87,  87,  87,  87,  87,  87,  87,
            87,  87,  87,  87,  86,  86,  86,  86,  86,  86,  86,  86,  86,
            86,  84,  84,  84,  84,  84,  84,  84,  84,  84,  84,  83,  83,
            83,  83,  83,  83,  83,  83,  83,  83,  83,  91,  91,  91,  91,
            91,  91,  91,  91,  91,  91,  91,  88,  88,  88,  88,  88,  88,
            88,  88,  88,  88,  88,  84,  84,  84,  84,  84,  84,  84,  84,
            84,  84,  84,  84,  89,  89,  89,  89,  89,  89,  89,  89,  89,
            89,  89,  89,  89,  89,  89,  89,  89,  89,  89,  89,  89,  89,
            89,  89,  96,  96,  96,  96,  96,  96,  96,  96,  95,  95,  95,
            95,  95,  95,  95,  95,  95,  95,  91,  91,  91,  91,  91,  91,
            91, 100, 100, 100, 100, 100, 100, 100, 101, 101, 101, 101, 101,
            101, 101, 101, 111, 111, 111, 111, 111, 111, 111, 111, 111, 111,
            111, 111, 111, 111, 111, 111, 111, 111, 111, 111, 116, 116, 116,
            116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116, 116,
            116, 116, 116, 116, 116, 116, 116, 116, 121, 121, 121, 121, 121,
            121, 121, 121, 121, 121, 121, 121, 121, 121, 121, 121, 121, 121,
            121, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129,
            129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129, 129,
            129, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141,
            141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141, 141,
            151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151,
            151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151,
            151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151, 151,
            151, 151, 151, 151, 151, 151, 151, 151, 151, 153, 153, 153, 153,
            153, 153, 153, 153, 153, 153, 153, 153, 153, 153, 153, 153, 153,
            153, 153, 154, 154, 154, 154, 154, 154, 154, 154, 154, 154, 154,
            154, 154, 154, 154, 154, 154, 154, 154, 156, 156, 156, 156, 156,
            156, 156, 158, 158, 158, 158, 158, 158, 158, 158, 158, 158, 158,
            156, 156, 156, 156, 156, 156, 156, 156, 156, 156, 156, 156, 158,
            158, 158, 158, 158, 158, 158, 158, 158, 160, 160, 160, 160, 160,
            160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160, 160,
            160, 161, 161, 161, 161, 161, 161, 161, 161, 161, 164, 164, 164,
            164, 164, 164, 164, 164, 164, 164, 164, 164, 164, 164, 164, 164,
            164, 164, 164, 164, 157, 157, 160, 160, 160, 160, 160, 160, 160,
            160, 160, 160, 162, 162, 162, 162, 162, 162, 162, 162, 162, 166,
            166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 168, 168, 168,
            168, 168, 168, 168, 168, 168, 168, 167, 167, 167, 167, 167, 167,
            167, 167, 167, 167, 167, 167, 167, 167, 167, 167, 167, 167, 167,
            166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166, 166,
            166, 166, 166, 166, 166, 165, 165, 165, 165, 165, 165, 165, 165,
            165, 165, 165, 165, 165, 165, 165, 165, 165, 165, 165, 165, 165,
            165, 165, 165, 165, 165, 165, 165, 165, 165, 165, 165, 165, 165,
            165, 165, 165, 165, 165, 165, 165, 165, 165]


def draw_map_from_dict(dict_files: list, map_name: str = "map_test", color_fonction=type_color) -> None:
    '''
    Create a map (htlm file) with the tracks extracted from gpx files on folium

    Input :
        - json_files (list) : list of the path to the several json files
        - map_name (str) : name of the html file to create (containing the map) without ".html"
        - color_fonction : fonction giving the color between each points of the track

    Output :
        - None
    '''
    tracks = []

    # Add all tracks
    for track_name in dict_files.keys():
        data = dict_files[track_name]

        # Extract the dots
        latitudes = []
        longitudes = []
        for track in data.values():
            for seg in track.values():
                for point in seg.values():
                    latitudes.append(point["lat"])
                    longitudes.append(point["lon"])

        # Add the line containing all dots

        line = folium.ColorLine(positions=list(zip(latitudes, longitudes)),
                                colors=color_fonction(data, track_name),
                                colormap=['blue', 'red'],
                                weight=5)

        folium.PolyLine(locations=list(zip(latitudes, longitudes)),
                        color=None, tooltip=folium.Popup(track_name)).add_to(line)

        tracks.append(line)

    # Create the map
    lat_med = median(latitudes)
    long_med = median(longitudes)
    map = folium.Map(location=[lat_med, long_med], zoom_start=13.5)

    for track in tracks:
        track.add_to(map)

    # Save the map
    map.save(f'extracted_data/maps/{map_name}.html')