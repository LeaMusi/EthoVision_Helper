# EthoVision_Helper

This script contains a collection of functions designed to put EthoVision tracks into a more usable format for further data analysis. This includes interpolating, smoothing, extracting data and metadata and writing them out as separate csv files. Some of them call on each other.

**savitzky-golay:** implements a Savitzky-Golay filter for smoothing tracks.  
References:   
A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.   
Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688


**read_tracks_excel:** reads tracks from excel file, separated data from metadata. Interpolates all empty coordinate cells.

**write_out_track:** 
