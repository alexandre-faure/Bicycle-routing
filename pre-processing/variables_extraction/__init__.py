'''
Init file for variables_extraction module.
'''

import os
from progress.bar import Bar
from data_interactions import get_files_from_folder, open_json, save_json_files
from .calculate_speed import calculate_speed_of_track, filter_outlying_speeds,\
    filter_speed_stop_track, filter_unrealistic_accelerations
from .calculate_elevation import calculate_elevation_of_track
from .calculate_cumulated_dist import calculate_cumulated_dist
from .calculate_slope import calculate_slope_of_track, filter_outlying_slopes,\
    filter_slope_stop_track, filter_unrealistic_slope_derivate
from .calculate_azimuth import calculate_azimuth_of_track
from .calculate_turns import calculate_turns_of_track

def main(data_path:str):
    '''
    Main function of the module variables_extraction.
    INPUT:
        - data_path (str) : path to the folder containing the JSON files.
    '''
    # Check if the data have previously been cleaned
    if not os.path.exists(data_path) or len(os.listdir(data_path)) == 0:
        raise FileNotFoundError("  The data have not been cleaned yet.")

    # We add the variables to the data
    print("  > Adding variables to the data...")

    # We get the files to add variables to
    print("  > Loading files to add variables to...")
    filenames_to_add_variables = get_files_from_folder(data_path, "json")
    files_to_add_variables = open_json(filenames_to_add_variables)
    print("  > Files to add variables to loaded.")

    # We add the speed to the files
    print("  > Adding speed...")
    if not check_already_calculated(files_to_add_variables, "speed"):
        # We calculate the raw speed
        print("  --> [1/4] Calculating raw speed...")
        do_forall_tracks(files_to_add_variables, calculate_speed_of_track, "speed")

        # We filter outlying speeds
        print("  --> [2/4] Filtering outlying speeds...")
        do_forall_tracks(files_to_add_variables, filter_outlying_speeds, "speed")

        # We filter speed stop track
        print("  --> [3/4] Filtering speed stop track...")
        do_forall_tracks(files_to_add_variables, filter_speed_stop_track, "speed")

        # We filter unrealistic accelerations
        print("  --> [4/4] Filtering unrealistic accelerations...")
        do_forall_tracks(files_to_add_variables, filter_unrealistic_accelerations, "speed")

        print("  > Speed added.")
    else:
        print("  > Speed not changed.")
    
    
    # We add the elevation to the files
    print("  > Adding elevation...")
    if not check_already_calculated(files_to_add_variables, "elevation"):
        do_forall_tracks(files_to_add_variables, calculate_elevation_of_track, "elevation")
        print("  > Elevation added.")
    else:
        print("  > Elevation not changed.")

    # We add the cumulated distance to the files
    print("  > Adding cumulated distance...")
    if not check_already_calculated(files_to_add_variables, "cumulated_dist"):
        do_forall_tracks(files_to_add_variables, calculate_cumulated_dist, "cumulated_dist")
        print("  > Cumulated distance added.")
    else:
        print("  > Cumulated distance not changed.")
    
    # We add the slope to the files
    print("  > Adding slope...")
    if not check_already_calculated(files_to_add_variables, "slope"):
        # We calculate the raw slope
        print("  --> [1/4] Calculating raw slope...")
        do_forall_tracks(files_to_add_variables, calculate_slope_of_track, "slope")

        # We filter outlying slopes
        print("  --> [2/4] Filtering outlying slopes...")
        do_forall_tracks(files_to_add_variables, filter_outlying_slopes, "slope")

        # We filter slope stop track
        print("  --> [3/4] Filtering slope stop track...")
        do_forall_tracks(files_to_add_variables, filter_slope_stop_track, "slope")

        # We filter unrealistic slope derivate
        print("  --> [4/4] Filtering unrealistic slope derivate...")
        do_forall_tracks(files_to_add_variables, filter_unrealistic_slope_derivate, "slope")

        print("  > Slope added.")
    else:
        print("  > Slope not changed.")

    # We add the azimuth to the files
    print("  > Adding azimuth...")
    if not check_already_calculated(files_to_add_variables, "azimuth"):
        do_forall_tracks(files_to_add_variables, calculate_azimuth_of_track, "azimuth")
        print("  > Azimuth added.")
    else:
        print("  > Azimuth not changed.")
    
    # We add the turns to the files
    print("  > Adding turns...")
    if not check_already_calculated(files_to_add_variables, "turns"):
        do_forall_tracks(files_to_add_variables, calculate_turns_of_track, "turns")
        print("  > Turns added.")
    else:
        print("  > Turns not changed.")


    # We save the files
    print("  > Saving files...")
    save_json_files(files_to_add_variables, data_path)
    print("  > Files saved.")

    
def check_already_calculated(files_data:dict, name:str) -> bool:
    '''
    Check if the variable has already been calculated.
    INPUT:
        - files_data (dict) : dictionnary of dictionnaries related to the input json files.
        - name (str) : name of the variable to check.
    OUTPUT:
        - bool : True if the variable has already been calculated, False otherwise.
    '''
    if name in list(list(files_data.values())[0].values())[0]:
        if input(f"  --> The variable '{name}' has already been calculated.\n" +\
                  "      Do you want to overwrite it? (y/n) ").lower() == "y":
            return False
        return True
    return False

def do_forall_tracks(files_data:dict, fun, name:str) -> None:
    '''
    Apply a function to all the tracks and save the result in
    the dictionnary with the given name.
    INPUT:
        - files_data (dict) : dictionnary of dictionnaries related to the input json files.
        - fun (function) : function to apply to the tracks.
        - name (str) : name of the variable to add.
    OUTPUT:
        - None
    '''
    pbar = Bar("Progression", max=len(files_data))
    for track_data in files_data.values():
        values = fun(track_data)
        for i, point in enumerate(track_data.values()):
            point[name] = values[i]
        pbar.next()
    pbar.finish()