#%%
"""
This example shows how to use the Design of Experiments (DOE) driver within
WEIS including OpenFAST.

Specifically, the DOE driver helps sample the design space of a problem, allowing
you to perform parameter sweeps or random samples of design variables. This is
useful for better understanding a design space, especially prior to running optimization.
The DOE driver is not an optimizer, but simply runs the cases prescribed.
Check out the `driver` section within the `analysis_options.yaml` for the
DOE driver settings.
"""

import os
import sys
from weis import weis_main
from wisdem.inputs.validation import load_yaml
#%%
## File management
run_dir                = os.path.dirname( os.path.realpath(__file__) ) + os.sep
basecase_dir           = os.path.join(run_dir, "..", "..", "04_frequency_domain_analysis_design","M4W_01_base_case_UN_TLPwamit")

fname_wt_input         = os.path.join(basecase_dir, "prac_IEA-15-VolturnUS_rect.yaml")
fname_modeling_options = os.path.join(basecase_dir, "modelOpts.yaml")
fname_analysis_options = os.path.join(run_dir, "m4w_01_raft_doe_analysis.yaml")

#%%
if True:
    wt_opt, modeling_options, opt_options = weis_main(fname_wt_input,
                                                  fname_modeling_options,
                                                  fname_analysis_options)

#%%
# Post-processing

# dir
dict_modelOpts = load_yaml(fname_analysis_options)
dir_sql_outputs = os.path.join(
    run_dir,
    dict_modelOpts['general']['folder_output']
)

post_multi=True

#%%
# save to csv, in parallel
sys.path.insert(0,"..")
from postprocess_results import save_csv_of_parametric_runs

if __name__ == "__main__":
    save_csv_of_parametric_runs(post_multi, dir_sql_outputs)

# %%
