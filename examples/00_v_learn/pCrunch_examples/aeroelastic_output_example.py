# %% [markdown]
# # pCrunch's Aeroelastic Output class
# 
# The `AeroelasticOutput` class is a general container for time-series based data for a single environmental condition (i.e., a single incoming wind spead and turbulence seed value).  This might be a single run of your aeroelastic multibody simulation tool (OpenFAST or HAWC2 or Bladed or QBlade or in-house equivalents) in a larger parametric variation for design load case (DLC) analysis.  The `AeroelasticOutput` class provides data containers and common or convenient manipulations of the data for engineering analysis.  
# 
# Analysis that involve multiple time-series simulations, such as a full run of multiple wind speeds and seeds, which yield multiple AeroelasticOutput instances, is done in the `Crunch`` *class*.
# 
# This file lays out some workflows and showcases capabilities of the `AeroelasticOutput` class.

# %% [markdown]
# ## Creating a new class instance
# 
# The `AeroelasticOutput` class can be initialized from an output file or from existing data structures.  pCrunch provides a reader for OpenFAST output files (both binary and ascii).  To expand pCrunch for use with other aeroelastic multibody codes, users could simply use the `openfast_readers.py` file as a template.  If you already have the data in Python, then data structures such as dictionaries, lists, NumPy arrays, and Pandas DataFrames can all be used as a constructor.  Here are some examples with each `myobj` representing a valid AeroelatsicOutput instance:

# %%
# imports
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pCrunch import AeroelasticOutput, read, FatigueParams
#%%
# inputs
from directory_pCrunch import dir_pcrunch
datadir = os.path.join(dir_pcrunch, 'test', 'data')

# OpenFAST output files
myobj_of_ascii = read( os.path.join(datadir, 'DLC2.3_1.out') )
myobj_of_bin   = read( os.path.join(datadir, 'Test2.outb') )

# Existing data structures
mydata = {
    "Time": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "WindVxi": [7, 7, 7, 7, 7, 8, 8, 8, 8, 8],
    "WindVyi": [0] * 10,
    "WindVzi": [0] * 10,
}

# From a dictionary
myobj_from_dict  = AeroelasticOutput(mydata)

# From a Pandas DataFrame
myobj_from_df    = AeroelasticOutput( pd.DataFrame(mydata) )

# From Python lists
chan_labels      = list( mydata.keys() )
ts_data          = [m for m in mydata.values()]
myobj_from_list  = AeroelasticOutput(ts_data, chan_labels)

# From a Numpy array
myobj_from_numpy = AeroelasticOutput(np.array(ts_data), chan_labels)

# As a copy from an existing output (especially helpful when needing to filter the core data)
myobj_copy       = myobj_from_numpy.copy()

# %% [markdown]
# Additional, optional arguments can also be passed that specify a label, a description, and a vector of units for the data channels:

# %%
myunits = ['s', 'm/s', 'm/s', 'm/s']
myobj_from_dict = AeroelasticOutput(mydata, name='pseudodata', description='pCrunch example', units=myunits)

# %% [markdown]
# Magnitude channels, extremes, and fatigue are presented in greater detail below.  These additional inputs can also be specified in the constructor:

# %%
# Vector magnitudes
mc = {"Wind": ["WindVxi", "WindVyi", "WindVzi"]}

# Channel-specific fatigue properties
fc = {
    "RootMc1": FatigueParams(lifetime=25.0, slope=10.0, ultimate_stress=6e8, load2stress=250.0, S_intercept=5e9),
    "RootMc2": FatigueParams(lifetime=25.0, slope=10.0, ultimate_stress=6e8, load2stress=250.0, S_intercept=5e9),
    "RootMc3": FatigueParams(lifetime=25.0, slope=10.0, ultimate_stress=6e8, load2stress=250.0, S_intercept=5e9),
}

