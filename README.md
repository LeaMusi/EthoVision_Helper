# EthoVision_Helper

This script contains a collection of functions designed to put EthoVision tracks into a more usable format for further data analysis. This includes extracting data and metadata and writing them out as separate csv files, as well as interpolating and smoothing if needed. Also contains a function for reading in the preprocessed data and preparing it for further analyses (e. g. by putting tracks of several subjects in one dataframe).

## Typical use   
```
# Tell python where to find ev_output_helper.py as well as the raw xlsx output files:

import sys   
sys.path.append("Location/of/EthoVision/Helper")   
rawfilepath = "Location/of/EthoVision/output/files"   
import ev_output_helper as evoh   
   
# First extract unsmoothed data as well as smoothe data, for 2 subjects tracked per trial:

evoh.data_preprocessing(rawfilepath=rawfilepath, smoothe_all=True, extract_all_unsmoothed=True, subjects_per_trial=2)   

# Then read in, check and prepare data for further analysis:

dat, framedur = evoh.data_initialization(rawfilepath=rawfilepath, use_smoothed_data=True, trial_id=i, subjects_per_trial=2)
```

## Overview of functions:

**read_tracks_excel:** reads tracks from excel file, separates data from metadata and returns them as pandas dataframes. Interpolates with a limit of two consecutive empty cells.

**write_out_track:** writes out smoothed or unsmoothed tracks as well as metadata to csv files.

**data_preprocessing:** uses **read_tracks_excel** to read in data, smoothes them or not, then writes them out using **write_out_track**. Asks for the number of rows of metadata as manual input!

**data_initialization:** reads in preprocessed data and metadata, performs rough check for missing frames, 
        includes tracks of all subjects as columns in one dataframe, takes user-defined independent variables 
        from metadata and appends them to data as columns (group variables).
