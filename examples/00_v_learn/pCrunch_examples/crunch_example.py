# %% [markdown]
# # pCrunch's Crunch class
# 
# The `Crunch` class is a general analysis tool for batches of time-series based data across multiple environmental conditions (i.e., a full wind speed and turbulence seed sweep). The methods are agnostic to the aeroelastic multibody simulation tool (OpenFAST or HAWC2 or Bladed or QBlade or in-house equivalents). The `AeroelasticOutput` class provides the data containers for each individual simulation.  The `AeroelasticOutput` class provides many analysis capabilities and the `Crunch` class extends them into their batch versions.
# 
# The `Crunch` class supports keeping all time series data in memory and a lean "streaming" version where outputs are processed and then deleted, retaining only the critical statistics and analysis outputs.
# 
# This file lays out some workflows and showcases capabilities of the `Crunch` class.  It is probably best to walk through the examples of the `AeroelasticOutput` class first.

# %% [markdown]
# ## Creating a new class instance
# 
# The `Crunch` class can be initialized from a list of AeroelasticOutput instances or none, in order to setup a "streaming" analysis.  Pleaes see the AeroelasticOutput example for the various means to initialize one of its instances.  pCrunch provides a reader for OpenFAST output files (both binary and ascii) and common Python data structures are also supported.  To extend pCrunch for use with other aeroelastic multibody codes, users could simply use the `openfast_readers.py` file as a template.  Here are some examples:

# %%
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pCrunch import Crunch, read, FatigueParams, __file__

dir_pcrunch = os.path.dirname(os.path.abspath(__file__))
datadir = os.path.join(dir_pcrunch, 'test', 'data')

# OpenFAST output files
filelist1 = glob.glob( os.path.join(datadir, '*.out') )
filelist1.sort()
filelist2 = glob.glob( os.path.join(datadir, 'DLC1p1', '*.outb') )
filelist2.sort()
print(f"Found {len(filelist1)} and {len(filelist2)} files.")

# Read all outputs into a list
outputs1 = [read(m) for m in filelist1[1:]]
outputs2 = [read(m) for m in filelist2]

# Vector magnitudes
mc = {
    "RootMc1": ["RootMxc1", "RootMyc1", "RootMzc1"],
    "RootMc2": ["RootMxc2", "RootMyc2", "RootMzc2"],
    "RootMc3": ["RootMxc3", "RootMyc3", "RootMzc3"],
}

# Channel-specific fatigue properties
fc = {
    "RootMc1": FatigueParams(slope=10.0, ultimate_stress=6e6, load2stress=5e2, S_intercept=5e7),
    "RootMc2": FatigueParams(slope=10.0, ultimate_stress=6e6, load2stress=5e2, S_intercept=5e7),
    "RootMc3": FatigueParams(slope=10.0, ultimate_stress=6e6, load2stress=5e2, S_intercept=5e7),
}

# Channels to focus on for extreme event tabulation
ec = ["RotSpeed", "RotThrust", "RotTorq"]

# Standard use case with all outputs read prior to use of Crunch.
mycruncher = Crunch(outputs1)

# Can also add some batch data operations in the constructor (many more available in Batch Processing below)
mycruncher_mc = Crunch(outputs2, magnitude_channels=mc, trim_data=[2, 8], fatigue_channels=fc, extreme_channels=ec)

# When planning on adding outputs later, you still need create a Crunch object that is initially empty of data
# The `lean` flag says that the outputs should be processed, but not stored in memory
mycruncher_lean = Crunch(outputs=[], lean=True)

# Can still add the batch operations to be done later when outputs are added
mycruncher_lean_mc = Crunch(outputs=[], lean=True, magnitude_channels=mc, trim_data=[2,8], fatigue_channels=fc, extreme_channels=ec)

# %% [markdown]
# ## Crunching the data
# 
# ### With full memory storage
# The Crunch class can batch process the outputs using one or more processors up to the number of available workstation cores.  This computes the essential statistics for each output.

# %%
# Process all outputs in parallel
mycruncher.process_outputs(cores=1)

# Process all outputs and override any prior input setting (especially in fatigue calculation)
mycruncher_mc.process_outputs(compute_damage=True)

# %% [markdown]
# The key outputs that are stacked together for each output are:
# 
# - Summary statistics
# - Load ranking
# - Extreme event table
# - Damage equivalent loads (DELs)
# - Palmgren-Miner damage

