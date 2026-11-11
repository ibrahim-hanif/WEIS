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
import pandas as pd

from weis import weis_main
from wisdem.inputs.validation import load_yaml
from wisdem.commonse.fileIO import var_df2dict

#%%
# Define MDAO flags
TEST_RUN = False # TEST_RUN will reduce the number and duration of simulations

# ---- case selection
case_dict = {
    "basecase":     "M4W_01b_basecase_UN_optimDTtower",
    "innovative":   "M4W_01c_innovative_UN_optimDTtower"
}
case_user = "innovative" # TODO: select "basecase" or "innovative"
case_loc = case_dict[ case_user ]
# ----

flag_GBO = False # To perform optimization (True) or not (False)

flag_onlyDT = False # NOTE: # 1

flag_onlyTower = False # NOTE: # 2

flag_DTandTower = True # NOTE: # 3 (not for iea15 DD)

wt_optim = True # turbine to analyse: True = new optim / False = base case

flag_load_results_csv = True

#%%
## File management
main_dir = os.path.dirname( os.path.abspath(__file__) ) 
run_dir = os.path.join( main_dir, case_loc )
# --- Base case
basecase_dir = os.path.join(
    run_dir, os.path.pardir, "M4W_01_base_case_UN_TLPwamit"
)
fname_yaml_geo_basecase = "prac_IEA-15-VolturnUS_rect.yaml" 
loc_yaml_geo_basecase = os.path.join(basecase_dir, fname_yaml_geo_basecase)
if case_user == "innovative":
    fname_yaml_geo_innovative = "prac_M4W-15-TLP.yaml"
    loc_yaml_geo_basecase = os.path.join(run_dir, fname_yaml_geo_innovative)

# --- Overrides
override_geometry = {}
override_analysis = {}

# -- MODELLING
fname_modeling_options = os.path.join(main_dir, "M4W_MODELING_OPTIONS.yaml")

# -- ANALYSIS
analysisNOopt = os.path.join(run_dir, "analysisNOOpt.yaml")
analysisOpt_onlyDT = os.path.join(run_dir, "analysisOpt_onlyDT.yaml")
analysisOpt_onlyTower = os.path.join(run_dir, "analysisOpt_onlyTower.yaml")
analysisOpt = os.path.join(run_dir, "analysisOpt.yaml") # NOTE: DT + Tower

if flag_onlyDT:
    print(" -- case: only DT optimization")
    fname_analysis_options = analysisOpt_onlyDT

elif flag_onlyTower:
    print(" -- case: only Tower optimization")
    fname_analysis_options = analysisOpt_onlyTower

elif flag_DTandTower:
    print(" -- case: DT + Tower optimization")
    fname_analysis_options = analysisOpt

else:
    print(" -- case: NO optimization (analysis)")
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

# ---- last optim
loc_yaml_geo_wt_optim = os.path.join(
        case_loc,
        dict_anaOpts['general']['folder_output'],
        dict_anaOpts['general']['fname_output']
    ) + ".yaml"
# ---- DT optim
dict_dtOpts = load_yaml( analysisOpt_onlyDT )
loc_yaml_geo_dt_optim = os.path.join(
    case_loc,
    dict_dtOpts['general']['folder_output'],
    dict_dtOpts['general']['fname_output']
) + ".yaml"
# ---- Tower optim
dict_wtOpts = load_yaml( analysisOpt_onlyTower )
loc_yaml_geo_tower_optim = os.path.join(
    case_loc,
    dict_wtOpts['general']['folder_output'],
    dict_wtOpts['general']['fname_output']
) + ".yaml"

# optimized
if wt_optim:
    fname_wt_input = loc_yaml_geo_wt_optim
    print(" -- initial turbine design: saved from last optim")

# use optim DT for tower optim
elif flag_onlyTower:
    fname_wt_input = loc_yaml_geo_dt_optim
    print(" -- initial turbine design: saved DT optim")

elif flag_DTandTower: # use basecase for DT+tower optim
    # TODO: start from basecase OR DT+tower seperated optimal results
    # 1.
    fname_wt_input = loc_yaml_geo_basecase #loc_yaml_geo_tower_optim OR loc_yaml_geo_basecase
    print(" -- initial turbine design: basecase")
    # 2. 
    # fname_wt_input = loc_yaml_geo_tower_optim
    # print(" -- initial turbine design: saved Tower optim")

