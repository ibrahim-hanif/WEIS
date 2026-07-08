#%%
# example script for running RAFT with second-order loads computed internally with the slender-body approximation based on Rainey's equation
# (copy of oc4semi-WAMIT_Coefs.py)
import numpy as np
import matplotlib.pyplot as plt
import yaml
import raft
import os
import os.path as path
#%%
# open the design YAML file and parse it into a dictionary for passing to raft
flNm = 'M4W-base_case-TLPwamit-mooringGeo'
current_dir = os.path.dirname(os.path.abspath(__file__))
flPath = path.join(current_dir, flNm + '.yaml')
with open(flPath) as file:
    design = yaml.load(file, Loader=yaml.FullLoader)
#%%
# Create the RAFT model (will set up all model objects based on the design dict)
model = raft.Model(design)

#%%
# 1. static properties

# Important checks:
# C33 > 0 (heave restoring)
# C55 > 0 (pitch restoring)
# CG below/near waterplane for stability

# 1a. Evaluate the system properties and equilibrium position before loads are applied
model.analyzeUnloaded()

fowt = model.fowtList[0]
print("\n Mass:", fowt.M_struc[0,0])
print("\n CG:", fowt.rCG)
# --- stiffnesses
C_hydro = fowt.C_hydro
print("\n Hydrostatic stiffness:\n", C_hydro)
print("\n - K44, K55 (RAFT) * 1e9: ", C_hydro[3,3]/1e9, C_hydro[4,4]/1e9) # index starts at 0,0 
print("\n - K44 or K55 (acciona) * 1e9: ", ((2*np.pi/3.9)**2) * 7.98e9 / 1e9 )

print("\n Mooring stiffness:\n", fowt.C_moor)
print("\n Coupled stiffness:\n", fowt.ms.getCoupledStiffness())
T_moor = fowt.ms.getTensions()
print(" \n Mooring tension @ fairleads (kN): \n", T_moor[:8]/1e3 )
print(" \n Mooring tension @ anchors (kN): \n", T_moor[8:]/1e3 )

# How-to parse the results dict
"""
# "resuls" dict: RAFT saves all its output data in a “results” dictionary that is a member of the Model class
results = model.results
for key,_ in results.items(): print(key)

# PSDs of load cases stored as such, for the 1st turbine [0], 1st load case [0]
results['case_metrics'][0][0]
results["response"]
"""

#%%
# 1b. static (mass, CG) properties and print
model.calcOutputs()

results = model.results
print("\n Model properties:")
results['properties']

# %%
# 2. Compute natural frequencies and mode shapes of the system
# - includes mooring stiffness and added mass effects
model.solveEigen()
# ---- post process
print("\n Eigen-solutions are: \n", model.results['eigen'])
freq_eigen = model.results['eigen']['frequencies']
modes_eigen = model.results['eigen']['modes']
naturalPeriods = 1 / freq_eigen
print("\n Natural periods:\n", naturalPeriods)

# If any mode:

# is zero → missing stiffness
# is very high → over-stiff proxy matrix

#%%
# 3. mean resp to steady loads
model.analyzeCases(display=1, RAO_plot=True) # TODO: or analyzeLoads()

print(model.results['mean_offsets'])

# This gives:

# mean surge / sway / heave
# mean pitch / roll
# contributions from:

# wind
# current
# wave drift (if included)

#%%
"""
# 4. Dynamic response (RAOs / motions) || used inside analyseCases()
model.solveDynamics() # TODO

results = model.results['dynamic']

# Typical contents:

# RAOs (motion amplitude vs frequency)
# platform motions (complex values)

freq = results['freq']
surge_RAO = results['RAO'][0]   # DOF 0 = surge
pitch_RAO = results['RAO'][4]
"""

#%%
# 5. Plot responses

model.plotResponses()
plt.show()

# %%
# Visualize the system in its most recently evaluated mean offset position
wd = 265 # water depth

model.plot(
    xbounds=[-wd,wd], ybounds=[-wd,wd],zbounds=[-wd,wd],
    plot_water=True,plot_frame=True
)
# model.plot(plot_frame=True) # flag plot_frame is used to plot the structural nodes and rigid links that are part of the structure. The default is False
plt.show()

# %%
