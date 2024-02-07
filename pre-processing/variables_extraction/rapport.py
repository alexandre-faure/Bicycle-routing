import overpy
import folium
from statistics import median
import json
from os import getcwd


api = overpy.Overpass()

# récupération des noeuds qui nous intéressent dans la zone sélectionnée
result = api.query("""
    node(48.67, 2.14, 48.75, 2.24)
    [highway=traffic_signals];
    out;
    """)

feux_rouges_zone = []  # création de la liste contenant les coordonées des feux rouges

for node in result.nodes:

    node.lat, node.lon = float(node.lat), float(
        node.lon)  # on passe en flottant

    coords_fr = [node.lat, node.lon]
    feux_rouges_zone.append(coords_fr)  # on ajoute les coords à la liste


def draw_map_from_dict(dict_files: dict, map_name: str = "map_test") -> None:
    '''
    Create a map (htlm file) with the tracks extracted from gpx files on folium

    Input :
        - json_files (list) : list of the path to the several json files
        - map_name (str) : name of the html file to create (containing the map) without ".html"

    Output :
        - None
    '''
    tracks = []
    matched = False
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
        if len(latitudes) > 0:
            matched = True
            tracks.append(
                folium.PolyLine(
                    locations=list(zip(latitudes, longitudes)),
                    popup=folium.Popup(track_name),
                    color='red'
                )
            )

    if matched:
        # Create the map
        lat_med = median([median([point[0] for point in track.locations])
                          for track in tracks])
        long_med = median(
            [median([point[1] for point in track.locations]) for track in tracks])

        map = folium.Map(location=[lat_med, long_med], zoom_start=13.5)

        for track in tracks:
            track.add_to(map)

        for feu in feux_rouges_zone:
            folium.Marker(location=feu, popup="Feu rouge").add_to(map)

        # Save the map
        map.save(f'extracted_data/maps/feu.html')


def test(k: int, seg_distance: float):
    with open(getcwd() + f'/extracted_data/JSON/clustering/clustering_seg_d_{seg_distance}.json') as f:
        data = json.load(f)

    draw_map_from_dict(
        dict_files=data[f'seg{k}'], map_name=f'map_d_{seg_distance}_seg_{k}')


test(9, 100)