else: # base case
    fname_wt_input = loc_yaml_geo_basecase
    print(" -- initial turbine design: basecase")

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
    print( f" * driver status: {wt_opt.driver.get_exit_status()}" )

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
    print("Fore-aft (FA) / side-side (SS) freq ranges:")
    print("Tower (only):")
    print(" ", freq_tower[0:2], " Hz" )
    freq_floater = wt_opt["floatingse.structural_frequencies"] # towerse.tower OR floatingse.structural_frequencies
    print("Floating tower:")
    print(" ", freq_floater[0:2], " Hz \n" )

    print("LSS desvars:")
    print(" ", wt_opt["drivese.L_h1"], wt_opt["drivese.L_12"], wt_opt["drivese.lss_diameter"], wt_opt["drivese.lss_wall_thickness"] )
    if case_user == "innovative":
        print("HSS desvars:")
        print(" ", wt_opt["drivese.L_hss"], wt_opt["drivese.hss_diameter"], wt_opt["drivese.hss_wall_thickness"] )
    print("Bedplate wall thickness:")
    if case_user == "basecase":
        print(" ", wt_opt["drivese.bedplate_wall_thickness"])
    else:
        print(" ", wt_opt["drivese.bedplate_flange_width"],
              wt_opt["drivese.bedplate_flange_thickness"],
              wt_opt["drivese.bedplate_web_thickness"]
        )

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
    if case_user == "basecase":
        print("- constr_access:", wt_opt["drivese.constr_access"])
        print("- constr_ecc:", wt_opt["drivese.constr_ecc"])

    print("\n--- RNA properties ---")
    print(f"RNA mass: {wt_opt["drivese.rna_mass"]}")
    print(f"RNA cm: {wt_opt["drivese.rna_cm"]}")
    
    print("\nTower-top / drivetrain bedplate base loads:")
    print(" - base_F: ", wt_opt['drivese.base_F'])
    print(" - base_M: ", wt_opt['drivese.base_M'])
    #
    print("\n--- obj: masses ---")
    # print(f"MSA mass: {wt_opt["drivese.msa_mass"]}")
    print(f"nacelle mass: {wt_opt["drivese.nacelle_mass"]}")
    print(f"nacelle cm: {wt_opt["drivese.nacelle_cm"]}")
    print(f"tower mass: {wt_opt["towerse.tower_mass"]}")
    print(f"Turbine mass: {wt_opt["floatingse.turbine_mass"]}")

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
if case_user == "innovative":
    lst_DTconstrs.append("constr_hss_vonmises")

fig_DTconstrs, ax_DTconstrs = plot_drivetrain_constraints(
    csv_file,lst_constrs=lst_DTconstrs,flag_WTnamespace=True)

if (case_user == "basecase"):# and (flag_GBO is True): # TODO
    fig_DTconstrs.axes[1].patches[0].set_color("tab:green")
    fig_DTconstrs.axes[1].patches[1].set_color("tab:green")
    fig_DTconstrs.axes[1].patches[5].set_color("tab:green")
else: # innovative
    fig_DTconstrs.axes[1].patches[4].set_color("tab:green")

# save
if 0: #flag_save_plots:
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

if 0: #flag_save_plots: 
    path_plot_tower_constr = os.path.join(
            run_dir, folder_results, fname_results + "_tower_constrs.png" )
    fig_TowerConstrs.savefig(
        path_plot_tower_constr,
        bbox_inches="tight",
        dpi=300
    )

# fig_TowerConstrs

#%% options for plotting

labels_compr=[
        "Basecase",
        f"De-coupled",
        f"Integrated",
    ]
clrs_compr=[
    "0.7", #"turquoise",
    "tab:green", #"tab:cyan",
    "tab:pink", #"tab:blue"
    ]

# %%
# Tower geometry
from Drive4Wind.utilities.plot_tower_data import plot_tower_geo_comparison

clrs_compr_tower = clrs_compr[:2].copy()

# ---- geo yaml and labels
if flag_onlyTower:
    optim_yaml = loc_yaml_geo_tower_optim
    ref_yaml = loc_yaml_geo_dt_optim
    optim_label = labels_compr[1]
    ref_label = labels_compr[0]

    legend_anchor_box = (0.7, 0.35)