# Channels to focus on for extreme event tabulation
ec = ["RotSpeed", "RotThrust", "RotTorq"]

# Can also add some batch data operations in the constructor (many more available in Batch Processing below)
myobj_mc = AeroelasticOutput(mydata, magnitude_channels=mc, trim_data=[2, 8], fatigue_channels=fc, extreme_channels=ec)


# %% [markdown]
# ## Data structures and access
# 
# pCrunch stores the time series data as a Numpy array and the channel names as a list.  More sophisticated data containers, such as netcdf or hdf5, could be adopted in future work, but the simplicity, familiarity, and accessibility of the data containers should help users adopt pCrunch into their workflows.  Easy converstions back to a Python dictionary or Pandas dataframe are available:

# %%
myobj_from_dict.channels

# %%
myobj_from_dict.data

# %%
myobj_from_dict.to_dict()

# %%
myobj_from_dict.to_df()

# %% [markdown]
# Accessing the data for a particular channel is done using familiar dictionary or DataFrame syntax.  A `.time` property is also available as that is assumed to be common to all datasets

# %%
myobj_from_dict['Time']

# %%
myobj_from_dict.time

# %%
myobj_from_dict['WindVxi']

# %% [markdown]
# If working with the data or summary statistics outside of the AeroelasticOutput object, it can be help to have an easy way to grab the index into the channel vector.  This is available via:

# %%
myobj_from_dict.chan_idx('WindVxi')

# %% [markdown]
# ## Adding new channels, dropping channels, and math operations on channel data
# 
# Significant new capability has been added in pCrunch v2 to enable easy addition of new data channels, especially from mathematically manipulating existing channels.  There are also easy short cuts to add channels that are vector magnitudes and load rose sectors based on vector components, which is helpful for tower and blade loading analysis.
# 
# As with the constructor, new channel data can be added with a dictionary, list, Pandas Series, or Numpy array:

# %%
# Inputting a dictionary new channel
myobj_from_dict.add_channel( {'New1': np.sin(myobj_from_dict['Time'])} )

# As a DataFrame
myobj_from_dict.add_channel( pd.DataFrame({'New2': np.cos(myobj_from_dict['Time'])}) )

# As a Numpy array or list and channel as a string
myobj_from_dict.add_channel( np.tan(myobj_from_dict['Time']), 'New3' )

myobj_from_dict.to_df()

# %% [markdown]
# A new feature in pCrunch that restores some of the old capability in mcrunch is the ability to write string expressions to add a new channel.  String names should match channel names and all standard python math expressions are allowed.  Users can also use `calculate_channel` in addition to `add_channel` for mcrunch consistency.

# %%
myobj_from_dict.add_channel( 'WindVxi**2 + WindVyi + New1/New2', 'New4' )
myobj_from_dict.to_df()

# %% [markdown]
# Channels can also be dropped using string wildcards (`drop_channel`, `remove_channel`, and `delete_channel` are all valid)

# %%
myobj_from_dict.drop_channel('New*')
myobj_from_dict.to_df()

# %% [markdown]
# ### Derivatives with respect to time
# 
# As a common operation, new channels can be added that are gradients of existing channels.  This uses the Numpy `gradient` method with double precision central differencing in the middle of the timeseries and one-sided differencing at the edges.

# %%
myobj_from_dict.add_gradient_channel('WindVxi','du_dt')
myobj_from_dict.to_df()

# %% [markdown]
# ### Vector magnitudes
# 
# Computing vector magnitudes is a common operation, which can be done by hand using one of the approaches above, or in the constructor by passing in a dictionary:

# %%
mc = {"Wind": ["WindVxi", "WindVyi", "WindVzi"]}
myobj_with_mag = AeroelasticOutput(mydata, magnitude_channels=mc)
myobj_with_mag.to_df()

# %% [markdown]
# The magnitude channels can also be added after the fact too:

