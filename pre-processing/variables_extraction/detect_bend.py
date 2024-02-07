import numpy as np
import matplotlib.pyplot as plt
import json
from useful_fcts import latlon_to_xyz, draw_map_from_dict


def extract_data(file: str) -> dict:
    full_points = {}
    error, l, v = 0, 0, 0
    while error < 2:
        track_ref = file[:-6] + str(v) + '.json'
        v += 1
        print(track_ref)
        try:
            with open(file=track_ref, mode='r') as f:
                points = json.load(f)
            for key, point in points.items():
                full_points[key[:5] + str(int(key[5:]) + l)] = point
            l += len(points.keys())
        except:
            error += 1
    return full_points


def calculate_angles(points: dict, bounds: float) -> list:
    Angles, Dist, bendPoints = [], [], []
    Dev_tot = []
    s = None
    debut = True
    dist = 0
    N1 = None
    for i in range(0, len(points.keys()) - 1):
        current_point = latlon_to_xyz(
            latitude=points[f'point{i}']['lat'], longitude=points[f'point{i}']['lon'])
        next_point = latlon_to_xyz(
            latitude=points[f'point{i + 1}']['lat'], longitude=points[f'point{i + 1}']['lon'])
        vector2 = next_point - current_point
        N2 = np.linalg.norm(vector2)
        if N2 != 0:
            if N1 is not None:
                dot_product = np.dot(vector1, vector2)
                # angle = np.arccos(dot_product / magnitudes_product)
                cross_product = np.cross(vector1, vector2)

                oriented_angle = np.degrees(np.arctan2(
                    np.linalg.norm(cross_product), dot_product))
                if np.dot(current_point, np.cross(vector1, vector2)) < 0:
                    oriented_angle = -oriented_angle
                if len(Angles) > 0:
                    if oriented_angle * Angles[-1] >= 0:
                        s += oriented_angle
                    else:
                        s = oriented_angle
                else:
                    s = oriented_angle
                Dev_tot.append(s)
                if abs(s) >= bounds:
                    if debut:
                        bendPoints.append(
                            {f'point{i+1}': points[f'point{i + 1}']})
                        debut = False
                else:
                    debut = True
                Angles.append(oriented_angle)
                dist += np.linalg.norm(vector1)
                Dist.append(dist)
            N1 = N2
            vector1 = vector2
    return Angles, Dist, Dev_tot, bendPoints


if __name__ == '__main__':
    file = 'extracted_data/JSON/originals_filtered_mm_full/02_juil._08h06_-_08h23_0.json'
    points = extract_data(file=file)
    bounds = 25
    Angles, Dist, Dev_tot, bendPoints = calculate_angles(
        points=points, bounds=bounds)
    draw_map_from_dict({file: points}, map_name='test_bend', points=bendPoints)
    plt.axhline(y=bounds)
    plt.axhline(y=-bounds)
    plt.plot(Dist, Dev_tot, 'k')
    plt.plot(Dist, Angles, 'r')
    plt.show()
    """full_points = {}
    error, l, v = 0, 0, 0
    while error < 2:
        track_ref = f'extracted_data/JSON/originals_filtered_mm_full/26_juin_11h14_-_13h24_{v}.json'
        v += 1
        print(track_ref)
        try:
            with open(file=track_ref, mode='r') as f:
                points = json.load(f)
            for key, point in points.items():
                full_points[key[:5] + str(int(key[5:]) + l)] = point
            l += len(points.keys())
        except:
            error += 1
            continue
    Curve, Dist, Time, DotCurve = [], [], [],  [0]
    dist = 0
    pA = None
    N01 = 0
    t_tot, t2 = 0, date(time=full_points['point0']['time'])
    angle2 = None
    k = 0
    while N01 < 3:
        lat0, lon0 = full_points[f'point{k}']['lat'], full_points[f'point{k}']['lon']
        p0_xyz = latlon_to_xyz(latitude=lat0, longitude=lon0)
        lat1, lon1 = full_points[f'point{k+1}']['lat'], full_points[f'point{k+1}']['lon']
        p1_xyz = latlon_to_xyz(latitude=lat1, longitude=lon1)
        N01 = np.linalg.norm(p1_xyz - p0_xyz)
        k += 1

    v01 = p1_xyz - p0_xyz

    for key, point in full_points.items():
        pB = point
        if pA is not None:
            latA, lonA = pA['lat'], pA['lon']
            pA_xyz = latlon_to_xyz(latitude=latA, longitude=lonA)
            latB, lonB = pB['lat'], pB['lon']
            pB_xyz = latlon_to_xyz(latitude=latB, longitude=lonB)
            vAB = pB_xyz - pA_xyz
            NAB = np.linalg.norm(vAB)
            if NAB > 0.5:
                # angle = np.degrees(
                #    np.arccos(np.dot(v01, vAB)/(np.linalg.norm(v01)*np.linalg.norm(vAB))))
                angle = np.dot(v01, vAB)/(np.linalg.norm(v01)
                                          * np.linalg.norm(vAB))
                if np.cross(v01, vAB) < 0:
                    angle = -angle
                Curve.append(angle)
                t1 = date(time=pA['time'])
                if angle2 is not None:
                    DotCurve.append((angle - angle2)/NAB)
                t_tot += (t1 - t2).total_seconds()
                Time.append(t_tot)
                t2 = date(time=pA['time'])
                angle2 = angle
                Dist.append(dist)
            dist += NAB
        pA = pB
    plt.axhline(y=0)
    plt.plot(Dist, Curve, 'k')
    plt.plot(Dist, DotCurve, 'r')

    # plt.plot(Time, Curve, 'k')
    # plt.plot(Time, DotCurve, 'r')

    # plt.plot(np.linspace(0, Dist[-1], len(Dist)), Curve, 'r')
    plt.show()
"""
