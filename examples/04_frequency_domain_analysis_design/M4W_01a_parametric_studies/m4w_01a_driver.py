#%%[markdown]
# Status: copy of `M4W_01b_`
#
# Purpose: parametric studies on infl of DT and tower masses on dynamics
#
# Progress:
# 1. TODO: 

#%%
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ast
import math
from weis import weis_main
from wisdem.inputs.validation import load_yaml

# def util funcs
from wisdem.commonse.fileIO import var_df2dict

def array_eval( value ):
  return np.array( eval( value) )

# plot options
from Drive4Wind.post_processing.color_schemes import plot_rcParams_update, loc_clr_scheme_m4w, read_color_scheme
clrs_m4w = read_color_scheme( loc_clr_scheme_m4w )

#%%
# Define MDAO flags
TEST_RUN = False # TEST_RUN will reduce the number and duration of simulations

dt_optim = True # turbine to analyse: True = new optim / False = base case

# ---- sensitivity study parameters: TODO: used defined
sensitiv_compn = "DT" # valid =
# 1. DT = Nac mass
# 2. MOOR TODO = TLP tendon tensions

override = "more" # valid =
# "" or "more" or "less"

percent_change = "50" # % change
# 1. "50"
# 2. "20"

str_compn_n_percent = f"{sensitiv_compn}_{percent_change}"
str_full_sens = f"{sensitiv_compn}_{percent_change}{override}"
print(f"- configuration = {str_full_sens}")
# ----

flag_save_results = False

flag_load_results_csv = True # runWEIS or not, for new analysis

flag_save_plots = False

#%%
## File management
run_dir = os.path.dirname( os.path.abspath(__file__) )
basecase_dir = os.path.join( run_dir, os.path.pardir, "M4W_01_base_case_UN_TLPwamit" )
optimDTtower_dir = os.path.join( run_dir, os.path.pardir, "M4W_01b_basecase_UN_optimDTtower" )

# -- geometry
geo_basecase = "prac_IEA-15-VolturnUS_rect.yaml"
geo_optimDT = "outputs\\only_Tower\\optim.yaml"
if not dt_optim:
    fname_wt_input = os.path.join(basecase_dir, geo_basecase)
else:
    fname_wt_input = os.path.join(optimDTtower_dir, geo_optimDT)

# -- modelling
fname_modeling_options = os.path.join(
    os.path.dirname(optimDTtower_dir), "M4W_MODELING_OPTIONS.yaml"
)

# -- analysis
analy_basecase = "analysisNOOpt.yaml"
analy_optimDT = "analysisOpt_onlyDT.yaml"
if not dt_optim:
    fname_analysis_options = os.path.join(run_dir, analy_basecase)
else:
    fname_analysis_options = os.path.join(optimDTtower_dir, analy_optimDT)  

# -- post-processing
csv_all_results = os.path.join(
    run_dir, f"outputs\\compr_{str_compn_n_percent}.csv"
)

#%% 
# pre-process for parametric studies

lst_output_folder = [
  "outputs\\iea15_UN\\results.csv",         # reference design (iea15 for UN)
  f"outputs\\iea15_UN_{str_compn_n_percent}less\\results.csv",   # 50 % lower Nac weight
  f"outputs\\iea15_UN_{str_compn_n_percent}more\\results.csv",   # 50 % higher Nac weight
]

# base case csv
csv_iea15 = os.path.join( run_dir, lst_output_folder[0] )
df_iea15 = pd.read_csv(csv_iea15)
dict_iea15 = var_df2dict( df_iea15 )

# extract reference nacelle and generator masses
gen_mass_ref = eval( dict_iea15["drivese.generator_mass"] )
nacelle_mass_ref = eval( dict_iea15["drivese.nacelle_mass"] )
ratio_gen_to_nacelle = (gen_mass_ref / nacelle_mass_ref)
print(
 f"mass_gen / mass_nacelle (ref. iea15mw UN): {ratio_gen_to_nacelle:.2f}"
)

def gen_mass_4_nac_pct_change( percent_change ):
    """Return the generator mass multiplier needed to shift the total nacelle mass by `percent_change`.

    Assumes only the generator mass changes while all other nacelle components stay fixed.
    `percent_change` is expressed as a fractional change, e.g. -0.10 for a 10% reduction.
    """
    gen_pct_change = (percent_change / ratio_gen_to_nacelle) + 1
    gen_mass_new = gen_mass_ref * gen_pct_change
    return gen_mass_new

hub_height = eval(dict_iea15['configuration.hub_height_user'])
rpm_min = eval(dict_iea15['drivese.minimum_rpm'])
rpm_rated = eval(dict_iea15['drivese.rated_rpm'])