# %%
myobj_with_mag = AeroelasticOutput(mydata)
myobj_with_mag.add_magnitude_channels(mc)
myobj_with_mag.to_df()

# %% [markdown]
# ### Load Roses
# 
# Neither vector components nor magnitude correctly capture the load impacts on a tower base or blade root.  A more appropriate approach is a load rose, where the 360-degree annulus is divided into sectors and the vector components are combined with sin() and cos() to compute the load impacts on each sector.  pCrunch automates this process and it results in the creation of n_sector new channels of data.  An example:

# %%
lr = {'TwrBs': ['TwrBsFxt', 'TwrBsFyt']}
myobj_of_bin.add_load_rose(lr, nsec=6)
# myobj_of_bin.to_df()

# %% [markdown]
# ### Binning, windowing, averaging
# 
# Another common operation is to downsample the time series signals in various ways.  Options include:
# 
# - Trim the data to remove transients or otherwise narrow the series
# - Windowed smoothing via correlation
# - Binned averages

# %%
# Trimming data can be done to the full data set
print( "elapsed_time: ", myobj_of_bin.elapsed_time,
      " num_timesteps: ", myobj_of_bin.num_timesteps )
# trim data
print("After: Trim `self.data` to the data between `tmin` and `tmax`:")
myobj_of_bin.trim_data(100, 600)
print( "elapsed_time: ", myobj_of_bin.elapsed_time,
      " num_timesteps: ", myobj_of_bin.num_timesteps )

# %%[markdown]
# Time windowing convolves an averaging window with the time signal and sets this as the new data array with the same timestep, 
# but a shorter signal that covers the valid windowing region.
#%%
myobj_of_bin.time_averaging(30.0)
print( myobj_of_bin.elapsed_time, myobj_of_bin.num_timesteps, myobj_of_bin.dt)

# %%[markdown]
# Time binning results in a downsampled data set that represents the average for each bin
#%%
myobj_of_bin.time_binning(30.0)
print( myobj_of_bin.elapsed_time, myobj_of_bin.num_timesteps, myobj_of_bin.dt)

# %% [markdown]
# ## Frequency domain spectra
# 
# Power spectral density in the frequency domain is made readily available using the SciPy `welch` function.  A new AeroelasticOutput object is returned with frequency taking the place of time and PSD content in the frequency domain taking the place of the time-domain data.

# %%
freq_obj = myobj_of_ascii.psd()
plt.loglog(freq_obj['Freq'], freq_obj['TwrBsFyt'])
plt.xlabel('Frequency [Hz]')
plt.ylabel('PSD')
plt.grid()

# %% [markdown]
# The user can also adjust the length of the FFT operation by passing that in the `psd` function an integer value.  This is usually done to zero-pad the FFT to a length longer than the data vector.
# 
# Further operations on the frequency domain data are also possible, such as binning to achieve greater windowed smoothing than the `psd` function naturally gives (using the SciPy Welch algorithm with Hann-window smoothing).

# %% [markdown]
# ## Statistics, extremes, and many other quantities

# %%
# Many other statistics of the data are readily available. A quick summary for each channel of data is available in a dictionary
myobj_from_df.summary_stats()

# %%
myobj_from_df.summary_stats()['WindVxi']['mean']

# %%[markdown]
# It is helpful to know the value of other channels when one of interest is at its extreme value
# %%
myobj_from_df.extremes()

# %%[markdown]
# This can be done for the whole dataset (which can be a large NxN output), or specific channels
# %%
myobj_of_ascii.extremes(['RotTorq','TwrBsFyt'])

# %%[markdown]
# The extremes is done using the maximum value by default, but 'min' and 'absmax' are also available
# %%
myobj_from_df.extremes(stat='min')

# %%
myobj_of_ascii.extremes(['RotTorq','TwrBsFyt'], stat='absmax')

# %% [markdown]
# A larger laundry list of statistics are available as data properties (meaning they don't have to be called as a function):

