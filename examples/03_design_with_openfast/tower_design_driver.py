#%%
import os
from weis import weis_main

# TEST_RUN will reduce the number and duration of simulations
TEST_RUN = False
#%%
## File management
run_dir = os.path.dirname( os.path.realpath(__file__) )
fname_wt_input = os.path.join(run_dir, "..", "00_setup", "ref_turbines", "IEA-15-240-RWT_VolturnUS-S_sparsetower.yaml")
fname_modeling_options = os.path.join(run_dir, "tower_design_modeling.yaml")
fname_analysis_options = os.path.join(run_dir, "tower_design_analysis.yaml")

wt_opt, modeling_options, opt_options = weis_main(fname_wt_input, 
                                                 fname_modeling_options, 
                                                 fname_analysis_options,
                                                 test_run=TEST_RUN
                                                 )
# TODO: dzalkind issue #471 (error in FASTLoacCases):
# - I suggest you review the openfast outputs of the last runs.
# - I've seen that error for short and steady state simulations, but thought
# - it was resolved in the latest version of pcrunch.

# %%
