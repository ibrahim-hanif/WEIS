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
from weis import weis_main
from wisdem.inputs.validation import load_yaml
#%%
# Define MDAO flags
TEST_RUN = False # TEST_RUN will reduce the number and duration of simulations

flag_override = True

wt_optim = False # turbine to analyse: True = new optim / False = base case

flag_save_results = False

flag_load_results_csv = True

flag_save_plots = False

#%%
## File management
run_dir = os.path.dirname( os.path.abspath(__file__) )
basecase_dir = os.path.join( run_dir, os.path.pardir, "M4W_01_base_case_UN_TLPwamit" )

# -- geometry
geo_input = "prac_IEA-15-VolturnUS_rect.yaml" 
fname_wt_input = os.path.join(basecase_dir, geo_input)

# -- modelling
fname_modeling_options = os.path.join(run_dir, "modelOpts.yaml")

# -- analysis
fname_analysis_options = os.path.join(run_dir, "analysisNOOpt.yaml")

# -- post-processing
csv_all_results = os.path.join( run_dir, "outputs\\compr_DD.csv" )

#%%
# Override values
# -- geometry
override_geometry = {}
if flag_override:
    override_geometry["drivese.generator_mass_user"] = [30.E3]
# -- analysis
override_analysis = {}
if flag_override:
    override_analysis["general"] = {}
    override_analysis["general"]["folder_output"] = "outputs/DD_floatfarm15"

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
  print(f" Max (stats_Tmoor_max) [10^9 Nm]: {wt_opt["raft.stats_Tmoor_max"].max()/1e9}")


  print("\n--- Merit figures ---")
  print(f" LCOE [USD/kW/h]: {wt_opt["financese.lcoe"]}")
  # -----------------------------------------------------------------------

# %%[markdown]
# Post-process
#%%
# def util funcs
from wisdem.commonse.fileIO import var_df2dict

def array_eval( value ):
  return np.array( eval( value) )
#%%

# input files
lst_output_folder = [
  "outputs\\DD_iea15\\results.csv",
  "outputs\\DD_floatfarm15\\results.csv"
]

lst_variables = [
  "drivese.F_aero_hub",
  "drivese.M_aero_hub",

  "floatingse.structural_frequencies",

  "drivese.base_F",
  "drivese.base_M",

  "drivese.nacelle_mass",
  "drivese.nacelle_cm",

  "raft.rigid_body_periods",

  "raft.Max_Offset",
  "raft.heave_avg",
  "raft.Max_PtfmPitch",
  "raft.max_nac_accel",
  "raft.max_tower_base",

  "raft.stats_surge_max",
  "raft.stats_Mbase_max",
  "raft.stats_Tmoor_max",
  "raft.stats_AxRNA_max"
]

# output init
outputs_dict = {}

#%%
# loop
for i, csv_dir in enumerate(lst_output_folder):

  csv_file = os.path.join( run_dir, csv_dir )

  df = pd.read_csv(csv_file)

  dict_vals = var_df2dict( df )

  # for each 

  for iv, var in enumerate(lst_variables):
    if var not in outputs_dict.keys(): outputs_dict[ var ] = []
    outputs_dict[ var ].append( dict_vals[ var ] )

#%%
outputs_df = pd.DataFrame( outputs_dict )

if flag_save_results:
  outputs_df.to_csv( csv_all_results, index=False )

#%%
if flag_load_results_csv:
   outputs_df = pd.read_csv(csv_all_results)

# %%[markdown]
# ### Plot tower base loads comparison
# TODO: incl in each bar top, the change % relative to init
# %%
from Drive4Wind.utilities.plot_tower_data import get_towerBaseLoads_from_csv, plot_compr_towerBaseLoads_from_dict
from Drive4Wind.post_processing.color_schemes import plot_rcParams_update, loc_clr_scheme_m4w, read_color_scheme
clrs_m4w = read_color_scheme( loc_clr_scheme_m4w )
plt.rcParams.update( plot_rcParams_update )

# - dict of both
twrLoads_iea15_dict = get_towerBaseLoads_from_csv(
   os.path.join(run_dir, lst_output_folder[0])
)
twrLoads_floatfarm15_dict = get_towerBaseLoads_from_csv(
   os.path.join(run_dir, lst_output_folder[1])
)
#%%
# - plot both
path_twrBaseLoads_compr = None
if flag_save_plots:
  path_twrBaseLoads_compr = os.path.join(
    run_dir, "outputs\\compr_twrBaseLoads.png")

