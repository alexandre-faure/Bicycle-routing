'''
This module provides functions to interact with the data.
'''

import os
import re
import json
import numpy as np


def get_files_from_folder(folder:str, extension:str, with_root:bool=True) -> list:
    '''
    Get all the paths of the files of a folder with a given extension.
    The root of the path can be included or not.
    INPUT:
        - extension (str) : give the extension of the files to find.
        - folder (str) : path to the folder where to look for the files.
        - with_root (bool) (default: True) : wether the path contains the folder path or not.
    OUTPUT:
        - files_paths (list) : List of the paths to the GPX files.
    '''
    ext_filenames = filter(lambda x: x[-len(extension)-1::] == "."+extension, os.listdir(folder))

    if with_root:
        ext_filenames = map(lambda x: folder + "/" * (folder[-1] != "/") + x, ext_filenames)

    return list(ext_filenames)


def open_json(filenames:list) -> dict:
    '''
    Open all json files and return list of dictionnaries related to the input files.
    INPUT:
        - filenames (list) : list of jthe .json filenames (str) to open.
    OUTPUT:
        - output (dict) : dictionnary of dictionnaries related to the input json files.
    '''
    res = {}
    for filename in filenames:
        with open(filename, 'r', encoding="utf-8") as json_file:
            _, name = re.findall("\/([^\/]+)\/([^\/]+)\.[^\/\.]+$", filename)[0]
            res[f"{name}"] = json.load(json_file)

    return res

def convert_to_json_serializable(obj):
    '''
    Convert an object to a JSON serializable object.
    INPUT:
        - obj : object to convert.
    OUTPUT:
        - obj : JSON serializable object.
    '''

    if isinstance(obj, dict):
        # If the object is a dictionary, go through its values
        for key, value in obj.items():
            # Recursive call for each value of the dictionary
            obj[key] = convert_to_json_serializable(value)
    elif isinstance(obj, list):
        # If the object is a list, go through its elements
        for i, item in enumerate(obj):
            # Recursive call for each element of the list
            obj[i] = convert_to_json_serializable(item)
    elif isinstance(obj, np.int64):
        # If the object is a numpy int64, convert it to int
        obj = int(obj)
    return obj

def save_json_files(files_data:dict, folder:str, indent:int=4) -> None:
    '''
    Save a dictionary of files in a folder.
    INPUT:
        - data (dict) : dictionary of filenames to save.
        - folder (str) : path to the folder where to save the file.
        - indent (int) (default: 4) : indentation of the JSON file.
    OUTPUT:
        - None
    '''
    # We save the files
    for filename, data in files_data.items():
        with open(f"{folder}/{filename}.json", 'w', encoding="utf-8") as json_file:
            json.dump(convert_to_json_serializable(data), json_file, indent=indent, ensure_ascii=False)