# %%
# Indices to the minimum value for each channel
myobj_from_df.idxmins

# %%
# Indices to the maximum value for each channel
myobj_from_df.idxmaxs

# %%
# Minimum value of each channel
myobj_from_df.minima

# %%
# Maximum value of each channel
myobj_from_df.maxima

# %%
# Maximum value of absolute values of each channel
myobj_from_df.absmaxima

# %%
# The range of data values (max - min)
myobj_from_df.ranges

# %%
# Channel indices which vary in time
myobj_from_df.variable

# %%
# Channel indices which are constant in time
myobj_from_df.constant

# %%
# Sum of channel values over time
myobj_from_df.sums

# %%
# Sum of channel values over time to the second power
myobj_from_df.sums_squared

# %%
# Sum of channel values over time to the third power
myobj_from_df.sums_cubed

# %%
# Sum of channel values over time to the fourth power
myobj_from_df.sums_fourth

# %%
# Second moment of the timeseries for each channel
myobj_from_df.second_moments

# %%
# Third moment of the timeseries for each channel
myobj_from_df.third_moments

# %%
# Fourth moment of the timeseries for each channel
myobj_from_df.fourth_moments

# %%
# Mean of channel values over time
myobj_from_df.means

# %%
# Median of channel values over time
myobj_from_df.medians

# %%
# Standard deviation of channel values over time
myobj_from_df.stddevs

# %%
# Skew of channel values over time
myobj_from_df.skews

# %%
# Kurtosis of channel values over time
myobj_from_df.kurtosis

# %%
# Integration of channel values over time
myobj_from_df.integrated

# %%
# Special instance of the integration that specifically uses
# the Power channel string to integrate over time and calculate energy
myobj_of_ascii.compute_energy('GenPwr') 

# %%
# Total "travel" during a simulation, which is helpful for pitch and yaw systems
myobj_of_ascii.total_travel('BldPitch1') 

# %% [markdown]
# ## Calculating fatigue
# 
# pCrunch can compute damage equivalent loads and, optionally, traditional Palmgren-Miner damage.  Computing these quantities requires additional inputs for material properties, S-N curve parameters, and some algorithm choices (although most of the work is handed off to the `fatpack` module).  These additional parameters would most likely vary from one channel to the next.  For instance, blade composites will use different inputs than the structural steel in the tower or the fancy steel in the low-speed shaft.  To facilitate these additional inputs, pCrunch provides a `FatigueParams` class that both contains the necessary parameters and interfaces with `fatpack`.  Association between a load channel and a FatigueParams instance is done with a dictionary, similar to the magnitude channels.
# 
# Instead of using the same examples as above, here we'll build a couple of sinusoids to understand the numerics a bit better.  One sinusoid is centered at y=0 and the other at y=80kN.

# %% [markdown]
# ### The `FatigueParams` class
# 
# There are three ways to initialize a FatigueParams instance with an associated S-N curve in the `fatpack` library:
#         
# 1. Specify a curve from DNV-RP-C203, Fatigue in Offshore Steel Structures.
#    Input keywords are `dnv_type` = (one of) ['air', 'seawater', 'cathodic'],
#    `dnv_name` = (one of) [B1, B2, C, C1, C2, D, E, G F1, F3, G, W1, W2, W3], and
#    `units` = (such as) 'kPa' or 'MNm' to set the input units.
# 
# 3. Specify the slope of the S-N curve and a point on the curve.
#    Required keywords are `slope`, `Nc` and `Sc`.  Assumes a linear S-N curve.
#    Units are left to the user but must be consistent for all inputs.
# 
# 5. Specify the slope and the S-intercept point assuming a perflectly linear S-N curve
#    (which might not be the actual ultimate failure stress of the material).
#    Required keywords are `slope` and `S_intercept`.
#    Units are left to the user but must be consistent for all inputs.
# 