plot_compr_towerBaseLoads_from_dict(
   twrLoads_floatfarm15_dict, twrLoads_iea15_dict,
   "FLOATFARM 15MW", "IEA 15MW", figsize=(16,8),
   loc_save_img=path_twrBaseLoads_compr
)

# %%[markdown]
# ### Plot change in Maximum (extreme) variables
# %%
# from the results comparison 
lst_vars_max = [
  ("raft.Max_Offset", r"$x_{max}$", "[m]"),
  ("raft.heave_avg", r"$z_{avg}$", "[m]"),
  ("raft.Max_PtfmPitch", r"$\theta_{max}$", "[deg]"),
  ("raft.max_nac_accel", r"$a^{nac}_{max}$", "[m/s/s]"),
  ("raft.max_tower_base", r"$M^{tower}_{max}$", "[Nm]")
]

#%%
# plot the change_ dict as a bar plot, with names one x-axis and values on y-axis
def plot_comparison_bar_plot_of_float_vars_from_csv(
        csv_path,
        lst_vars=lst_vars_max,
        first_label="IEA 15MW",
        second_label="Made4Wind",
        colors=None,
        ncols=3,
        figsize=None,
        loc_save_img=None,
        percent_decimals=1):
    """
    only valid for float type variables
    """

    df = pd.read_csv(csv_path)

    if len(df) < 2:
        raise ValueError(
            "CSV must contain at least two data rows."
        )

    row1 = df.iloc[0]
    row2 = df.iloc[1]

    vals1 = np.array(
        [float(row1[var]) for var, _, _ in lst_vars]
    )

    vals2 = np.array(
        [float(row2[var]) for var, _, _ in lst_vars]
    )

    labels = [
        label for _, label, _ in lst_vars
    ]

    units = [
        unit for _, _, unit in lst_vars
    ]

    with np.errstate(divide="ignore",
                     invalid="ignore"):

        differences = (
            (vals2 - vals1)
            / vals1
            * 100.0
        )

    if colors is None:
        colors = [
            "tab:blue",
            "tab:orange"
        ]

    nvars = len(lst_vars)
    import math
    nrows = math.ceil(nvars / ncols)

    if figsize is None:
        figsize = (
            6 * ncols,
            5 * nrows
        )

    fig, axs = plt.subplots(
        nrows,
        ncols,
        figsize=figsize
    )

    axs = np.atleast_1d(axs).flatten()

    for i, ax in enumerate(axs[:nvars]):

        ax.bar(
            -0.18,
            vals1[i],
            width=0.36,
            color=colors[0],
            label=first_label
        )

        ax.bar(
            0.18,
            vals2[i],
            width=0.36,
            color=colors[1],
            label=second_label
        )

        diff = differences[i]
        value = vals2[i]

        if np.isfinite(diff):

            scale = max(
                abs(vals1[i]),
                abs(vals2[i]),
                1e-12
            )

            offset = 0.03 * scale

            if value >= 0:
                y = value + offset
                va = "bottom"
            else:
                y = value - offset
                va = "top"

            ax.text(
                0.18,
                y,
                f"{diff:+.{percent_decimals}f}%",
                ha="center",
                va=va
            )

        ax.set_xticks([0])

        ax.set_xticklabels(
            [labels[i]]
        )

        ax.set_ylabel(
            units[i]
        )

        ax.grid(
            True,
            axis="y"
        )

        ax.set_axisbelow(True)

        ymin, ymax = ax.get_ylim()

        if value >= 0:
            ax.set_ylim(
                ymin,
                ymax * 1.12
            )
        else:
            ax.set_ylim(
                ymin * 1.12,
                ymax
            )

    # remove unused subplots
    for ax in axs[nvars:]:
        ax.remove()

    axs[0].legend()

    fig.suptitle(
        "Maximum Results Comparison"
    )

    plt.tight_layout()

    if loc_save_img:
        plt.savefig(
            loc_save_img,
            bbox_inches="tight",
            dpi=300
        )

    plt.show()

    return (
        vals1,
        vals2,
        differences
    )

#%%
# - plot both
path_maxDynamicVariables_compr = None
if flag_save_plots:
  path_maxDynamicVariables_compr = os.path.join(
    run_dir, "outputs\\compr_maxDynamicVariables.png")

