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

# Evaluate the system properties and equilibrium position before loads are applied
model.analyzeUnloaded()

# %%
# "resuls" dict: RAFT saves all its output data in a “results” dictionary that is a member of the Model class
results = model.results
for key,_ in results.items(): print(key)

## PSDs of load cases stored as such, for the 1st turbine [0], 1st load case [0]
# results['case_metrics'][0][0]
results["response"]

#%%
# 1. static properties

# Important checks:
# C33 > 0 (heave restoring)
# C55 > 0 (pitch restoring)
# CG below/near waterplane for stability

fowt = model.fowtList[0]
print("Mass:", fowt.M_struc[0,0])
print("CG:", fowt.rCG)
print("Hydrostatic stiffness:\n", fowt.C_hydro)

fowt.ms.getCoupledStiffness()

# %%
# 2. mean resp to steady loads
model.analyzeCases(display=1) # TODO: or analyzeLoads()

print(model.results['mean_offsets'])

# This gives:

# mean surge / sway / heave
# mean pitch / roll
# contributions from:

# wind
# current
# wave drift (if included)

#%%
# 3. Compute natural frequencies and mode shapes
model.solveEigen()

print(model.results['eigen'])

# If any mode:

# is zero → missing stiffness
# is very high → over-stiff proxy matrix

#%%
# 4. Dynamic response (RAOs / motions)
model.solveDynamics() # TODO

results = model.results['dynamic']

# Typical contents:

# RAOs (motion amplitude vs frequency)
# platform motions (complex values)

freq = results['freq']
surge_RAO = results['RAO'][0]   # DOF 0 = surge
pitch_RAO = results['RAO'][4]

#%%
# 5. Plot responses

model.plotResponses()
plt.show()

# %%
