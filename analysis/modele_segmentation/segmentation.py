import numpy as np
from useful_fcts import latlon_to_xyz
import folium
from statistics import median
import json


def segmentation_uni(file: str, seg_distance: float = 50) -> dict:
    """Performs uniform segmentation along the track by cutting segments of constant distance

    Args:
        track (dict): the trace to be segmented
        seg_size (float, optional): the size of a segment. Defaults to 50.

    Returns:
        dictionnaire : format des json entree : {'nom de la trace':{track0: {seg0:{...}, seg1{...}}}}
    """
    dist = [0.0]
    dist_tot = 0.0
    i, j = 0, 0
    M1 = np.array([])

    file_path = f'data/JSON/originals_mm_full/{file}'
    with open(file=file_path, mode='r') as f:
        points = json.load(f)

    segments = {}
    seg = {}
    for key, point in points.items():
        lon2 = point['lon']
        lat2 = point['lat']
        M2 = latlon_to_xyz(latitude=lat2, longitude=lon2)
        if np.any(M1):
            dist_tot += np.linalg.norm(M2 - M1)
            dist.append(dist_tot)
            if dist_tot < (seg_distance * (i + 1)):
                seg[key] = point
            else:
                i += 1
                if len(seg) > 0:
                    segments[f'seg{j}'] = seg
                    j += 1
                    seg = {}
        M1 = M2

    return segments


def display_segmented_track(seg_track):
    '''fontion qui affiche une trace segmentée

    Input :
        - seg_track (dict): trace segmentée de structure :{'nom de la trace':{track0: {seg0:{...}, seg1{...}}}}

    Output:
        - None
    '''
    tracks = []

    def colors(x):
        return (int(x[-1]) % 2 == 0) * "blue"+(int(x[-1]) % 2 == 1)*"red"

    # Add all tracks

    for track_name in seg_track.keys():
        data = seg_track[track_name]

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
                color=colors(track_name)
            )
        )

    # Create the map
    lat_med = median([median([point[0] for point in track.locations])
                     for track in tracks])
    long_med = median(
        [median([point[1] for point in track.locations]) for track in tracks])

    map = folium.Map(location=[lat_med, long_med], zoom_start=13.5)

    for track in tracks:
        track.add_to(map)

    # Save the map
    map.save(f'extracted_data/maps/segmented_500.html')


if __name__ == '__main__':
    pass
