import numpy as np
import math
from json_processing import *
import gpxpy

# Get all files to extract (o: orignial, mm: map-matched)
o_files = get_files_from_folder(
    "json", "extracted_data/JSON/originals")
mm_files = get_files_from_folder(
    "json", "extracted_data/JSON/originals_mm")

# Get data from filenames
o_data = open_json(o_files)
mm_data = open_json(mm_files)

# Remove files with no original / map-matched correspondance
filenames = list(set(o_data.keys()) & set(mm_data.keys()))
o_data = {k: v for k, v in o_data.items() if k in filenames}
mm_data = {k: v for k, v in mm_data.items() if k in filenames}

# Remove the files already analysed
# analysed_files = get_files_from_folder("json", "extracted_data/JSON/map-matched-full-GH")
# analysed_data = open_json(analysed_files)
# filenames = list(set(filenames) - set(analysed_data.keys()))
# o_data = {k:v for k,v in o_data.items() if k in filenames}
# mm_data = {k:v for k,v in mm_data.items() if k in filenames}


def get_lines(mm_data: dict) -> dict:
    """
    Get the segments (coord_start, coord_end) of each track from filenames.

    Input:
        - mm_data (dict): dictionnary of the map-matched data for each file.

    Output:
        - lines (dict): dictionnary of the lines that composes the track of each file related to
                        the mm_data dictionnay.
    """
    lines = {}
    for file, data in mm_data.items():
        lines[file] = {}
        coord_start = None
        i = 0
        for track in data.values():
            for seg in track.values():
                for point in seg.values():
                    if coord_start is not None:
                        # Add a new line
                        lines[file][f"line{i}"] = [
                            coord_start, (point['lat'], point['lon'])]
                        i += 1
                    coord_start = (point['lat'], point['lon'])
    return lines


def get_projection(coord: tuple, line: tuple, is_between: bool = True) -> tuple:
    """
    Get the projection of a point on a line (considering 2D space regarding of the small
    distances considered).

    Input:
        - coord (tuple): coordinates of the point to project.
        - line (tuple): tuple of the coordinates of the start and the end of the line to consider.
        - is_between (bool) (default: True): force the projection to be between the two points
                                            defining the line, by taking the closest extremity if necessary.

    Output:
        - ((proj_lat, proj_lon), dist, between)
            => proj_lat (float) : latitude of the projected point
            => proj_lon (float) : longitude of the projected point
            => dist (float) : distance (arbitrary unit) between the real point and the projected one
            => between (None|bool) : None if is_between is set to False. Otherwise, if between is True,
                                    the projected point was between the two extremities of the line.
    """
    # Set some parametres
    between = None
    line_start = line[0]
    line_end = line[1]

    # Calculate the distance between the two line endpoints
    line_length = np.linalg.norm(np.array(
        [line_end[1] - line_start[1], line_end[0] - line_start[0]])) + 1e-8  # to avoid division by zero

    # Calculate the distance between the projection point and the two line endpoints
    proj_start_dist = np.linalg.norm(
        np.array([line_start[1] - coord[1], line_start[0] - coord[0]]))
    proj_end_dist = np.linalg.norm(
        np.array([line_end[1] - coord[1], line_end[0] - coord[0]]))

    # Calculate the projection of coord
    angle_seg = math.atan2(
        line_end[1] - line_start[1], line_end[0] - line_start[0])
    ratio = np.dot(np.array([coord[1] - line_start[1], coord[0] - line_start[0]]),
                   np.array([line_end[1] - line_start[1], line_end[0] - line_start[0]])) / line_length

    proj_lat = line_start[0] + np.cos(angle_seg) * ratio
    proj_lon = line_start[1] + np.sin(angle_seg) * ratio

    dist = np.linalg.norm(np.array([coord[1] - proj_lon, coord[0] - proj_lat]))

    if is_between:
        # Force the projection to be between the two coordinates
        between = True
        angle_start = math.atan2(
            line_start[1] - proj_lon, line_start[0] - proj_lat)
        angle_end = math.atan2(line_end[1] - proj_lon, line_end[0] - proj_lat)
        if abs(abs(math.degrees(angle_end-angle_start)) - 180) > 1:
            # projection not between the two coordinates
            between = False
            if proj_start_dist < proj_end_dist:
                [proj_lat, proj_lon] = line_start
                dist = proj_start_dist
            else:
                [proj_lat, proj_lon] = line_end
                dist = proj_end_dist

    return (proj_lat, proj_lon), dist, between


def get_position(coord: tuple, lines: dict, rank: int, plage: tuple = (3, 5)) -> tuple:
    """
    Get the position of a point when we suppose it's situated on one of the lines selected.

    Input:
        - coord (tuple): coordinates of the point to project
        - lines (dict): dictionnary of all the lines related to the track studied
        - rank (int): id of the line corresponding to the previous point projected
        - plage (tuple) (default: (3,5)): range of the lines to observe to determine the projection
                                        by default : [|rank - 3, rank + 5|].

    Output:
        - (rank, position)
            => rank (int): id of the line selected for the projection
            => position (tuple): coordinates of the projected point selected
    """
    inf, sup = max(
        0, rank - plage[0]), min(len(lines.keys()), rank + plage[1] + 1)
    positions = {}
    for i in range(inf, sup):
        positions[i] = {}
        positions[i]["coord"], positions[i]["dist"], positions[i]["between"] = get_projection(
            coord, lines[f"line{i}"], True)

    rank, position = next((k, v["coord"]) for k, v in positions.items(
    ) if v["dist"] == min([d["dist"] for d in positions.values()]))
    return rank, position


dest_folder = 'extracted_data/JSON/originals_mm_full/'


def create_projected_map_match(o_data: dict, mm_data: dict, dest_folder=dest_folder) -> None:
    """
    Create the complete map-matched track from the map-matched obtained with GraphHopper by projecting
    the originals tracks on the map-matched ones.

    Input:
        - o_data (dict): dictionnary of the original data
        - mm_data (dict): dictionnary of the map-matched data from GraphHopper
        - dest_folder (str) (default: "extracted_data/JSON/map-matched-full-GH"): path where to save
                            the projected tracks on the map-matched ones

    Output:
        - None
    """
    # Get all lines
    lines = get_lines(mm_data)

    # For each file
    for filename, data in o_data.items():
        print(f"File {filename}:\n\tProcessing...")
        res_data = {}
        j = 0
        for track in data.values():
            for seg in track.values():
                for key, point in seg.items():
                    i, (lat, lon) = get_position(
                        (point["lat"], point["lon"]), lines[filename], j)
                    res_data[key] = {}
                    res_data[key]["lat"] = lat
                    res_data[key]["lon"] = lon
                    res_data[key]["line"] = i
                    res_data[key]["time"] = point["time"]
                    j = i
        print(f"\tProcessing done.")

        with open(f'{dest_folder}{filename}.json', 'w', encoding="utf-8") as outfile:
            json.dump(res_data, outfile)
        print(f"\tData file saved succesfully !\n")

    return None


if __name__ == '__main__':
    create_projected_map_match(
        o_data=o_data, mm_data=mm_data, dest_folder=dest_folder)
