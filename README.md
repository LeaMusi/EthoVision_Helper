# EthoVision_Helper

This script contains a collection of functions designed to put EthoVision tracks into a more usable format for further data analysis. This includes interpolating, smoothing, extracting data and metadata and writing them out as separate csv files. Some of them call on each other.



## Overview of functions:
**savitzky-golay:** implements a Savitzky-Golay filter for smoothing tracks, returns smoothed tracks as numpy array.  
References:   
A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.   
Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688

**read_tracks_excel:** reads tracks from excel file, separates data from metadata and returns them as pandas dataframes. Interpolates up to two consecutive empty cells.

**write_out_track:** writes out smoothed or unsmoothed tracks as well as metadata to csv files.

**data_preprocessing:** uses **read_tracks_excel** to read in data, smoothes them using **savitzky-golay** or not, then writes them out using **write_out_track**.

**data_initialization:** 