elif flag_DTandTower:
    optim_yaml = loc_yaml_geo_wt_optim
    ref_yaml = loc_yaml_geo_tower_optim
    optim_label = labels_compr[2]
    ref_label = labels_compr[1]

    legend_anchor_box = ()

    clrs_compr_tower = clrs_compr[1:].copy()

else:
    optim_yaml = loc_yaml_geo_basecase
    ref_yaml = loc_yaml_geo_basecase
    optim_label = labels_compr[0] + " tower"
    ref_label = labels_compr[0] + " tower"

    legend_anchor_box = (0.9, 0.35)

clrs_compr_tower.append("darkgreen") # for tower-transition

# ----

fig_TowerGeo, ax_TowerGeo = plot_tower_geo_comparison(
    optim_yaml,
    ref_yaml,
    m4w_label=optim_label, iea_label=ref_label,
    colors= clrs_compr_tower
)

fig_TowerGeo.set_size_inches([13,8])
# 
for iplot in range(2):
    for iline in range(3):
        ax_TowerGeo[ iplot ].lines[ iline ].set_linewidth( linewidth )
        if iline != 0: ax_TowerGeo[ iplot ].lines[ iline ].set_marker(".")
        if iline == 1: ax_TowerGeo[ iplot ].lines[ iline ].set_linestyle("--")
#
ax_TowerGeo[0].legend()
ax_TowerGeo[0].legend_.set_bbox_to_anchor( legend_anchor_box )
#
ax_TowerGeo[0].set_ylabel("Height along tower [m]")

if 0: #flag_save_plots: 
    path_plot_tower_geo = os.path.join(
            run_dir, folder_results, fname_results + "_tower_geo.png" )
    fig_TowerGeo.savefig(
        path_plot_tower_geo,
        bbox_inches="tight",
        dpi=300
    )

# fig_TowerGeo

# %%
# Define input-output files

# variables to parse from each csv output
from Drive4Wind.utilities.raft_helpers import lst_variables, parse_variables_from_csv_to_dict

tendon_index = 0
str_max_Tmoor_anchor = f"raft.max_Tmoor_{tendon_index+1}_anchor"

lst_output_folder = [
  "outputs\\only_Tower\\optim.csv",         # de-coupled
  f"outputs\\DTandTower\\optim.csv",   # integrated
]

# input csv output files
lst_csv_outputs = lst_output_folder.copy()
for i, csv_dir in enumerate(lst_output_folder):
  csv_file = os.path.join( run_dir, csv_dir )
  lst_csv_outputs[i] = csv_file

# parse into df
outputs_df, outputs_dict = parse_variables_from_csv_to_dict(
    lst_csv_outputs=lst_csv_outputs,
    lst_variables=lst_variables,
    tendon_index=tendon_index
)

# -- post-processing
csv_all_results = os.path.join(
    run_dir, f"outputs\\compr_decoupl_integrated.csv"
)

if 0: outputs_df.to_csv( csv_all_results, index=False )

#%% options for plotting

labels_compr_raft = labels_compr[1:]
clrs_compr_raft = clrs_compr[1:]
markers_compr=["v", "^"]

RBM_NAMES_SYMB_DICT = {
    "surge": r"$(x)$",
    "sway ": r"$(y)$",
    "heave ": r"$(z)$",
    "roll ": r"$(\phi)$",
    "pitch ": r"$(\theta)$",
    "yaw ": r"$(\psi)$",
}

# base case csv
csv_iea15 = os.path.join( lst_csv_outputs[0] )
df_iea15 = pd.read_csv(csv_iea15)
dict_iea15 = var_df2dict( df_iea15 )

hub_height = eval(dict_iea15['configuration.hub_height_user'])
rpm_min = eval(dict_iea15['drivese.minimum_rpm'])
rpm_rated = eval(dict_iea15['drivese.rated_rpm'])

# %%[markdown]
# ### Plot drivetrain-base & tower base loads comparison
#%%
from Drive4Wind.utilities.raft_helpers import plot_bars_force_moment_loads

