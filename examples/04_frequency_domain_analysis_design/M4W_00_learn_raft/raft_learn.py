#%%
import raft
import yaml
import os

#%%
# File management
dir_this = os.path.dirname( os.path.abspath(__file__) )
dir_RAFT_RefDesigns = os.path.join( dir_this,"ReferenceDesigns_TLP","RAFT")
yaml_tlp_200m = os.path.join( dir_RAFT_RefDesigns,"NREL_15MW_TLP_200m.yaml")

dir_04eg = os.path.dirname( dir_this )
raft_04_umaine = os.path.join(dir_04eg, "outputs",
    "04_umaine_semi_raft_opt","raft_designs","raft_design_0.yaml")

#%%
# open the design YAML file and parse it into a dictionary for passing to raft
with open( yaml_tlp_200m ) as file:
        design = yaml.load(file, Loader=yaml.FullLoader)
#%%
# Create the RAFT model (will set up all model objects based on the design dict)
model = raft.Model(design)
#%%
# Evaluate the system properties and equilibrium position before loads are applied
model.analyzeUnloaded()
#%%
# Compute natural frequencies
model.solveEigen()
#%%
# Simule the different load cases
model.analyzeCases(display=1)
#%%
# Plot the power spectral densities from the load cases
model.plotResponses()
#%%
# Visualize the system in its most recently evaluated mean offset position
model.plot(hideGrid=False) # True gives Error
#%%
