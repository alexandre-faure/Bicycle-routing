'''
Main file for the project
'''

import argparse
import os
import map_matching
import data_cleaning
import variables_extraction

def main():
    '''
    Main function of the package pre-processing.
    '''
    # Définir les arguments en ligne de commande
    parser = argparse.ArgumentParser(description="Pre-processing module")
    parser.add_argument("--module", choices=["map-matching",
                                             "data-cleaning",
                                             "variables-extraction",
                                             "all"],
                        help="Choose which sub-module to run.\n\
                        You can't run 'data-cleaning' without running 'map-matching' first and\
                        you can't run 'variables-extraction' without running 'data-cleaning' first.")

    # Analyser les arguments en ligne de commande
    args = parser.parse_args()

    # Créer les dossiers de sortie s'ils n'existent pas
    DATA_PATH = os.path.join("../data")

    if not os.path.exists(os.path.join(DATA_PATH,"JSON/originals_mm")):
        os.makedirs(os.path.join(DATA_PATH,"JSON/originals_mm"))
    if not os.path.exists(os.path.join(DATA_PATH,"JSON/originals_mm_full")):
        os.makedirs(os.path.join(DATA_PATH,"JSON/originals_mm_full"))

    # Exécuter le sous-module approprié en fonction de l'argument passé
    if args.module in ("map-matching", "all"):
        print("[Step 1] Map-matching")
        #map_matching("input_gpx_data.gpx", "originals_mm")

    if args.module in ("data-cleaning", "all"):
        print("[Step 2] Data cleaning")
        data_cleaning.main(os.path.join(DATA_PATH, "JSON"))

    if args.module in ("variables-extraction", "all"):
        print("[Step 3] Variables extraction")
        variables_extraction.main(os.path.join(DATA_PATH, "JSON/originals_mm_full_truncated"))

if __name__ == "__main__":
    main()
