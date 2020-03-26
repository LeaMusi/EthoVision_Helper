
def savitzky_golay(y, window_size, order, deriv, rate):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """
    import numpy as np
    from math import factorial

    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except(ValueError, msg):
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))

    print("Data smoothed with window size of "+str(window_size)+", polynomial of order "+str(order)+", derivative of order "+str(deriv)+" and rate "+str(rate)+".")
   
    return np.convolve( m[::-1], y, mode='valid')




#%%
def read_tracks_excel(xlsfile, no_of_headerrows, sheet_no):
    ''' Reads tracks from excel file. Interpolates all empty coordinate cells.
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
    df["X center"]=df["X center"].astype(float).interpolate(method="linear", axis=0, limit=1)
    df["Y center"]=df["Y center"].astype(float).interpolate(method="linear", axis=0, limit=1)
    
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
    
    if smoothe_all or extract_all_unsmoothed:
        datfiles=glob.glob(rawfilepath+"*Trial*.xlsx")
        print("\nNumber of raw xlsx files:", len(datfiles))
        header_rows = int(input("How many rows of metadata are there in the raw xlsx file? This means the number of rows before the first header row."))
        for xlsfile in datfiles:
            for sheet_no in range(0, subjects_per_trial):
                #print(xlsfile)
                coord, metadata=read_tracks_excel(xlsfile, header_rows, sheet_no)
                outpath = rawfilepath+"preprocessed_tracks/"
                if extract_all_unsmoothed:    
                    write_out_track(xlsfile, outpath, coord, metadata, sheet_no, smoothed=False)
                if smoothe_all:            
                    coord["X center"]=savitzky_golay(np.array(coord["X center"]), window_size=5, order=3, deriv=0, rate=1)
                    coord["Y center"]=savitzky_golay(np.array(coord["Y center"]), window_size=5, order=3, deriv=0, rate=1)
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
        #dat.dropna(subset=['X center', 'Y center'], inplace=True)
        dat.reset_index(inplace=True)
        dat.drop(columns="index", inplace=True)
        if "subject_type" in meta.index:
            sub_type = meta.loc['subject_type'][1]
        else:
            sub_type = "subject"
    
        #Do rough check of data integrity
        err = False
        for j in range(0, len(dat)-1):
            if round(dat.iloc[j]["Trial time"], 3) != round(dat.iloc[j]["Recording time"], 3):
                print("Subject "+str(i)+sub_type+": Trial time not in sync with recording time, please check!")
                err = True
                break
            framedur = round(dat.iloc[1]["Recording time"]-dat.iloc[0]["Recording time"], 2)
            if round(dat.iloc[j+1]["Recording time"]-dat.iloc[j]["Recording time"], 2) != framedur:
                print("Subject "+str(i)+sub_type+": Strongly deviant frame duration, please check!")  
                err = True
                break
        
        if err:
            print("Data contains gaps or frame duration is flawed, please check!")
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
                    print("Number of recorded frames strongly diverge between subjects, please check!") 
                dat0 = pd.merge(dat0, dat, on="Trialtime")

    # Add columns for additional IVs possibly written out in raw file         
    ud = meta.loc['User-defined Independent Variable':][1]
    for i in range(1, len(ud)):
        if str(meta.loc[ud.index[i]][1]) != "nan":
            dat0[ud.index[i]] = meta.loc[ud.index[i]][1]
    dat0.drop("subject_type", axis=1, inplace=True)
                       
    return dat0, framedur
