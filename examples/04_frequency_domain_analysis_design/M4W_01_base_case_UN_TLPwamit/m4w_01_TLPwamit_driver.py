#%%[markdown]
# TODO:
# 1. DONE: how to incl point_inertia (as in raft yaml)
# 2. DONE: final weis geo yaml matching raft
# 3. TODO: DLCs in the modeling options

#%%
import os
from weis import weis_main
from wisdem.inputs.validation import load_yaml

import matplotlib.pyplot as plt

from Drive4Wind.post_processing.color_schemes import plot_rcParams_update, loc_clr_scheme_m4w, read_color_scheme
clrs_m4w = read_color_scheme( loc_clr_scheme_m4w )

#%%
# TEST_RUN will reduce the number and duration of simulations
TEST_RUN = False

flag_GBO = False

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

# %%[markdown]
# Post-process
#%%
# directories
dict_analy = load_yaml(fname_analysis_options)
folder_results = dict_analy["general"]["folder_output"]
csv_name = dict_analy["general"]["fname_output"] + ".csv"
csv_file = os.path.join( run_dir, folder_results, csv_name )

# plt.rcParams.update( plot_rcParams_update )
linewidth = 3
params_plot_rc = {
        "font.size": 24,
        "axes.labelsize": 24,
        "legend.fontsize": 24, # 16 for pdf of `var_with_iter` plot
        "lines.linewidth": linewidth,
        "lines.markersize": 10, #linewidth*3,
    }
plt.rcParams.update( params_plot_rc )

#%%
# Drivetrain utilities
from Drive4Wind.utilities.utilities_drivetrain import plot_drivetrain_constraints

lst_DTconstrs = [
    "constr_lss_vonmises", "constr_bedplate_vonmises",
    "constr_shaft_deflection", "constr_shaft_angle",
    "constr_mb1_defl", "constr_mb2_defl",
    "constr_stator_deflection", "constr_stator_angle"]
fig_DTconstrs, ax_DTconstrs = plot_drivetrain_constraints(
    csv_file,lst_constrs=lst_DTconstrs,flag_WTnamespace=True)

# save
if False: #flag_save_plots:
    path_plot_dt_constr = os.path.join(
        run_dir, folder_results, "iea15_DT_constrs.pdf" )
    fig_DTconstrs.savefig( path_plot_dt_constr )

# fig_DTconstrs

#%%
# Tower constraints
from Drive4Wind.utilities.plot_tower_data import plot_tower_constraints_stress_utils

fig_TowerConstrs, ax = plot_tower_constraints_stress_utils(
    csv_file,
    figsize=(5.0,10.0),
    colors=["tab:blue","tab:green","tab:red"]
)

if False: #flag_save_plots: 
    path_plot_tower_constr = os.path.join(
            run_dir, folder_results, "iea15_tower_constrs.pdf" )
    fig_TowerConstrs.savefig(
        path_plot_tower_constr,
        bbox_inches="tight",
        dpi=300
    )

# fig_TowerConstrs

# %%
