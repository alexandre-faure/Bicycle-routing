import requests
import xml.etree.ElementTree as ET
import gpxpy.gpx
import os
import json
import time
from useful_fcts import date

# Clé d'API GraphHopper - Il faut la changer
api_key = 'c739725e-96f6-4b5c-b6a5-29510aae2bad'


def json_to_gpx(input_file: str, output_file: str):

    with open(input_file, 'r') as json_file:
        data = json.load(json_file)

    # Create a GPX object
    gpx = gpxpy.gpx.GPX()

    # Create a GPX track segment
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)

    # Create a GPX track segment segment
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)

    # Extract and add trackpoints from the JSON data as <trkpt> elements
    for point in data.values():
        latitude = point['lat']
        longitude = point['lon']
        time = date(time=point['time'])
        gpx_trackpoint = gpxpy.gpx.GPXTrackPoint(
            latitude=latitude, longitude=longitude, time=time)
        gpx_segment.points.append(gpx_trackpoint)

    # Save the GPX data to a file
    with open(output_file, 'w') as gpx_file:
        gpx_file.write(gpx.to_xml())


def mapFile(input_file, output_file) -> None:

    # URL de l'API Map Matching de GraphHopper
    url = 'https://graphhopper.com/api/1/match'

    # En-têtes de la requête
    headers = {'Content-Type': 'application/gpx+xml'}

    # Paramètres de la requête
    params = {
        'points_encoded': False,
        "profile": 'bike',
        'simplify': False,
        'instructions': True,
        "details": 'time',
        'key': api_key,
    }

    # Set the maximum number of track points per request, À RÉDUIRE SI PROBLÈME TIMEOUT
    max_track_points_per_request = 500

    # Read the input GPX file
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Extract the track points from the GPX file
    track_points = []
    for trkpt in root.findall(".//{http://www.topografix.com/GPX/1/1}trkpt"):
        lat = trkpt.attrib["lat"]
        lon = trkpt.attrib["lon"]
        track_points.append((lat, lon))

    # Divide the track points into chunks of size max_track_points_per_request
    chunks = [track_points[i:i+max_track_points_per_request]
              for i in range(0, len(track_points), max_track_points_per_request)]
    # Create a new XML tree for the output GPX file
    output_tree = ET.ElementTree(ET.Element(
        "gpx", version="1.1", xmlns="http://www.topografix.com/GPX/1/1"))

    # Loop over the chunks of track points and make Map Matching API requests
    for i, chunk in enumerate(chunks):
        # create a new GPX object
        gpx = gpxpy.gpx.GPX()

        # create a new track in the GPX file
        gpx_track = gpxpy.gpx.GPXTrack()
        gpx.tracks.append(gpx_track)

        # create a new segment in the track
        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        gpx_track.segments.append(gpx_segment)

        # Build the request URL for the Map Matching API
        for lat, lon in chunk:
            gpx_segment.points.append(
                gpxpy.gpx.GPXTrackPoint(latitude=lat, longitude=lon))

        # write the GPX file to disk
        with open(f"/data/GPX/sousfichier_{i}.gpx", "w") as f:
            f.write(gpx.to_xml())
        # Make the API request

        with open(f"/data/GPX/sousfichier_{i}.gpx", 'r') as f:
            gpx_content = f.read()

        os.remove(
            f"/data/GPX/sousfichier_{i}.gpx")
        x = False
        while not x:
            try:
                response = requests.post(url, headers=headers,
                                         params=params, data=gpx_content)
#                # Parse the response JSON
                response_data = json.loads(response.content)
                # Extract the matched points from the response
                matched_points = []
                time.sleep(1)
                for point in response_data["paths"][0]["points"]["coordinates"]:
                    lat = point[1]
                    lon = point[0]
                    matched_points.append((lat, lon))
                x = True
            except:
                print(response.text)
                time.sleep(60)
        # Add the matched points to the output GPX file
        trk = ET.SubElement(output_tree.getroot(), "trk")
        trkseg = ET.SubElement(trk, "trkseg")
        for lat, lon in matched_points:
            trkpt.tail = "\n"
            trkpt = ET.SubElement(trkseg, "trkpt", lat=str(lat), lon=str(lon))
        # Print progress message
        print("Processed chunk {}/{}".format(i+1, len(chunks)))

    print(output_file)
    # Write the modified GPX file to disk
    # output_tree.write(output_file)


if __name__ == '__main__':
    input_folder = 'data/GPX/originals'
    output_folder = 'data/GPX/map-matcjed-GH-GPX'
    Files = os.listdir(path=input_folder)
    tot = len(Files)
    count = 0
    for filename in Files:
        count += 1
        print(count, tot)
        if filename.endswith('.gpx'):
            output_file = os.path.join(output_folder, filename)
            if not os.path.exists(output_file):
                input_file = os.path.join(input_folder, filename)
                print(output_file)
                try:
                    mapFile(input_file=input_file, output_file=output_file)
                    print(input_file)
                except:
                    print("Error")
                    time.sleep(10)
