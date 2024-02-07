import os
import json
import numpy as np
from useful_fcts import latlon_to_xyz

original_path = 'extracted_data/JSON/originals/'
map_matched_path = 'extracted_data/JSON/map-matched-full-GH/'

def ecart_quadratique(Y_original:np.ndarray, Y_predicted:np.ndarray) -> float:
    """_summary_

    Args:
        Y_original (np.ndarray): _description_
        Y_predicted (np.ndarray): _description_

    Returns:
        float: _description_
    """
    return np.mean((Y_original - Y_predicted)**2)

def ecart(Y_original:np.ndarray, Y_predicted:np.ndarray) -> float:
    """_summary_

    Args:
        Y_original (np.ndarray): _description_
        Y_predicted (np.ndarray): _description_

    Returns:
        float: _description_
    """
    return np.mean(Y_original - Y_predicted)

def vitesse(dico:dict) -> np.ndarray:
    return 'a'

if __name__ == '__main__':
    for filename in os.listdir(path=original_path):
        if filename.endswith('.json'):
            if filename not in os.listdir(map_matched_path):
                print(f'Le fichier {filename} n est pas présent dans les deux dossiers')
                pass
            
            with open(file=original_path + filename) as f:
                original = json.load(f)
            
            with open(file=map_matched_path + filename) as f:
                map_matched = json.load(f)
            
            print(map_matched)
            
            V_original = vitesse(dico=original)
            V_mm = vitesse(dico=map_matched)