plot_comparison_bar_plot_of_float_vars_from_csv(
   csv_path=csv_all_results, lst_vars=lst_vars_max,
   first_label="IEA 15MW", second_label="FLOATFARM 15MW",
   loc_save_img=path_maxDynamicVariables_compr
)

#%%[markdown]
# ### Plot changes in rigid body periods
# %%
def plot_comparison_bar_plot_of_1Darray_from_csv(
        csv_path,
        lst_vars,
        first_label="IEA 15MW",
        second_label="Made4Wind",
        colors=None,
        figsize=None,
        percent_decimals=1,
        loc_save_img=None):

    df = pd.read_csv(csv_path)

    if len(df) < 2:
        raise ValueError(
            "CSV must contain at least two rows."
        )

    row1 = df.iloc[0]
    row2 = df.iloc[1]

    nvars = len(lst_vars)

    if colors is None:
        colors = [
            "tab:blue",
            "tab:orange"
        ]

    if figsize is None:
        figsize = (
            7,
            5 * nvars
        )

    fig, axs = plt.subplots(
        nvars,
        1,
        figsize=figsize
    )

    axs = np.atleast_1d(axs)

    import ast
    for ax, (var, label, unit) in zip(
            axs,
            lst_vars):

        vals1 = np.asarray(
            ast.literal_eval(
                str(row1[var])
            ),
            dtype=float
        )

        vals2 = np.asarray(
            ast.literal_eval(
                str(row2[var])
            ),
            dtype=float
        )

        if len(vals1) != len(vals2):

            raise ValueError(
                f"Different lengths for {var}"
            )

        n = len(vals1)

        x = np.arange(n)

        width = 0.35

        ax.bar(
            x - width/2,
            vals1,
            width=width,
            color=colors[0],
            label=first_label
        )

        ax.bar(
            x + width/2,
            vals2,
            width=width,
            color=colors[1],
            label=second_label
        )

        with np.errstate(
            divide="ignore",
            invalid="ignore"
        ):

            diff = (
                (vals2 - vals1)
                / vals1
                * 100
            )

        for i in range(n):

            if np.isfinite(diff[i]):

                scale = max(
                    abs(vals1[i]),
                    abs(vals2[i]),
                    1e-12
                )

                offset = 0.03 * scale

                if vals2[i] >= 0:
                    y = vals2[i] + offset
                    va = "bottom"
                else:
                    y = vals2[i] - offset
                    va = "top"

                ax.text(
                    x[i] + width/2,
                    y,
                    f"{diff[i]:+.{percent_decimals}f}%",
                    ha="center",
                    va=va,
                    # fontsize=9
                )

        # ax.set_title(label)

        ax.set_ylabel(unit)

        ax.set_xticks( x )

        ax.set_xticklabels(
            [str(i) for i in range(n)]
        )

        ax.set_xlabel( label )

        ax.grid(
            True,
            axis="y",
            alpha=0.3
        )

    axs[0].legend()

    # fig.suptitle("1D Array Variable Comparison")

    plt.tight_layout()

    if loc_save_img:

        plt.savefig(
            loc_save_img,
            bbox_inches="tight",
            dpi=300
        )

    plt.show()
# %%
lst_vars_1Darray = [
    ( "raft.rigid_body_periods", "Rigid Body Modes", "[s]")
]

# - plot both
path_compr_RBM = None
if flag_save_plots:
  path_compr_RBM = os.path.join(
    run_dir, "outputs\\compr_RBM.png")
  
plot_comparison_bar_plot_of_1Darray_from_csv(
    csv_path=csv_all_results,
    lst_vars=lst_vars_1Darray,
    first_label="IEA 15MW", second_label="FLOATFARM 15MW",
    figsize=(10,7), loc_save_img=path_compr_RBM
)