# %%
# Setting with curves found in Tables 2-1, 2-2, 2-4 from DNV-RP-C203 - Edition October 2024
myparam1 = FatigueParams(dnv_type='Air', dnv_name='D', units='kPa')
myparam2 = FatigueParams(load2stress=25.0, dnv_type='sea', dnv_name='c1', units='MPa')

# Also showing the other available keywords
myparam3 = FatigueParams(bins=256, goodman=True, ultimate_stress=1e6, dnv_type='cathodic', dnv_name='B2', units='N')

# Setting with slope and a known point, (Nc, Sc)
myparam4 = FatigueParams(Sc=2e7, Nc=2e6, slope=3)

# Setting with slope and the S-axis intercept
myparam5 = FatigueParams(ultimate_stress=1e6, slope=4) # Will use ultimate_stress as S_intercept
myparam6 = FatigueParams(ultimate_stress=1e6, slope=4, S_intercept=1e6)

# %% [markdown]
# ### Plotting the S-N surve
# 
# Once initialized, it can be helpful to plot the S-N curve to verify expected behavior.  This can be done by passing in a vector of values for N and plotting the resulting values of S.

# %%
NN = np.logspace(3,9,100)
plt.loglog(NN, myparam1.get_stress(NN),
          NN, myparam2.get_stress(NN),
          NN, myparam3.get_stress(NN),
          NN, myparam4.get_stress(NN),
          NN, myparam5.get_stress(NN),
          NN, myparam6.get_stress(NN))
plt.xlabel('Endurance (# of cycles)')
plt.ylabel('Stress [Pa]')
plt.legend([str(m+1) for m in range(6)])
plt.grid()

# %% [markdown]
# ### Fatigue examples
# 
# Time-series channel history can be passed directly to the FatigueParams instances to compute damage equivalent loads (DELs) and Palmgren-Miner damage.  Note that the DELs (and damage) are computed to an equivalent 1 Hz constant cyclic load.

# %%
# Compute DELs
dels = myparam1.compute_del(myobj_of_ascii['TwrBsFyt'], myobj_of_ascii.elapsed_time)

# Compute Damage
dams = myparam1.compute_damage(myobj_of_ascii['TwrBsFyt'])

# Can also override the algorithmic options, such as number of bins and the Goodman correction
dels2 = myparam1.compute_del(myobj_of_ascii['TwrBsFyt'], myobj_of_ascii.elapsed_time, bins=50, goodman=True)
dams2 = myparam1.compute_damage(myobj_of_ascii['TwrBsFyt'], bins=200, goodman=True)
print(dels, dels2, dams, dams2)

# %% [markdown]
# A more helpful approach is usually to drive the fatigue calculations from the AeroelasticOutput object directly.  This next example does just that and also demonstrates some of the trends involved as the number of cycles and the amplitude of cycles changes.

# %%
# Build a FatigueParams instance that we'll use for all channels
myparam = FatigueParams(load2stress = 25.0,          # Factor based on cross-section to convert channel force/moment to stress
                        slope = 3.0,                 # Slope of S-N curve
                        ultimate_stress = 6e8,       # Yield stress of the material
                        S_intercept = 5e9,           # S-intercept on S-N curve (catastrophic load amplitude for 1 cycle)
                        goodman_correction = False,  # Apply Goodman correction for mean load value?
                        )

# Our time series
t   = np.linspace(0, 600, 10000)

# Sinusoids centered at 0 and 80kN, with amplitude of 80kN
y0  = 80e3 * np.sin(2*np.pi*t/60.0) # Will have +/- values
y80 = y0 + 80e3                     # All + values
zeros = np.zeros(y0.shape)

# Simple dictionary for AeroelasticOutput instance
mydata = {"Time":t,
          "Signal0":y0,
          "Signal80":y80,
          "Zeros":zeros}

