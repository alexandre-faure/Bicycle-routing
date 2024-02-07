'''
Initialisation du package data_cleaning.
'''

import os
from data_interactions import get_files_from_folder, open_json, save_json_files
from data_cleaning.json_cleaning import clean_data


def main(data_path:str):
    '''
    Function to clean the tracks.
    '''
    # Check if the data have previously been map-matched
    if not os.path.exists(os.path.join(data_path,"originals_mm_full"))\
        or len(os.listdir(os.path.join(data_path,"originals_mm_full"))) == 0:
        raise FileNotFoundError("  The data have not been map-matched yet.")

    # Check if the data have already been cleaned
    if os.path.exists(os.path.join(data_path,"originals_mm_full_truncated")):
        if len(os.listdir(os.path.join(data_path,"originals_mm_full_truncated"))) > 0:
            print("  The data have already been cleaned.")
            
            # We ask the user if he wants to clean them again
            if input("  Do you want to clean them again? (y/n) ").lower() != "y":
                print("  ---> Data cleaning aborted.")
                return
            
            # We delete the files
            for file in os.listdir(os.path.join(data_path,"originals_mm_full_truncated")):
                os.remove(os.path.join(data_path,"originals_mm_full_truncated",file))
    else:
        # We create the folder
        os.makedirs(os.path.join(data_path,"originals_mm_full_truncated"))

    # We clean the data
    print("  > Cleaning the data...")

    # We get the files to clean
    filenames_to_clean = get_files_from_folder(os.path.join(data_path,"originals_mm_full"), "json")
    files_to_clean = open_json(filenames_to_clean)
    print("  > Files to clean loaded.")

    # We clean the files
    cleaned_files = clean_data(files_to_clean, max_delay=10, min_points=10, min_distance=10)
    print("  > Files cleaned.")

    # We save the files
    save_json_files(cleaned_files, os.path.join(data_path,"originals_mm_full_truncated"))

    print("  > Data cleaning completed.")