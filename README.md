# EthoVision_Helper

This script contains a collection of functions designed to put EthoVision tracks into a more usable format for further data analysis. This includes interpolating, smoothing, extracting data and metadata and writing them out as separate csv files. Some of them call on each other.

## Typical use   
```
# Tell python where to find ev_output_helper.py as well as the raw xlsx output files
import sys   
sys.path.append("Location/of/EthoVision/Helper")   
rawfilepath = "Location/of/EthoVision/output/files"   
import ev_output_helper as evoh   
   
# First extract unsmoothed data as well as smoothe data, for 2 subjects tracked per trial
evoh.data_preprocessing(rawfilepath=rawfilepath, smoothe_all=True, extract_all_unsmoothed=True, subjects_per_trial=2)   

# Then read in, check and prepare data for further analysis
dat, framedur = evoh.data_initialization(rawfilepath=rawfilepath, use_smoothed_data=True, trial_id=i, subjects_per_trial=2)
```

## Overview of functions:
**savitzky-golay:** implements a Savitzky-Golay filter for smoothing tracks, returns smoothed tracks as numpy array.  
References:   
A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.   
Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688

**read_tracks_excel:** reads tracks from excel file, separates data from metadata and returns them as pandas dataframes. Interpolates with a limit of two consecutive empty cells.

**write_out_track:** writes out smoothed or unsmoothed tracks as well as metadata to csv files.

**data_preprocessing:** uses **read_tracks_excel** to read in data, smoothes them using **savitzky-golay** or not, then writes them out using **write_out_track**.

**data_initialization:** reads in preprocessed data and metadata, performs rough check for missing frames, 
        includes tracks of all subjects as columns in same dataframe, takes user-defined independent variables 
        from metadata and appends them to data as columns (group variables).
