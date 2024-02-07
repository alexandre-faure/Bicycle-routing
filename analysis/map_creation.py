import folium
import re
from statistics import median


def draw_map_from_json(data_dict: dict, map_name: str = "map_test"):
    '''
    Create a map (html file) with the tracks extracted from gpx files on folium

    Input :
        - data_dict (dict) : dictionnary of the dictionnaries of data extracted from the json files.
                            To get such dictionnary, you can refer to the open_json function in the json_processing module.
        - map_name (str) : name of the html file to create (containing the map) without ".html"

    Output :
        - None
    '''
    tracks = []

    def colors(x):
        if 'mm' in x:
            return 'red'
        return 'blue'

    # Add all tracks
    for filename, data in data_dict.items():
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

    new_map = folium.Map(location=[lat_med, long_med], zoom_start=13.5)

    for track in tracks:
        track.add_to(map)

    # Save the map
    new_map.save(f'data/maps/{map_name}.html')


if __name__ == '__main__':
    pass