# extract reference mooring properties
mooring_dia = float(eval(dict_iea15["mooring.line_diameter"])[0]) # NOTE: should be 0.51744 [m] for the basecase
# stiffness per diameter^2
line_stiffness_coeff_moor = np.array(
    eval(dict_iea15["mooring.line_stiffness_coeff"])
) # should be 4.46e10 / (mooring_dia**2)

#%%
# Override values

# ---- geometry
override_geometry = {}

percent_change_in_decimaL  = float(eval(percent_change)/100)

# 1. if Drivetrain/nacelle sensitivity
if ("DT" in sensitiv_compn):
    if "less" in override:
        override_geometry["drivese.generator_mass_user"] = gen_mass_4_nac_pct_change(
            -percent_change_in_decimaL
        )
    elif "more" in override:
        override_geometry["drivese.generator_mass_user"] = gen_mass_4_nac_pct_change(
            percent_change_in_decimaL
        )

elif ("MOOR" in sensitiv_compn): # TODO
    changed_line_k_coeff_moor = line_stiffness_coeff_moor.copy()

    if "less" in override: # tendon-1
        changed_line_k_coeff_moor[0] = 0.1
        override_geometry["mooring.line_stiffness_coeff"] = changed_line_k_coeff_moor

    elif "more" in override: # tendon-3
        changed_line_k_coeff_moor[2] = 0.1
        override_geometry["mooring.line_stiffness_coeff"] = changed_line_k_coeff_moor

# ---- analysis
override_analysis = {}

if dt_optim:
    override_analysis["general"] = {}
    override_analysis["general"]["fname_output"] = "results"
    override_analysis["driver"] = {}
    override_analysis["driver"]["optimization"] = {}
    override_analysis["driver"]["optimization"]["flag"] = False

    folder_results = lst_output_folder[0].split("\\results.csv")[0]

    if "less" in override:
        folder_results = lst_output_folder[1].split("\\results.csv")[0]

    elif "more" in override:
        folder_results = lst_output_folder[2].split("\\results.csv")[0]

    override_analysis["general"]["folder_output"] = os.path.join(
            run_dir, folder_results
    )

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
if not flag_load_results_csv:
  # Print the results
  print("F_aero_hub:")
  print(" ", wt_opt["drivese.F_aero_hub"]/1e6, " MN" )
  print("M_aero_hub:")
  print(" ", wt_opt["drivese.M_aero_hub"]/1e6, " MNm \n" )

  # ---- 1P and 3P freq ranges
  rpm_min = wt_opt['drivese.minimum_rpm'][0]
  rpm_rated = wt_opt['drivese.rated_rpm'][0]
  freq_range_1P = np.array( [rpm_min, rpm_rated] )/60
  freq_range_3P = 3* freq_range_1P
  print("1P (blade period) ranges:")
  print(" - freqs ", freq_range_1P, " Hz | Periods ", 1/freq_range_1P, " s." )
  print("3P (blade passing) ranges:")
  print(" - freqs ", freq_range_3P, " Hz | Periods ", 1/freq_range_3P, " s.\n" )
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
  print(f" Max (stats_Tmoor_max) [10^9 Nm]: {wt_opt["raft.stats_Tmoor_max"].max()/1e9}")


  print("\n--- Merit figures ---")
  print(f" LCOE [USD/kW/h]: {wt_opt["financese.lcoe"]}")

# ======================================================================

# %%[markdown]
# # Post-process
#%%
# options
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
from Drive4Wind.utilities.utilities_drivetrain import plot_drivetrain_constraints

csv_file = os.path.join( run_dir, folder_results, "results.csv" )
lst_DTconstrs = [
    "constr_lss_vonmises", "constr_bedplate_vonmises",
    "constr_shaft_deflection", "constr_shaft_angle",
    "constr_mb1_defl", "constr_mb2_defl",
    "constr_stator_deflection", "constr_stator_angle"]
fig_DTconstrs, ax_DTconstrs = plot_drivetrain_constraints(
    csv_file,lst_constrs=lst_DTconstrs,flag_WTnamespace=True)
# fig_DTconstrs.axes[0].lines[1].set_color("tab:red")
if dt_optim and ( override.__len__() == 0 ):
    fig_DTconstrs.axes[1].patches[1].set_color("tab:green")

# save
if False: #flag_save_plots:
    path_plot_dt_constr = os.path.join(
        run_dir, folder_results, "DT_constrs.png" )
    fig_DTconstrs.savefig( path_plot_dt_constr )

# show
# fig_DTconstrs

# %%
# Tendon tensions

str_Tmoor = 'raft.stats_Tmoor_max'

val_Tmoor = np.asarray( eval(
                str( dict_iea15[ str_Tmoor ] )
                ), dtype=float
            )
