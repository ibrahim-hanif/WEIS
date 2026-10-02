#%%[markdown]
# Status: copy of M4W_01_base_case_UN_TLPwamit, but with optimization of the DT tower
#
# Workflow:
# 1. analysis of iea 15mw design (in UN site)
# 2. only DT optimization
# 3. only Tower optimization (with optim DT)
# 4. (X) DT + Tower optim
#
# Progress:
# 1. TODO: 

#%%
import os
import numpy as np
import matplotlib.pyplot as plt

from weis import weis_main
from wisdem.inputs.validation import load_yaml

#%%
# Define MDAO flags
TEST_RUN = False # TEST_RUN will reduce the number and duration of simulations

flag_GBO = False # To perform optimization (True) or not (False)

flag_onlyDT = False # NOTE: # 1

flag_onlyTower = True # NOTE: # 2

flag_DTandTower = False # NOTE: # 3 (not for iea15 DD)

wt_optim = True # turbine to analyse: True = new optim / False = base case

flag_load_results_csv = True

#%%
## File management
run_dir = os.path.dirname( os.path.abspath(__file__) )
# --- Base case
basecase_dir = os.path.join(
    run_dir, os.path.pardir, "M4W_01_base_case_UN_TLPwamit"
)
fname_yaml_geo_basecase = "prac_IEA-15-VolturnUS_rect.yaml" 
loc_yaml_geo_basecase = os.path.join(basecase_dir, fname_yaml_geo_basecase)

# --- Overrides
override_geometry = {}
override_analysis = {}

# -- MODELLING
fname_modeling_options = os.path.join(run_dir, "modelOpts.yaml")

# -- ANALYSIS
analysisNOopt = os.path.join(run_dir, "analysisNOOpt.yaml")
analysisOpt_onlyDT = os.path.join(run_dir, "analysisOpt_onlyDT.yaml")
analysisOpt_onlyTower = os.path.join(run_dir, "analysisOpt_onlyTower.yaml")
analysisOpt = os.path.join(run_dir, "analysisOpt.yaml") # NOTE: DT + Tower

if flag_onlyDT:
    fname_analysis_options = analysisOpt_onlyDT

elif flag_onlyTower:
    fname_analysis_options = analysisOpt_onlyTower

elif flag_DTandTower:
    fname_analysis_options = analysisOpt

else:
    fname_analysis_options = analysisNOopt

dict_anaOpts = load_yaml( fname_analysis_options )

# ---- GBO ?
if not flag_GBO:
    override_analysis["general"] = {}
    override_analysis["general"]["fname_output"] = "NOoptim"
    override_analysis["driver"] = {}
    override_analysis["driver"]["optimization"] = {}
    override_analysis["driver"]["optimization"]["flag"] = False

# -- GEOMETRY
if wt_optim: # optimized
    loc_yaml_geo_wt_optim = os.path.join(
        dict_anaOpts['general']['folder_output'],
        dict_anaOpts['general']['fname_output']
    ) + ".yaml"
    fname_wt_input = loc_yaml_geo_wt_optim

elif flag_onlyTower: # use optim DT for tower optim
    dict_dtOpts = load_yaml( analysisOpt_onlyDT )
    loc_yaml_geo_dt_optim = os.path.join(
        dict_dtOpts['general']['folder_output'],
        dict_dtOpts['general']['fname_output']
    ) + ".yaml"
    fname_wt_input = loc_yaml_geo_dt_optim

else: # base case
    fname_wt_input = loc_yaml_geo_basecase

#%%
# run WEIS
if not flag_load_results_csv:
    wt_opt, modeling_options, opt_options = weis_main(
        # init
        fname_wt_input, 
        fname_modeling_options, 
        fname_analysis_options,
        # override
        geometry_override=override_geometry,
        analysis_override=override_analysis,
        # test ?
        test_run=TEST_RUN
    )