# Magnitude channels (in this case, just an absolute value operation on the sinusoids)
mymagnitudes = {"Mag0":["Signal0", "Zeros"],
                "Mag80":["Signal80", "Zeros"]}

# The channels we will be computing fatigue on
myfatigues = {"Signal0":myparam,
              "Signal80":myparam,
              "Mag0":myparam,
              "Mag80":myparam}

# Create the instance
myobj = AeroelasticOutput(mydata, magnitude_channels=mymagnitudes, fatigue_channels=myfatigues)

# Loop over channels and pass in channel-specific fatigue parameters
dels, dams = myobj.get_DELs(return_damage = True)

# Organize the output into a table
pd.concat((pd.DataFrame(dels, index=['DELs']), pd.DataFrame(dams, index=['Damage'])))

# %% [markdown]
# A couple of points to highlight in the results:
# 
# - The Signal0 and Signal80 have the same DEL and Damage values because the amplitude of the variations are equivalent
# - Compare the DEL value to the analytically computed value of (10*(160000^3)/600)^(1/3) = 40869.8
# - The Mag80 signal is also equivalent because the signal is unchanged by the magnitude operation
# - The Mag0 signal has noticeably less fatigue accumulation.  This is because by taking the absolute value of the signal centered at zero, we have doubled the frequency but halved the amplitude.  These effects combine in nonlinear ways, but the net result is a drop in fatigue accumulation.
#   
# Now let's add the Goodman Correction, which should calculate additional fatigue impacts based on the mean value of the signals, not just the amplitude of variation.  We can do this by either regenerating a new FatigueParams instance with the Goodman flag set to True, or pass in a keyword to the `compute_del` function that overrides the inputs.

# %%
dels2, dams2 = myobj.get_DELs(goodman=True)

pd.concat((pd.DataFrame(dels, index=['DELs']), pd.DataFrame(dels2, index=['DELs-Goodman']), pd.DataFrame(dams, index=['Damage']), pd.DataFrame(dams2, index=['Damage-Goodman'])))    

# %% [markdown]
# As expected, there is now a difference between Signal0 and Signal80 in the Goodman columns because of the higher mean loads in the Signal80 case.

# %% [markdown]
# ### Plotting the rainflow results
# 
# For debugging purposes, the rainflow bin counts and values can also be obtained directly and plotted.

# %%
# Actual timeseries examples
Nf, Sf = myparam1.get_rainflow_counts(myobj_of_ascii['TwrBsFyt'], 100)
plt.bar(Sf, Nf)
plt.xlabel('Stress cycle amplitude bin [kN]')
plt.ylabel('Rainflow count')

# %%
# From toy problem with single sinusoid, there are 10 cycles in the time period at a single amplitude
Nf, Sf = myparam.get_rainflow_counts(myobj['Signal80'], 100)
plt.bar(Sf*1e-3, Nf)
plt.xlabel('Stress cycle amplitude bin [kN]')
plt.ylabel('Rainflow count')

# %% [markdown]
# The Rainflow Matrix, also known as the Markov Matrix, which is a heatmap of the rainflow counting of means and amplitude ranges can be obtained and easily plotted.

# %%
# Use an timeseries examples, with a smaller number of bins for plotting
Z, X, Y = myparam1.get_rainflow_matrix(myobj_of_ascii['TwrBsFyt'], 10)
C = plt.pcolormesh(X, Y, Z, cmap='jet')
plt.colorbar(C)
plt.title("Rainflow matrix counts")
plt.ylabel("Mean Value")
plt.xlabel("Amplitude Range")

# %% [markdown]
# ## Saving and Loading Data
# 
# The timeseries and channel data can be saved and loaded from a file.  The supporting data structures, such as `magnitude_channels` or `fatigue_channels` are not saved or loaded (yet).

# %%
myobj_from_dict.save('myfile.p')
myobj_copy = AeroelasticOutput()
myobj_copy.load('myfile.p')
myobj_copy.to_df()

#%%
