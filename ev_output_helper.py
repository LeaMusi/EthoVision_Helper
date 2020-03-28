#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created Mar 2020

@author: %Lea Musiolek


This tool is shared under the GNU General Public License v3.0 or later.
"""


def read_tracks_excel(xlsfile, no_of_headerrows, sheet_no):
    ''' Reads tracks from excel file. Interpolates up to 5 consecutive empty coordinate cells.
        Parameters:
        xlsfile             - name of input file as string
        no_of_headerrows    - number of rows that form the data header (sometimes more than 1)
        sheet_no            - index number of sheet from xls file to be read in
    
        Returns: 
        df                  - coordinates as pandas dataframe 
        metadata            - information on the tracking file from the first n rows set by metadata_rows
    '''
    
    import pandas as pd
    import numpy as np
    
    df=pd.read_excel(io=xlsfile, sheet_name=sheet_no)
    metadata_rows = df['Number of header lines:'].loc[df['Number of header lines:'] == "Trial time"].index[0]
    
    metadata=df.iloc[:metadata_rows]
    
    df = df.drop(df.index[0:metadata_rows])
    df.columns = df.iloc[0]
    df = df.drop(df.index[0:no_of_headerrows])
    df = df.reset_index()
    df = df.drop("index", axis=1)
    
    df=df.replace("-",np.NaN)
    df["X center"]=df["X center"].astype(float).interpolate(method="linear", axis=0, limit=5)
    df["Y center"]=df["Y center"].astype(float).interpolate(method="linear", axis=0, limit=5)
    
    return df, metadata

#%%
def write_out_track(xlsfile, outpath, coord, metadata, sheet_no, smoothed):
    if smoothed:
        outcsvfile = outpath+"smoo_"+xlsfile.split("/")[-1].split(".")[-2]+"sheet_"+str(sheet_no)+".csv"
        outmetafile = outpath+"meta_"+xlsfile.split("/")[-1].split(".")[-2]+"sheet_"+str(sheet_no)+".csv"
    else:
        outcsvfile = outpath+"unsmoo_"+xlsfile.split("/")[-1].split(".")[-2]+"sheet_"+str(sheet_no)+".csv"
        outmetafile = outpath+"meta_"+xlsfile.split("/")[-1].split(".")[-2]+"sheet_"+str(sheet_no)+".csv"
    coord.to_csv(outcsvfile, header=True, index=False, float_format="%.5f",sep="\t")
    metadata.to_csv(outmetafile, header=False, index=False, float_format="%.5f",sep="\t")

#%%
def data_preprocessing(rawfilepath, smoothe_all, extract_all_unsmoothed, subjects_per_trial):
    ''' Performs preprocessing steps as desired by using read_tracks_excel, savitzky-golay and write_out_track. Requires manuel input!
        Parameters:
        rawfilepath             - Directory containing raw EthoVision output files
        smoothe_all             - Boolean of whether to smoothe data or not
        extract_all_unsmoothed  - Boolean of whether to extract unsmoothed data or not
        subjects_per_trial      - Number of subjects tracked in given trial (i e number of sheets in EthoVision output xlsx file)
    
        Returns: none
    '''
    import glob
    import numpy as np
    import os
    import scipy.signal as sgn
    
    if not os.path.exists(rawfilepath+"preprocessed_tracks/"):
        os.makedirs(rawfilepath+"preprocessed_tracks/")
    
    if smoothe_all or extract_all_unsmoothed:
        datfiles=glob.glob(rawfilepath+"*Trial*.xlsx")
        print("\nNumber of raw xlsx files:", len(datfiles))
        header_rows = int(input("User input needed: How many rows make up the column headers of the tracking data? This is sometimes more than one row. \nEnter here:   "))
        for xlsfile in datfiles:
            for sheet_no in range(0, subjects_per_trial):
                #print(xlsfile)
                coord, metadata=read_tracks_excel(xlsfile, header_rows, sheet_no)
                coord.dropna(axis=0, subset=["X center", "Y center"], inplace=True)
                outpath = rawfilepath+"preprocessed_tracks/"
                if extract_all_unsmoothed:    
                    write_out_track(xlsfile, outpath, coord, metadata, sheet_no, smoothed=False)
                if smoothe_all:  
                    if len(coord)==0:
                        print("Warning: no tracking data in sheet " + str(sheet_no) + " of \n" + xlsfile + ".")
                        write_out_track(xlsfile, outpath, coord, metadata, sheet_no, smoothed=True)
                    else:
                        coord["X center"]=sgn.savgol_filter(np.array(coord["X center"]), window_length=5, polyorder=3, deriv=0)
                        coord["Y center"]=sgn.savgol_filter(np.array(coord["Y center"]), window_length=5, polyorder=3, deriv=0)
                        write_out_track(xlsfile, outpath, coord, metadata, sheet_no, smoothed=True)

#%%
def data_initialization(rawfilepath, use_smoothed_data, trial_id, subjects_per_trial):
    ''' Reads in preprocessed data and metadata, performs rough check for missing frames, 
        includes tracks of all subjects as columns in one dataframe, takes user-defined independent variables 
        from metadata and appends them to data as columns (group variables).
        Parameters:
        rawfilepath             - Directory containing raw EthoVision output files
        use_smoothed_data       - Boolean of whether to use smoothed data or not
        trial_id                - Number of trial to be used (same as in EthoVision output xlsx file name)
        subjects_per_trial      - Number of subjects tracked in this trial (i e number of sheets in EthoVision output xlsx file)
    
        Returns:
        dat0                    - Pandas dataframe containing data
        framedur                - Typical frame duration (duration of first frame in recording time)
    '''
    
    import glob
    import pandas as pd
    
    print("Selected trial:", str(trial_id))

    if use_smoothed_data:
        filestart = rawfilepath+"preprocessed_tracks/smoo"
        metastart = rawfilepath+"preprocessed_tracks/meta"
    else:
        filestart = rawfilepath+"preprocessed_tracks/unsmoo"
        metastart = rawfilepath+"preprocessed_tracks/meta"
 

    for i in range(0, subjects_per_trial):
        infiles = glob.glob(filestart+"* "+str(trial_id)+"sheet_"+str(i)+".csv")
        metafiles = glob.glob(metastart+"* "+str(trial_id)+"sheet_"+str(i)+".csv")
        dat = pd.read_csv(infiles[0], sep="\t", header=0)
        meta = pd.read_csv(metafiles[0], sep="\t", header=None, index_col=0)
        dat.reset_index(inplace=True)
        dat.drop(columns="index", inplace=True)
        if "subject_type" in meta.index:
            sub_type = meta.loc['subject_type'][1]
        else:
            sub_type = "subject"
    
        # If there is tracking data, do rough check of data integrity
        err = False
        if len(dat) > 0:
            for j in range(0, len(dat)-1):
                if round(dat.iloc[j]["Trial time"], 3) != round(dat.iloc[j]["Recording time"], 3):
                    print("Subject "+str(i)+sub_type+": Trial time not in sync with recording time, please check!")
                    err = True
                    break
                framedur = round(dat.iloc[1]["Recording time"]-dat.iloc[0]["Recording time"], 2)
                if round(dat.iloc[j+1]["Recording time"]-dat.iloc[j]["Recording time"], 2) != framedur:
                    print("Subject "+str(i)+sub_type+" Warning: Some frames seem to be missing!")  
                    err = True
                    break
        
        if err:
            print("Warning: Data contains gaps or frame duration is flawed!")
        else:
            print("Data checked, all clear!")
            dat = dat[['Trial time', 'X center', 'Y center']]
            dat.columns = ['Trialtime', 'X_'+sub_type, 'Y_'+sub_type] # Rename coordinate columns according to subject type
            
            if i == 0:
                dat0 = dat
            else:
                ncount0 = len(dat0)
                ncount = len(dat)
                if ncount != ncount0:
                    print("Warning: Number of recorded frames strongly diverge between subjects!") 
                dat0 = pd.merge(dat0, dat, on="Trialtime")

    # Add columns for additional IVs possibly written out in raw file         
    ud = meta.loc['User-defined Independent Variable':][1]
    for i in range(1, len(ud)):
        if str(meta.loc[ud.index[i]][1]) != "nan":
            dat0[ud.index[i]] = meta.loc[ud.index[i]][1]
    dat0.drop("subject_type", axis=1, inplace=True)
                       
    return dat0, framedur