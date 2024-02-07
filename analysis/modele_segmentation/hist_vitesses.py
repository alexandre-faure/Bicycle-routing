import json
from useful_fcts import latlon_to_xyz
import numpy as np
from os import getcwd
import matplotlib.pyplot as plt
from useful_fcts import date
from math import sqrt


def exploitable_track(track: str, max_delay: int = 10) -> bool:
    '''
    Check whether a track is exploitable or not for further analysis.
    If the time between to successive point is superior to max_delay, it returns False.

    Input :
        - seg : segment to analyze
        - max_delay (int) (default: 10) : maximum delay in second between two points

    Output :
        - res (bool) : returns whether the track is good or not'''

    points = list(track.keys())
    if len(points) < 2:
        return False
    i, n = 1, len(points)
    while i < n:
        if (date(track[points[i]]["time"]) - date(track[points[i-1]]["time"])).total_seconds() > max_delay:
            return False
        i += 1
    return True


def create_seg(len, number):
    '''
    Input :
        - len : longueur du segment voulu
        - number : numero du sgment cherché

    Output : 
        - segment : dictionnaire associé au segment'''

    folder_path = getcwd() + \
        '/data/JSON/clustering/clustering_seg_d_' + \
        str(len) + '.json'

    with open(folder_path) as f:
        dict_file = json.load(f)

    segment = dict_file['seg'+str(number)]
    n = 0
    for k in segment.keys():
        n += 1
    segment_ok = {}
    for track in segment.keys():
        if exploitable_track(segment[track]):
            segment_ok[track] = segment[track]
    h = 0
    for k in segment_ok.keys():
        h += 1
    print(n, h)

    return segment_ok


def vitesse_seg(segment: dict):
    '''
    Input :
        - segment (dictionnaire):  associé à un segment détecté par clustering.create_file 

    Output :
        - vitesses_seg : dictionnaire des vitesses du segment étudié
    '''

    vitesse_seg = {}
    for track in segment.keys():
        t1, x1 = None, None
        speed = []
        for point in segment[track].values():
            lat, lon = point['lat'], point['lon']
            t2 = date(time=point['time'])
            x2 = latlon_to_xyz(latitude=lat, longitude=lon)
            if t1 != None:
                dx = np.linalg.norm(x2 - x1)
                dt = (t2 - t1).total_seconds()
                if dt == 0:
                    speed.append(None)
                else:
                    v = dx / dt
                    speed.append(v)
            t1, x1 = t2, x2
        vitesse_seg[track] = speed

    return vitesse_seg


def histo_segment(vitesses, segment, maxi=10, mini=0, bins=20):
    '''
    Input : - vitesses (dict):   'nom_fichier': array vitesse sur le segment
            - maxi : vitesse maximale affichée sur l'histogrammes
            - mini : vitesse minimale affichée
            - bins : nombre de barres sur l'histogramme
            - segment : nom du segment étudié

    Output : - affiche histogrammes des vitesses moyennes sur le segment
    '''

    traces = list(vitesses.keys())
    print(vitesse[traces[0]])
    Vmoy = []
    for i in range(len(traces)):
        moy = np.mean(vitesses[traces[i]])
        if moy < 14:
            Vmoy.append(moy)

    Vmoy = np.array(Vmoy)
    mean = np.mean(Vmoy)
    variance = np.var(Vmoy)
    print(Vmoy, mean, variance)
    plt.hist(Vmoy, density=True, bins=bins)
    plt.title(segment)
    plt.axvline(mean, color='r', linestyle='dashed',
                linewidth=2, label='Moyenne')
    plt.axvline(mean + sqrt(variance), color='g', linestyle='dashed',
                linewidth=2, label='Ecart-type')
    plt.axvline(mean - sqrt(variance), color='g', linestyle='dashed',
                linewidth=2)
    plt.legend()
    plt.xlabel('vitesse moyenne')
    plt.show()


seg = create_seg(200, 4)
vitesse = vitesse_seg(seg)
traces = vitesse.keys()
histo_segment(vitesse, 'seg 200m n°4')