# %%
# The summary stats per each file are here:
mycruncher.summary_stats

# %%
# These are indexable by channel, stat:
mycruncher_mc.summary_stats["RootMc1"]

# %%
mycruncher_mc.summary_stats["RootMc1"]['min']

# %%
# Or by file
mycruncher.summary_stats.loc["DLC2.3_2.out"]

# %%
# Load rankings are manipulations of the summary statistics table
# All channels and statistics are available
mycruncher_mc.get_load_rankings(['RootMc1'],['max'])

# %%
# Damage equivalent loads are found here:
mycruncher_mc.dels

# %%
# Palmgren-Miner damage can be viewed with (although it is not computed without a `return_damage=True`
mycruncher_mc.damage

# %%
# Extreme events table. For each channel, there is a list of the extreme condition for each output case
mycruncher.extremes

# %% [markdown]
# ### Crunching in "lean / streaming" mode
# 
# If operating in "lean / streaming" mode, the outputs can either be processed one at a time, or even more lean, the summary statistics themselves can be passed to the `cruncher` object to append to the running list.

# %%
# Adding AeroelasticOutput objects in lean / streaming mode
for iout in outputs1:
    mycruncher_lean.add_output( iout ) # Each output is processed without retaining the full time series

# Adding statistics incrementally
results_pool = []
for iout in outputs2:
    iresults = mycruncher_lean_mc.process_single( iout ) # This could be the result of parallelized function
    results_pool.append( iresults )

# After parallel processing is complete, assemble all the statistic for batch analysis
for iresults in results_pool:
    fname, stats, extremes, dels, damage =  iresults
    mycruncher_lean_mc.add_output_stats(fname, stats, extremes, dels, damage)

# %%
# Results are the same as the full-memory approach above
mycruncher_lean_mc.summary_stats["RootMc1"]['min']

# %%
mycruncher_lean_mc.dels

# %% [markdown]
# ## Integrating outputs with a probability weighting (AEP, Damage, etc)
# 
# When running design load cases, not all windspeeds, or other environmental condition, occur with equal likelihood.  pCrunch provides a way to assign a probability to each output.  This probability can then weight a summation to compute annual energy production (AEP), or sum all Palmgren-Miner damages together.  Using a subset of the outputs is also a provided capability.
# 
# pCrunch provides a couple different ways to set the probabilities, either:
# - Inflow wind speed using a Weibull or Rayleigh distribution for the site
# - IEC turbine class with different average wind speeds that define a Weibull distribution
# - Users can set the probability values directly.

# %%
# Set probability based on wind speed channel name, Weibull distribution average of 7.5 m/s (shape factor input optional)
mycruncher.set_probability_wind_distribution('WindVxi', 7.5, kind='weibull', weibull_k=2.0)

# Or Rayleigh distribution using the same distribution average of 7.5 m/s
mycruncher.set_probability_wind_distribution('WindVxi', 7.5, kind='rayleigh')

# If you only want to use some of the outputs, but not all of them
mycruncher.set_probability_wind_distribution('WindVxi', 7.5, kind='weibull', idx=[0,2])

# If you would rather specify the inflow wind speed directly to use in the probability distribution
mycruncher.set_probability_wind_distribution([8,10,12], 7.5, kind='weibull')

# Can also set the probability based on IEC turbine class, again using a channel name of user input of wind speeds
mycruncher.set_probability_turbine_class('WindVxi', 2)
mycruncher.set_probability_turbine_class([8,10,12], 2)

# A savvy user can set the probability values directly (they will be rescaled to sum to one no matter what)
mycruncher.prob = np.array([0.1, 0.5, 0.4])

# A user can also set their own probability vs. wind speed values
mycruncher.set_probability_wind_distribution([8,10,12], 10., kind='user', v_prob=[4,12,24], probability=[0.1,0.4,0.1])
mycruncher.prob




# %% [markdown]
# ### Computing AEP
# 
# Once the probabilities are set, the user can use them to calculate AEP or total fatigue accumulation across the scenarios represented by each output.  For the AEP calculation, the user must specify the channel name.  Additional loss factors or restriction to certain indices are optional inputs.

# %%
# Probability weighted and unweighted AEP values are returned in kWh
mycruncher_mc.set_probability_turbine_class('Wind1VelX', 2)
mycruncher_mc.compute_aep('GenPwr')