# %%
# Print the results
if not flag_load_results_csv:
    print("F_aero_hub:")
    print(" ", wt_opt["drivese.F_aero_hub"]/1e6, " MN" )
    print("M_aero_hub:")
    print(" ", wt_opt["drivese.M_aero_hub"]/1e6, " MNm \n" )

    # ---- 1P and 3P freq ranges
    rpm_min = wt_opt['drivese.minimum_rpm'][0]
    rpm_rated = wt_opt['drivese.rated_rpm'][0]
    freq_range_1P = np.array( [rpm_min, rpm_rated] )/60
    freq_range_3P = 3* freq_range_1P
    print("1P (blade period) freq ranges:")
    print(" ", freq_range_1P, " Hz" )
    print("3P (blade passing) freq ranges:")
    print(" ", freq_range_3P, " Hz \n" )
    freq_tower = wt_opt["towerse.tower.structural_frequencies"] # towerse.tower OR floatingse.structural_frequencies
    print("Tower fore-aft/side-side freq range:")
    print(" ", freq_tower[0:2], " Hz" )
    freq_floater = wt_opt["floatingse.structural_frequencies"] # towerse.tower OR floatingse.structural_frequencies
    print("Floater freq range:")
    print(" ", freq_floater[0:2], " Hz \n" )

    print("LSS desvars:")
    print(" ", wt_opt["drivese.L_h1"], wt_opt["drivese.L_12"], wt_opt["drivese.lss_diameter"], wt_opt["drivese.lss_wall_thickness"] )
    print("Bedplate wall thickness:")
    print(" ", wt_opt["drivese.bedplate_wall_thickness"])

    print("\n--- constr_ max ---")
    print("- lss: ", np.max(wt_opt["drivese.constr_lss_vonmises"]) )
    print("- bedplate: ", np.max(wt_opt["drivese.constr_bedplate_vonmises"]) )
    print("- defl mb1: ", np.max(wt_opt["drivese.constr_mb1_defl"]) )
    print("- defl mb2: ", np.max(wt_opt["drivese.constr_mb2_defl"]) )

    print("- constr_shaft_deflection:", wt_opt["drivese.constr_shaft_deflection"])
    print("- constr_shaft_angle:", wt_opt["drivese.constr_shaft_angle"])
    print("- constr_stator_deflection:", wt_opt["drivese.constr_stator_deflection"])
    print("- constr_stator_angle:", wt_opt["drivese.constr_stator_angle"])
    print("- constr_hub_diameter:", wt_opt["drivese.constr_hub_diameter"])
    print("- constr_length:", wt_opt["drivese.constr_length"])
    print("- constr_height:", wt_opt["drivese.constr_height"])
    print("- constr_access:", wt_opt["drivese.constr_access"])
    print("- constr_ecc:", wt_opt["drivese.constr_ecc"])

    print("\nTower-top / drivetrain bedplate base loads:")
    print(" - base_F: ", wt_opt['drivese.base_F'])
    print(" - base_M: ", wt_opt['drivese.base_M'])
    #
    print("\n--- obj: masses ---")
    # print(f"MSA mass: {wt_opt["drivese.msa_mass"]}")
    print(f"nacelle mass: {wt_opt["drivese.nacelle_mass"]}")
    print(f"nacelle cm: {wt_opt["drivese.nacelle_cm"]}")
    print(f"tower mass: {wt_opt["towerse.tower_mass"]}")

    print("\n--- RNA properties ---")
    print(f"RNA mass: {wt_opt["drivese.rna_mass"]}")
    print(f"RNA cm: {wt_opt["drivese.rna_cm"]}")

    print("\n--- Dynamic properties (RAFT) ---")
    print(f" Max_Offset [m]: {wt_opt["raft.Max_Offset"]}")
    print(f" Heave_avg [m]: {wt_opt["raft.heave_avg"]}")
    print(f" Max_PtfmPitch [deg]: {wt_opt["raft.Max_PtfmPitch"]}")
    print(f" Max_nac_accel [m/s^2]: {wt_opt["raft.max_nac_accel"]}")
    print(f" Max_tower_base [10^9 Nm]: {wt_opt["raft.max_tower_base"]/1e9}")

    print("\n--- Merit figures ---")
    print(f" LCOE [USD/kW/h]: {wt_opt["financese.lcoe"]}")
# -----------------------------------------------------------------------

# %%[markdown]
# # Post-process
#%%
# directories
if not flag_load_results_csv: dict_analy = opt_options.copy()
else: dict_analy = load_yaml(fname_analysis_options)

folder_results = dict_analy["general"]["folder_output"]
fname_results = dict_analy["general"]["fname_output"]
csv_file = os.path.join( run_dir, folder_results, fname_results + ".csv" )

from Drive4Wind.post_processing.color_schemes import read_color_scheme, loc_clr_scheme_m4w
clrs_m4w = read_color_scheme(loc_clr_scheme_m4w)

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
if flag_GBO:
    fig_DTconstrs.axes[1].patches[1].set_color("tab:green")
# save
if False: #flag_save_plots:
    path_plot_dt_constr = os.path.join(
        run_dir, folder_results, fname_results + "_DT_constrs.png" )
    fig_DTconstrs.savefig(
        path_plot_dt_constr,
        bbox_inches="tight",
        dpi=300
    )

fig_DTconstrs

#%%
# Tower constraints
from Drive4Wind.utilities.plot_tower_data import plot_tower_constraints_stress_utils

fig_TowerConstrs, ax = plot_tower_constraints_stress_utils(
    csv_file,
    figsize=(5.0,10.0),
    colors=["tab:blue","tab:green","tab:orange"]
)

if False: #flag_save_plots: 
    path_plot_tower_constr = os.path.join(
            run_dir, folder_results, fname_results + "_tower_constrs.png" )
    fig_TowerConstrs.savefig(
        path_plot_tower_constr,
        bbox_inches="tight",
        dpi=300
    )

# fig_TowerConstrs

# %%
# Tower geometry
from Drive4Wind.utilities.plot_tower_data import plot_tower_geo_comparison

# optimized tower yaml
dict_wtOpts = load_yaml( analysisOpt_onlyTower )
loc_yaml_geo_tower_optim = os.path.join(
    dict_wtOpts['general']['folder_output'],
    dict_wtOpts['general']['fname_output']
) + ".yaml"

fig_TowerGeo, ax_TowerGeo = plot_tower_geo_comparison(
    loc_yaml_geo_tower_optim,
    loc_yaml_geo_basecase,
    m4w_label="Optimized tower", iea_label="Basecase tower",
    colors=[ "grey", "tab:blue", "darkgreen" ]
)

fig_TowerGeo.set_size_inches([13,8])
# 
for iplot in range(2):
    for iline in range(3):
        ax_TowerGeo[ iplot ].lines[ iline ].set_linewidth( linewidth )
        if iline != 0: ax_TowerGeo[ iplot ].lines[ iline ].set_marker(".")
#
ax_TowerGeo[0].legend()
ax_TowerGeo[0].legend_.set_bbox_to_anchor((0.9, 0.35))
#
ax_TowerGeo[0].set_ylabel("Height along tower [m]")

if False: #flag_save_plots: 
    path_plot_tower_geo = os.path.join(
            run_dir, folder_results, fname_results + "_tower_geo.png" )
    fig_TowerGeo.savefig(
        path_plot_tower_geo,
        bbox_inches="tight",
        dpi=300
    )

# fig_TowerGeo

# %%
