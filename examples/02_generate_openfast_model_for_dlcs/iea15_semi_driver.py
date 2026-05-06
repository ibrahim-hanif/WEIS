#%%
import os
from weis import weis_main
#%%
# TEST_RUN will reduce the number and duration of simulations
TEST_RUN = False

## File management
run_dir = os.path.dirname( os.path.realpath(__file__) )
fname_wt_input = os.path.join(run_dir, "..", "00_setup", "ref_turbines", "IEA-15-240-RWT_VolturnUS-S_rectangular.yaml")
fname_analysis_options = os.path.join(run_dir, "iea15_semi_analysis.yaml")


analysis_override = {}
analysis_override["general"] = {}
#%%
# Option 1: Strip theory model
analysis_override["general"]["folder_output"] = "outputs/02_iea15_semi/0_strip_theory_modeling"

fname_modeling_options = os.path.join(run_dir, "iea15_semi_modeling_strip.yaml")
wt_opt, modeling_options, opt_options = weis_main(fname_wt_input, 
                                                 fname_modeling_options, 
                                                 fname_analysis_options,
                                                 test_run=TEST_RUN,
                                                 analysis_override=analysis_override
                                                 )
#(v) dzaklind issue #471 (takes 22 hours to run!):
# - it's running SubDyn, which can resolve internal platform loads, but takes a long time to simulate.

#%%
# Option 2: Hybrid model (strip theory + potential flow)
analysis_override["general"]["folder_output"] = "outputs/02_iea15_semi/1_hybrid_modeling"
fname_modeling_options = os.path.join(run_dir, "iea15_semi_modeling_hybrid.yaml")
wt_opt, modeling_options, opt_options = weis_main(fname_wt_input, 
                                                 fname_modeling_options, 
                                                 fname_analysis_options,
                                                 test_run=TEST_RUN,
                                                 analysis_override=analysis_override
                                                 )
#%%