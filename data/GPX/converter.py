import gpxpy
import re
import json
import os


def is_in_IDF(lon: float, lat: float) -> bool:
    '''
    Function to estimate if coordinates are in Ile de France.

    Input :
        - lon (float) : longitude
        - lat (float) : latitude

    Output :
        - res (bool) : Return wheter the coordinates are near Ile-de-France or not.
    '''
    return lon > 1.4 and lon < 3.6 and lat > 48 and lat < 49.3


def gpx_to_json(gpx_files: list, dest_folder: str = "../../extracted_data/JSON/originals/", keep_time: bool = True) -> None:
    '''
    Convert a GPX file to a JSON file ans save it it an specified folder.

    Input :
        - gpx_files (list) : list of the path to the several gpx files
        - dest_folder (str) (default: "../../extracted_data/JSON/originals/") : path to the destination folder to save the JSON files
        - keep_time (bool) (default: True) : save the time data or not

    Output :
        - None
    '''
    # For each GPX file
    for filename in gpx_files:
        gpx_file = open(filename, 'r')
        gpx = gpxpy.parse(gpx_file)
        data = {}
        i = 0

        # For each track
        for track in gpx.tracks:
            data[f"track{i}"] = {}
            j = 0
            # For each segment
            for segment in track.segments:
                data[f"track{i}"][f"seg{j}"] = {}
                k = 0
                # For each point
                for point in segment.points:
                    value = {
                        "lat": point.latitude,
                        "lon": point.longitude
                    }
                    if keep_time:
                        value["time"] = point.time.isoformat()

                    data[f"track{i}"][f"seg{j}"][f"point{k}"] = value
                    k += 1
                j += 1
            i += 1

        # Save the JSON file
        json_filename = re.findall(
            "\/([^\/]*)\.[^\/\.]*$", filename)[0] + ".json"
        try:
            if is_in_IDF(data["track0"]["seg0"]["point0"]["lon"], data["track0"]["seg0"]["point0"]["lat"]):
                with open(dest_folder + json_filename, "w") as json_file:
                    json.dump(data, json_file)
            else:
                print(f"Not in IDF : {json_filename}")
        except:
            print(filename)


if __name__ == '__main__':
    input_folder = 'data/GPX/GPX Géovélo'
    output_folder = 'extracted_data/JSON/originals/'
    files = [os.path.join(input_folder, filename) for filename in os.listdir(
        input_folder) if filename.endswith('.gpx')]
    gpx_to_json(gpx_files=files, dest_folder=output_folder, keep_time=True)