#%%
# Drivetrain-base or tower-top loads
fig, axs, F, M = plot_bars_force_moment_loads(
    path_csv_of_all_outputs=csv_all_results,
    var_force="drivese.base_F",
    var_moment="drivese.base_M",

    design_labels=labels_compr_raft,

    reference_index=0,

    colors= clrs_compr_raft,

    figsize=(17,7),
    show_percent=True,
    percent_decimals=0,
    title="Tower-Top Loads Comparison"
)

# save
if 0: #flag_save_plots:
    path_twrTopLoads_compr = os.path.join(
        run_dir,
        f"outputs\\compr_twrTopLoads.png"
    )
    fig.savefig(
        path_twrTopLoads_compr,
        bbox_inches="tight",
        dpi=300 )

#%%
# Tower-base loads
fig, axs, F, M = plot_bars_force_moment_loads(
    path_csv_of_all_outputs=csv_all_results,
    var_force="towerse.tower.turbine_F",
    var_moment="towerse.tower.turbine_M",

    design_labels=labels_compr_raft,

    reference_index=0,

    colors= clrs_compr_raft,

    figsize=(17,7),
    show_percent=True,
    percent_decimals=0,
    title="Tower-Base Loads Comparison"
)

# save
if 0: #flag_save_plots:
    path_twrBaseLoads_compr = os.path.join(
        run_dir,
        f"outputs\\compr_twrBaseLoads.png"
    )
    fig.savefig(
        path_twrBaseLoads_compr,
        bbox_inches="tight",
        dpi=300 )

#%%[markdown]
# ### Plot scalar variables for multiple designs
#%%
from Drive4Wind.utilities.raft_helpers import plot_comparison_bar_plot_of_float_vars_from_csv
#%%
# =================
# Variables
# =================
lst_vars_max = [
    ("raft.Max_Offset",       r"$x_{max}$",           "[m]"),
    ("raft.heave_avg",        r"$z_{avg}$",           "[m]"),
    ("raft.Max_PtfmPitch",    r"$\theta_{max}$",      "[deg]"),
    ("raft.max_nac_accel",    r"$a^{max}_{nac}$",     "[m/s/s]"),
    ("raft.max_tower_base",   r"$M^{max}_{TwrBase}$",   "[Nm]"),
    (str_max_Tmoor_anchor,  r"$T_{1,anchor}^{max}$", "[N]")
]

fig, axs, values, differences = (
    plot_comparison_bar_plot_of_float_vars_from_csv(
        csv_all_results,
        reference_index=0,

        lst_vars=lst_vars_max,

        design_labels=labels_compr_raft,
        colors=clrs_compr_raft,

        show_percent=True,
        percent_decimals=1,
        figsize=(16,9),
        title="Maximum Response Comparison (DLC 6.1)",
        idx_axis_show_legend=0
    )
)

if 0: #flag_save_plots:
    path_maxDynamicVariables_compr = os.path.join(
        run_dir,
        f"outputs\\compr_maxDynamicVariables.png"
    )
    fig.savefig(
        path_maxDynamicVariables_compr,
        bbox_inches="tight",
        dpi=300
    )

#%%[markdown]
# ### Plot changes in rigid body periods
#%%
from Drive4Wind.utilities.raft_helpers import plot_comparison_bar_plot_of_1Darray_from_csv

#%%
lst_vars_1Darray = [
    ( "raft.rigid_body_periods", "Rigid Body Modes", "[s]" ),
]

fig, axs, values_RBM, differences_RBM = (
    plot_comparison_bar_plot_of_1Darray_from_csv(
        csv_path=csv_all_results,
        lst_vars=lst_vars_1Darray,
        reference_index=0,

        figsize=(15, 9),
        design_labels=labels_compr_raft,
        colors=clrs_compr_raft,

        show_percent=True,
        percent_decimals=1,
        title="Natural Periods of Rigid Body Modes Comparison"
    )
)

# Save
if 0: #flag_save_plots:
    path_compr_RBM = os.path.join(
        run_dir,
        f"outputs\\compr_RBM.png"
    )
    fig.savefig(
        path_compr_RBM,
        bbox_inches="tight",
        dpi=300
    )

plt.show()

#%%[markdown]
# ### Plot spectra of excitation (1P, 3P), RBMs, tower bending modes (1.,2.)
#%%
from Drive4Wind.utilities.raft_helpers import plot_frequency_placement_with_metocean

#%%

clrs_compr_w_black = clrs_compr.copy()
clrs_compr_w_black[0] = "black"

