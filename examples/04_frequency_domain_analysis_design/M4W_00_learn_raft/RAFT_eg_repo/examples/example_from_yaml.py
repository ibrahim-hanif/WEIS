#%%
# # example script for running RAFT from a YAML input file

import sys
import matplotlib.pyplot as plt
import yaml
import raft
#%%
def run_example(plot_flag = False):
    # open the design YAML file and parse it into a dictionary for passing to raft
    with open('VolturnUS-S_example.yaml') as file:
        design = yaml.load(file, Loader=yaml.FullLoader)

    # Create the RAFT model (will set up all model objects based on the design dict)
    model = raft.Model(design)  

    # Evaluate the system static properties and equilibrium position before loads are applied
    # - static props: weight, mass, hydrostatics, and linearized mooring force and stiffness, about the system’s equilibrium position
    model.analyzeUnloaded()

    # Compute natural frequencies and mode shapes
    model.solveEigen()

    # Dynamic response simulation of the different load cases
    model.analyzeCases(display=1) # (display metrics on)

    if plot_flag:
        # Plot the power spectral densities from the load cases
        model.plotResponses()

        # Visualize the system in its most recently evaluated mean offset position
        model.plot(plot_frame=True) # flag plot_frame is used to plot the structural nodes and rigid links that are part of the structure. The default is False

        plt.show()

    return model
#%%
if __name__ == "__main__":
    if len(sys.argv) == 2:
        plot_flag = sys.argv[1].lower() in ["1", "t", "true", "y", "yes", 1, True]
    elif len(sys.argv) == 1:
        plot_flag = True
    else:
        print("Usage: python example_from_yaml.py <True/False>")
        print("  The last argument is an optional declaration to show or suppress the plots (default is True)")
        
    model = run_example(plot_flag = True) # plot_flag ; def above
        
# %%
# "resuls" dict: RAFT saves all its output data in a “results” dictionary that is a member of the Model class
results = model.results
for key,_ in results.items(): print(key)

## PSDs of load cases stored as such, for the 1st turbine [0], 1st load case [0]
# results['case_metrics'][0][0]

# %%
