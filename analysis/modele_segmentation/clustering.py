import numpy as np
import os
import json
import segmentation as seg
import time
import pandas as pd
from useful_fcts import latlon_to_xyz


def is_point_on_segment(point: np.ndarray, segment: np.ndarray):
    """_summary_

    Args:
        point (np.ndarray): _description_
        segment (np.ndarray): _description_

    Returns:
        np.ndarray: _description_
    """
    tolerance = 4.0  # Largeur de la route en mètres
    points = list(segment.values())
    end = points[0]['xyz']
    for i in range(len(points) - 1):
        start = end
        end = points[i + 1]['xyz']
        segment_direction = end - start
        segment_length = np.linalg.norm(segment_direction)
        if segment_length == 0:
            continue
        point_direction = point - start
        dot_product = np.dot(segment_direction, point_direction)
        if dot_product < - tolerance * segment_length or dot_product > segment_length * (segment_length + tolerance):
            continue
        elif 0 <= dot_product <= segment_length ** 2:
            perpendicular_distance = np.linalg.norm(
                np.cross(segment_direction, point_direction))*(1/segment_length)
            if perpendicular_distance <= tolerance:
                return True, i
        else:
            if np.linalg.norm(point_direction) <= tolerance or ((i == len(points) - 2) and (np.linalg.norm(point - end) <= tolerance)):
                return True, i
    return False, 0


def load_segments(file: str, seg_distance: float) -> np.ndarray:
    segments = seg.segmentation_uni(file=file, seg_distance=seg_distance)
    segments_xyz = []
    for segment in segments.values():
        segment_xyz = {}
        for key, point in segment.items():
            xyz = latlon_to_xyz(latitude=point['lat'], longitude=point['lon'])
            segment_xyz[key] = {'xyz': xyz, 'time': point['time']}
        segments_xyz.append(segment_xyz)
    return np.array(segments_xyz, dtype=object)


def load_json(file_path):
    with open(file_path) as f:
        data = json.load(f)
    df = pd.DataFrame.from_dict(data, orient='index')
    df['xyz'] = df.apply(lambda row: latlon_to_xyz(
        row['lat'], row['lon']), axis=1)
    return df


def create_file(file: str, seg_distance: float) -> None:
    total_time = 0
    matching_points_dict = {}
    folder_path = 'data/JSON/originals_mm_full_truncated'
    segments_xyz = load_segments(
        file=file, seg_distance=seg_distance)

    track_nb = 0
    K_matched = 1
    l_seg = len(segments_xyz)
    S = np.cumsum([len(seg) for seg in segments_xyz])

    SE = {f'seg{k}': {'A': 0, 'B': 0} for k in range(l_seg)}
    matching_points_dict = {
        f'seg{k}_A': {} for k in range(l_seg)
    }
    matching_points_dict.update({
        f'seg{k}_B': {} for k in range(l_seg)
    })

    file_list = [filename for filename in os.listdir(
        folder_path) if filename.endswith('json')]

    # Parcourir les traces test et enregistrer les points sur un même tronçon de route que la trace de référence
    for filename in file_list:
        track_nb += 1
        t2 = time.time()
        file_path = os.path.join(folder_path, filename)
        points = load_json(file_path=file_path)

        s_test = None
        Sign = SE.copy()

        for p, point_ser in points.iterrows():
            point_xyz = latlon_to_xyz(
                latitude=point_ser.iloc[0], longitude=point_ser.iloc[1])
            for k in range(l_seg):
                K_test = (K_matched - 1 + k) % l_seg
                result, matchp = is_point_on_segment(
                    point_xyz, segments_xyz[K_test])
                if result:
                    s = S[K_test] + matchp
                    if s_test is not None:
                        sign = np.sign(s_test - s)
                        Sign[f'seg{K_test}']['A' if sign > 0 else 'B'] += 1
                    s_test = s
                    K_matched = K_test

                    point_ser['xyz'] = point_ser['xyz'].tolist()
                    Sign[f'seg{K_test}'][p] = point_ser.to_dict()
                    break
        for key, values in Sign.items():
            SensA, SensB = values['A'], values['B']
            sens = 'A' if SensA >= SensB else 'B'
            matching_points_dict[f'{key}_{sens}'][filename] = values.copy()

        # Enregistrer les points correspondants dans un dictionnaire
        delta_t = round(time.time() - t2, 2)
        total_time = round(total_time + delta_t, 2)
        print(track_nb, filename, delta_t, total_time)

    with open(f'data/JSON/clustering/clustering_seg_d_{seg_distance}.json', 'w') as f:
        json.dump(matching_points_dict, f)


def sense1(dico: dict) -> dict:
    """_summary_

    Args:
        dico (dict): _description_

    Returns:
        dict: _description_
    """
    new_dico = {}
    for key in dico.keys():
        new_dico[f'{key}_A'] = {}
        new_dico[f'{key}_B'] = {}
        for track, value in dico[key].items():
            if len(value.keys()) > 1:
                if len(new_dico[f'{key}_A'].keys()) == 0:
                    new_dico[f'{key}_A'][track] = value
                    ptA0_xyz = np.array(list(value.values())[0]['xyz'])
                    ptA1_xyz = np.array(list(value.values())[1]['xyz'])
                else:
                    pt0_xyz = np.array(list(value.values())[0]['xyz'])
                    pt1_xyz = np.array(list(value.values())[1]['xyz'])
                    dot_product = np.dot(
                        pt1_xyz - pt0_xyz, ptA1_xyz - ptA0_xyz)
                    if dot_product >= 0:
                        new_dico[f'{key}_A'][track] = value
                    else:
                        new_dico[f'{key}_B'][track] = value

        print(key, 'segA : ', len(new_dico[f'{key}_A'].keys()), 'segB : ', len(
            new_dico[f'{key}_B'].keys()))


if __name__ == '__main__':
    seg_distance = 2000
    file = '02_juil._08h06_-_08h23.json'
    create_file(file=file, seg_distance=seg_distance)