# %%
# Or with loss factors and restricted by select outputs
mycruncher.compute_aep('GenPwr', loss_factor=0.15, idx=[0,2])

# %% [markdown]
# ### Computing lifetime damage and summary DELs
# 
# pCrunch computes a summary damage equivalent load (DEL) and Palmgren-Miner lifetime damage based on the outputs in the list.  For the summary DELs, there is an optional input, `idx` that can be used to select the correct outputs.  For the damage calculation, in addition to `lifetime` scaling, there is an allowance for operational runs with `availability`, parked rotor simulations for downtime with `idx_park` scaled with `(1 - availability)`, and expected number of fault events in a lifetime with `idx_fault` and `n_fault`.
# All optional inputs are valid for the damage calculation.
# 
# The `process_outputs` function shuld be run before this if the output statisctics were not added in streaming mode.

# %%
# Damage calculation does not require a channel name, as it uses the previously computed case-specific and channel-specific values.
dels_tot, dams_tot = mycruncher_mc.compute_total_fatigue(lifetime=30.0, availability=0.9)

# %%
dels_tot

# %%
dams_tot

# %%
# Select indices are also available to restrict the summation
dels_tot, dams_tot = mycruncher_mc.compute_total_fatigue(lifetime=30.0, availability=0.9, idx=[0,2])

# %% [markdown]
# ## Other Batch Procressing
# 
# The Crunch class provides batch extensions of nearly all of the operations offered in the AeroelasticOutputs class.  This includes the add channel or drop channel utilities and all statistical functions.  For the statistics, unlike the AeroelasticOutput class, these batch versions are functions, not data properties.  The result is returned as a list, with each index corresponding to the output list.  Many of these statistics also vary by channel, so there are likely to be nested lists.  Also, some are unavailable in "lean / streaming" mode.

# %%
# Adding channel
mycruncher.calculate_channel('LSSGagMya + LSSGagMza', 'Test')

# Adding Load Roses
lr = {'TwrBs': ['TwrBsFxt', 'TwrBsFyt']}
mycruncher.add_load_rose(lr, nsec=6)

# Dropping channels by string wildcard
mycruncher.drop_channel('Fair*')
mycruncher.drop_channel('Anch*')
mycruncher.drop_channel('Spn*')
mycruncher.drop_channel('Root*')
mycruncher.drop_channel('Wave*')
mycruncher.drop_channel('Ptfm*')
mycruncher.drop_channel('Tw*')
mycruncher.drop_channel('Yaw*')

# %%
# Indices to the minimum value for each channel
mycruncher.idxmins()

# %%
# Indices to the maximum value for each channel
mycruncher.idxmaxs()

# %%
# Minimum value of each channel
mycruncher.minima()

# %%
# Maximum value of each channel
mycruncher.maxima()

# %%
# Maximum value of absolute values of each channel
mycruncher.absmaxima()

# %%
# The range of data values (max - min)
mycruncher.ranges()

# %%
# Channel indices which vary in time
mycruncher.variable()

# %%
# Channel indices which are constant in time
mycruncher.constant()

# %%
# Sum of channel values over time
mycruncher.sums()

# %%
# Sum of channel values over time to the second power
mycruncher.sums_squared()

# %%
# Sum of channel values over time to the third power
mycruncher.sums_cubed()

# %%
# Sum of channel values over time to the fourth power
mycruncher.sums_fourth()

# %%
# Second moment of the timeseries for each channel
mycruncher.second_moments()

# %%
# Third moment of the timeseries for each channel
mycruncher.third_moments()

# %%
# Fourth moment of the timeseries for each channel
mycruncher.fourth_moments()

# %%
# Mean of channel values over time
mycruncher.means()

# %%
# Median of channel values over time
mycruncher.medians()

# %%
# Standard deviation of channel values over time
mycruncher.stddevs()

# %%
# Skew of channel values over time
mycruncher.skews()

# %%
# Kurtosis of channel values over time
mycruncher.kurtosis()

# %%
# Integration of channel values over time
mycruncher.integrated()

# %%
# Special instance of the integration that specifically uses
# the Power channel string to integrate over time and calculate energy
mycruncher.compute_energy('GenPwr')

# %%
# Total travel across simulation- useful for pitch drives and yaw drivers
mycruncher.total_travel('BldPitch1')


