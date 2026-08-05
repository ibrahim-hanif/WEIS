#%%[markdown]
# TODO:
# 1. DONE: how to incl point_inertia (as in raft yaml)
# 2. DONE: final weis geo yaml matching raft
# 3. TODO: DLCs in the modeling options

#%%
import os
from weis import weis_main
from wisdem.inputs.validation import load_yaml
#%%
# TEST_RUN will reduce the number and duration of simulations
TEST_RUN = False # TODO
flag_GBO = False # TODO

wt_m4w = False # turbine to analyse: True = m4w / False = iea15mw

#%%
## File management
run_dir = os.path.dirname( os.path.abspath(__file__) )
# -- geometry
if wt_m4w: geo_input = "geometryOpt.yaml"
else: geo_input = "prac_IEA-15-VolturnUS_rect.yaml"
fname_wt_input = os.path.join(run_dir, geo_input)
# -- modelling
fname_modeling_options = os.path.join(run_dir, "modelOpts.yaml")
# -- analysis
if flag_GBO:
    fname_analysis_options = os.path.join(run_dir, "analysisOpt.yaml")
else:
    fname_analysis_options = os.path.join(run_dir, "analysisNOopt.yaml")

#%%
# run WEIS
wt_opt, modeling_options, opt_options = weis_main(fname_wt_input, 
                                                 fname_modeling_options, 
                                                 fname_analysis_options,
                                                 test_run=TEST_RUN
                                                 )

#%%
# Test that the input we are providing RAFT has not changed
this_raft_input = load_yaml(
    os.path.join(run_dir,"outputs","raft_designs","raft_design_0.yaml")
    )
standard_raft_input = load_yaml(
    os.path.join(run_dir, "..", "M4W_00_learn_raft","TLP_Acciona","M4W-base_case-TLPwamit-mooringGeo.yaml")
    )
# Disable this test because we get slightly different inputs on the linux CI
assert(this_raft_input == standard_raft_input)

# If the values have changed for a purpose, move this_raft_input to standard_raft_input and commit
# %%