val_Tmoor_tendon1_dlc61 = val_Tmoor[-1,1:3]
print(f" Tendon 1 (DLC 6.1) max tension: {val_Tmoor_tendon1_dlc61} N")

#%%
# Define input-output files

# variables to parse from each csv output
from Drive4Wind.utilities.raft_helpers import lst_variables, parse_variables_from_csv_to_dict

tendon_index = 0
str_max_Tmoor_anchor = f"raft.max_Tmoor_{tendon_index+1}_anchor"

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

if flag_save_results:
  outputs_df.to_csv( csv_all_results, index=False )

#%%
if flag_load_results_csv:
   outputs_df = pd.read_csv(csv_all_results)

#%%[markdown]
# # Plotting results from the sensitivity study 

#%% options for plotting

if sensitiv_compn == "DT": str_compn_label = "Nac. mass"
elif sensitiv_compn == "MOOR": str_compn_label = "Tension"

labels_compr=[
        "Reference",
        f"-{percent_change}% {str_compn_label}",
        f"+{percent_change}% {str_compn_label}",
    ]
clrs_compr=[
    "0.7", #"turquoise",
    "tab:green", #"tab:cyan",
    "tab:red", #"tab:blue"
    ]

RBM_NAMES_SYMB_DICT = {
    "surge": r"$(x)$",
    "sway ": r"$(y)$",
    "heave ": r"$(z)$",
    "roll ": r"$(\phi)$",
    "pitch ": r"$(\theta)$",
    "yaw ": r"$(\psi)$",
}

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

    design_labels=labels_compr,

    reference_index=0,

    colors= clrs_compr,

    figsize=(17,7),
    show_percent=True,
    percent_decimals=0,
    title="Tower-Top Loads Comparison"
)

# save
if 0: #flag_save_plots:
    path_twrTopLoads_compr = os.path.join(
        run_dir,
        f"outputs\\compr_twrTopLoads_{str_compn_n_percent}.png"
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

    design_labels=labels_compr,

    reference_index=0,

    colors= clrs_compr,

    figsize=(17,7),
    show_percent=True,
    percent_decimals=0,
    title="Tower-Base Loads Comparison"
)

# save
if 0: #flag_save_plots:
    path_twrBaseLoads_compr = os.path.join(
        run_dir,
        f"outputs\\compr_twrBaseLoads_{str_compn_n_percent}.png"
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

if sensitiv_compn == "DT": idx_axis_show_legend = 0
elif sensitiv_compn == "MOOR": idx_axis_show_legend = 3

fig, axs, values, differences = (
    plot_comparison_bar_plot_of_float_vars_from_csv(
        csv_all_results,
        reference_index=0,

        lst_vars=lst_vars_max,

        design_labels=labels_compr,
        colors=clrs_compr,

        show_percent=True,
        percent_decimals=1,
        figsize=(16,9),
        title="Maximum Response Comparison (DLC 6.1)",
        idx_axis_show_legend=idx_axis_show_legend
    )
)

if 0: #flag_save_plots:
    path_maxDynamicVariables_compr = os.path.join(
        run_dir,
        f"outputs\\compr_maxDynamicVariables_{str_compn_n_percent}.png"
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
        design_labels=labels_compr,
        colors=clrs_compr,

        show_percent=True,
        percent_decimals=1,
        title="Natural Periods of Rigid Body Modes Comparison"
    )
)

# Save
if 0: #flag_save_plots:
    path_compr_RBM = os.path.join(
        run_dir,
        f"outputs\\compr_RBM_{str_compn_n_percent}.png"
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
        design_labels=labels_compr,
        colors=clrs_compr_w_black,
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
        f"compr_natPeriods_to_excitation_{str_compn_n_percent}.png"
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
        design_labels=labels_compr,
        colors=clrs_compr_w_black,
        markers=[ "o", "v", "^"],
        title=f"Maximum Response vs. Wind-Speed Comparison (DLC {DLC})"
    )
)

if 0: #flag_save_plots:
    path_compr_response_with_WS = os.path.join(
        run_dir,
        f"outputs\\compr_response_with_WS_{str_compn_n_percent}.png"
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
        design_labels=labels_compr,
        colors=clrs_compr_w_black,
        markers=[ "o", "v", "^"],
        title = f"Tendon {tendon_index+1} Maximum Tensions (DLC {DLC})"
    )
)

if 0: #flag_save_plots:
    str_extn = ".png"

    path_compr_TmoorMax = os.path.join(
        run_dir,
        f"outputs\\compr_Tmoor_{tendon_index+1}_max_with_WS_{str_compn_n_percent}"+str_extn
    )
    fig.savefig(
        path_compr_TmoorMax,
        bbox_inches="tight",
        dpi=300
    )

# %%