#%%[markdown]
# ### Plot changes in stats (dynamics) of variables with wind speed
#%%
def plot_comparison_windspeed_series_from_csv(
        csv_path,
        lst_vars,
        wind_speeds=None,
        index_start_end=(),
        first_label="IEA 15MW",
        second_label="Made4Wind",
        colors=None,
        figsize=None,
        loc_save_img=None,
        percent_decimals=1):

    import ast
    df = pd.read_csv(csv_path)

    if len(df) < 2:
        raise ValueError(
            "CSV must contain at least two rows."
        )

    row1 = df.iloc[0]
    row2 = df.iloc[1]

    if colors is None:
        colors = [
            "tab:blue",
            "tab:orange"
        ]

    nvars = len(lst_vars)

    if len(index_start_end) == 0:
        index_start_end = (0, len(wind_speeds))

    if figsize is None:
        figsize = (
            16,
            4 * nvars
        )

    fig, axs = plt.subplots(
        nvars,
        2,
        figsize=figsize,
        squeeze=False
    )

    for i, (var, label, unit) in enumerate(lst_vars):

        ax_val = axs[i, 0]
        ax_diff = axs[i, 1]

        vals1 = np.asarray(
            ast.literal_eval(
                str(row1[var])
            ),
            dtype=float
        )[ index_start_end[0]:index_start_end[1] ]

        vals2 = np.asarray(
            ast.literal_eval(
                str(row2[var])
            ),
            dtype=float
        )[ index_start_end[0]:index_start_end[1] ]

        if len(vals1) != len(vals2):

            raise ValueError(
                f"{var}: inconsistent array lengths."
            )

        n = len(vals1)

        if wind_speeds is None:

            x = np.arange(n)

        else:

            if len(wind_speeds) != n:

                raise ValueError(
                    f"{var}: array length={n}, "
                    f"wind speeds={len(wind_speeds)}"
                )

            x = np.asarray(wind_speeds)

        with np.errstate(
            divide="ignore",
            invalid="ignore"
        ):

            diff = (
                (vals2 - vals1)
                / vals1
                * 100.0
            )

        # --------------------------------------------------
        # LEFT : actual values
        # --------------------------------------------------

        ax_val.plot(
            x,
            vals1,
            "-o",
            linewidth=2,
            color=colors[0],
            label=first_label
        )

        ax_val.plot(
            x,
            vals2,
            "-s",
            linewidth=2,
            color=colors[1],
            label=second_label
        )

        ax_val.set_title(
            label
        )

        ax_val.set_ylabel(
            unit
        )

        ax_val.set_xticks( wind_speeds )

        ax_val.grid(
            True,
            alpha=0.3
        )

        if i == 0:
            ax_val.legend()

        # --------------------------------------------------
        # RIGHT : % difference
        # --------------------------------------------------

        ax_diff.plot(
            x,
            diff,
            "-o",
            linewidth=2,
            color="tab:red"
        )

        ax_diff.axhline(
            0.0,
            color="k",
            linestyle="--",
            linewidth=1
        )

        ax_diff.set_title(
            f"{label}: % Difference"
        )

        ax_diff.set_ylabel(
            "[%]"
        )

        ax_diff.set_xticks( wind_speeds )

        ax_diff.grid(
            True,
            alpha=0.3
        )

        ymax = np.nanmax(np.abs(diff))

        if np.isfinite(ymax):
            ax_diff.set_ylim(
                -1.15 * ymax,
                1.15 * ymax
            )

    axs[-1, 0].set_xlabel(
        "Wind Speed [m/s]"
    )

    axs[-1, 1].set_xlabel(
        "Wind Speed [m/s]"
    )

    fig.suptitle(
        "Wind-Speed Response Comparison"
    )

    plt.tight_layout()

    if loc_save_img:

        plt.savefig(
            loc_save_img,
            bbox_inches="tight",
            dpi=300
        )

    plt.show()
    
#%%
lst_vars_wind = [
  ("raft.stats_surge_max", r"$x_{max}$", "[m]"),
  ("raft.stats_Mbase_max",r"$M^{tower}_{max}$","[Nm]"),
  ("raft.stats_AxRNA_max",r"$a^{RNA}_{max}$","[m/s/s]")
]

wind_speeds = [
    3,  5,  7,  9, 11, 13, 15, 17, 19, 21, 23, 25
]

# - plot both
path_compr_response_with_WS = None
if flag_save_plots:
  path_compr_response_with_WS = os.path.join(
    run_dir, "outputs\\compr_response_with_WS.png")
  
plot_comparison_windspeed_series_from_csv(
    csv_path=csv_all_results,
    lst_vars=lst_vars_wind,
    wind_speeds=wind_speeds,
    first_label="IEA 15MW", second_label="FLOATFARM 15MW",
    loc_save_img=path_compr_response_with_WS,
    # figsize=(14,10)
)

# %%
