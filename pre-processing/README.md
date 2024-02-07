# Pre-processing module

## Description

This module is the first step of the pipeline. It takes the raw data and transforms it into a format that can be used by the other modules. It is composed of three sub-modules:
1. `map-matching` : takes raw GPX data and apply map-matching to it
2. `data-cleaning` : takes the map-matched data and clean the tracks
3. `variables_extraction` : takes the cleaned data and extract the useful variables such as speed, slope, etc.

## Usage

The `main.py` script is the entry point of the module. You can choose which sub-module to run by using the `--module` argument. It can take the following values:
- `map-matching`
- `data-cleaning`
- `variables-extraction`
- `all`

The execution of the package will generate automatically the following folders:
- `originals_mm` : contains the data after the map-matching
- `originals_mm_full` : contains the data after reprojection of the tracks on the map-matched data
- `originals_mm_full_truncated` : contains the data after having clean the tracks