fig, ax, rbm_periods, tower_periods = (
    plot_frequency_placement_with_metocean(
        csv_path=csv_all_results,
        modeling_options_yaml=fname_modeling_options,
        hub_height=hub_height, 
        rpm_min=rpm_min,
        rpm_rated=rpm_rated,
        design_labels=labels_compr_raft,
        colors=clrs_compr_raft,
        markers=["o", "v", "^"],
        figsize=(21, 10),
        title="Excitation, Rigid-Body and Tower-Bending Frequency Comparison"
    )
)

freq_range_1P = np.array( [rpm_min, rpm_rated] )/60
freq_range_3P = 3* freq_range_1P
print("1P (blade period) ranges:")
print(" - freqs ", freq_range_1P, " Hz | Periods ", 1/freq_range_1P, " s." )
print("3P (blade passing) ranges:")
print(" - freqs ", freq_range_3P, " Hz | Periods ", 1/freq_range_3P, " s.\n" )

if 0: #flag_save_plots:
    path_freq = os.path.join(
        run_dir,
        "outputs",
        f"compr_natPeriods_to_excitation.png"
    )

    fig.savefig(
        path_freq,
        dpi=300,
        bbox_inches="tight"
    )

#%%[markdown]
# ### Plot changes in stats (dynamics) of variables with wind speed
#%%
from Drive4Wind.utilities.raft_helpers import plot_comparison_windspeed_series_from_csv

# %%
lst_vars_wind = [
    ("raft.stats_surge_max",  r"$x_{max}$",           "[m]"),
    ("raft.stats_Mbase_max",  r"$M^{TwrBase}_{max}$",   "[Nm]"),
    ("raft.stats_AxRNA_max",  r"$a^{RNA}_{max}$",     "[m/s/s]")
]

wind_speeds = [
    3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25
]

DLC = "1.1" # 1.1 or 1.6

if DLC == "1.1": index_start_end=(0, 12)
elif DLC == "1.6": index_start_end=(12, 24)
else: ValueError(" --- valid DLC values are 1.1 and 1.6 ;")

fig, axs, values_WS, differences_WS = (
    plot_comparison_windspeed_series_from_csv(
        csv_path=csv_all_results,
        lst_vars=lst_vars_wind,
        wind_speeds=wind_speeds,
        reference_index=0,
        index_start_end=index_start_end,

        figsize=(16, 12),
        design_labels=labels_compr_raft,
        colors=clrs_compr_raft,
        markers=markers_compr,
        title=f"Maximum Response vs. Wind-Speed Comparison (DLC {DLC})"
    )
)

if 0: #flag_save_plots:
    path_compr_response_with_WS = os.path.join(
        run_dir,
        f"outputs\\compr_response_with_WS.png"
    )
    fig.savefig(
        path_compr_response_with_WS,
        bbox_inches="tight",
        dpi=300
    )

#%%
from Drive4Wind.utilities.raft_helpers import plot_comparison_Tmoor_windspeed_from_csv

# %%
tendon_index = 0 # 0 = tendon 1 ; 3 = tendon 4

DLC = "1.1" # 1.1 or 1.6

if DLC == "1.1": index_start_end=(0, 12)
elif DLC == "1.6": index_start_end=(12, 24)
else: ValueError(" --- valid DLC values are 1.1 and 1.6 ;")

fig, axs, Tmoor_DLC11, diff_DLC11 = (
    plot_comparison_Tmoor_windspeed_from_csv(
        csv_path=csv_all_results,
        wind_speeds=wind_speeds,
        index_start_end=index_start_end,
        var = "raft.stats_Tmoor_max",
        tendon_index=tendon_index,
        reference_index=0,
        figsize=(16,6),
        design_labels=labels_compr_raft,
        colors=clrs_compr_raft,
        markers=markers_compr,
        title = f"Tendon {tendon_index+1} Maximum Tensions (DLC {DLC})"
    )
)

if 0: #flag_save_plots:
    str_extn = ".png"

    path_compr_TmoorMax = os.path.join(
        run_dir,
        f"outputs\\compr_Tmoor_{tendon_index+1}_max_with_WS"+str_extn
    )
    fig.savefig(
        path_compr_TmoorMax,
        bbox_inches="tight",
        dpi=300
    )

# %%