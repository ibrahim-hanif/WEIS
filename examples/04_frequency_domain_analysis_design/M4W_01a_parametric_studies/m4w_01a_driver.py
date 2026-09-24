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
plt.rcParams.update( plot_rcParams_update )

#%%
# Define MDAO flags
TEST_RUN = False # TEST_RUN will reduce the number and duration of simulations

dt_optim = True # turbine to analyse: True = new optim / False = base case

override = "more" # valid = "" or "more" or "less" ; % change in Nac mass for param study

flag_save_results = False

flag_load_results_csv = False # runWEIS or not, for new analysis

flag_save_plots = False

#%%
## File management
run_dir = os.path.dirname( os.path.abspath(__file__) )
basecase_dir = os.path.join( run_dir, os.path.pardir, "M4W_01_base_case_UN_TLPwamit" )
optimDTtower_dir = os.path.join( run_dir, os.path.pardir, "M4W_01b_basecase_UN_optimDTtower" )

# -- geometry
geo_basecase = "prac_IEA-15-VolturnUS_rect.yaml"
geo_optimDT = "outputs\\optim\\onlyDT_results.yaml"
if not dt_optim:
    fname_wt_input = os.path.join(basecase_dir, geo_basecase)
else:
    fname_wt_input = os.path.join(optimDTtower_dir, geo_optimDT)

# -- modelling
fname_modeling_options = os.path.join(run_dir, "modelOpts.yaml")

# -- analysis
analy_basecase = "analysisNOOpt.yaml"
analy_optimDT = "analysisOpt_onlyDT.yaml"
if not dt_optim:
    fname_analysis_options = os.path.join(run_dir, analy_basecase)
else:
    fname_analysis_options = os.path.join(optimDTtower_dir, analy_optimDT)  

# -- post-processing
csv_all_results = os.path.join( run_dir, "outputs\\compr_DD.csv" )

#%% 
# pre-process for parametric studies

lst_output_folder = [
  "outputs\\iea15_UN\\results.csv",         # reference design (iea15 for UN)
  "outputs\\iea15_UN_50less\\results.csv",   # 50 % lower Nac weight
  "outputs\\iea15_UN_50more\\results.csv",   # 50 % higher Nac weight
]

# extract reference nacelle and generator masses
gen_mass_ref = eval(var_df2dict(
        pd.read_csv(lst_output_folder[0])
    )["drivese.generator_mass"])
nacelle_mass_ref = eval(var_df2dict(
        pd.read_csv(lst_output_folder[0])
    )["drivese.nacelle_mass"])
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

#%%
# Override values

# ---- geometry
override_geometry = {}

if "less" in override:
    override_geometry["drivese.generator_mass_user"] = gen_mass_4_nac_pct_change(
        -0.5
    )

elif "more" in override:
    override_geometry["drivese.generator_mass_user"] = gen_mass_4_nac_pct_change(
        0.5
    )

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
fig_DTconstrs

#%%
# Define input-output files

# input files
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
outputs_dict["name"] = []

#%%
# loop
for i, csv_dir in enumerate(lst_output_folder):

  csv_file = os.path.join( run_dir, csv_dir )

  df = pd.read_csv(csv_file)

  dict_vals = var_df2dict( df )

  # TODO: add first column as 'name' with names of each design 'iea15_UN_*'
  outputs_dict["name"].append( csv_dir.split("\\")[1] )

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

#%%
# # Plotting
# options
labels_compr=[
        "Reference",
        "-50% Nac. mass",
        "+50% Nac. mass"
    ]
clrs_compr=[
    "turquoise",
    "tab:cyan",
    "tab:blue"
    ]

# %%[markdown]
# ### Plot tower base loads comparison
#%%
def plot_tower_base_loads(
        csv_path,
        var_force="drivese.base_F",
        var_moment="drivese.base_M",
        name_col="name",
        design_labels=None,
        colors=None,
        figsize=(14, 6),
        show_percent=False,
        reference_index=0,
        percent_decimals=1,
        loc_save_img=None):
    """
    Plot tower-base force and moment components for multiple designs.

    Expected CSV structure
    ----------------------
    Each row represents one design.

    Required columns:
        name
        drivese.base_F
        drivese.base_M

    drivese.base_F expected as:
        [[Fx], [Fy], [Fz]]

    drivese.base_M expected as:
        [[Mx], [My], [Mz]]

    Parameters
    ----------
    csv_path : str
        Path to comparison CSV.

    design_labels : list[str] or None
        Optional custom labels.
        If None, values from `name_col` are used.

    colors : list or None
        Colors corresponding to each design.

    show_percent : bool
        If True, add percentage difference relative
        to design at `reference_index`.

    reference_index : int
        Row/design used as reference for percentage differences.

    loc_save_img : str or None
        Optional path for saving figure.

    Returns
    -------
    fig, axs
    F, M
        F and M have shape (n_designs, 3), in MN and MNm.
    """
    percent_decimals = int(percent_decimals)

    # ============================================================
    # Read CSV
    # ============================================================

    df = pd.read_csv(csv_path)

    n_designs = len(df)

    if n_designs < 1:
        raise ValueError("CSV contains no designs.")

    # ============================================================
    # Helper for parsing [[x], [y], [z]]
    # ============================================================

    def parse_vector(value):

        arr = np.asarray(
            ast.literal_eval(str(value)),
            dtype=float
        ).squeeze()

        arr = arr.flatten()

        if len(arr) != 3:
            raise ValueError(
                "Expected a 3-component vector, "
                f"but received shape {arr.shape}"
            )

        return arr

    # ============================================================
    # Extract data
    # ============================================================

    F = np.vstack([
        parse_vector(value)
        for value in df[var_force]
    ])

    M = np.vstack([
        parse_vector(value)
        for value in df[var_moment]
    ])

    # N -> MN
    F = F / 1e6

    # Nm -> MNm
    M = M / 1e6

    # ============================================================
    # Labels
    # ============================================================

    if design_labels is None:

        if name_col in df.columns:
            design_labels = df[name_col].astype(str).tolist()
        else:
            design_labels = [
                f"Design {i+1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must match "
            "number of rows in CSV."
        )

    # ============================================================
    # Colors
    # ============================================================

    if colors is None:
        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    # ============================================================
    # Figure
    # ============================================================

    fig, axs = plt.subplots(
        1,
        2,
        figsize=figsize
    )

    ax_F, ax_M = axs

    x = np.arange(3)

    # Keep full group width reasonably constant
    group_width = 0.8
    bar_width = group_width / n_designs

    # Center all bars around Fx/Fy/Fz or Mx/My/Mz
    offsets = (
        np.arange(n_designs)
        - (n_designs - 1) / 2
    ) * bar_width

    # ============================================================
    # Plot each design
    # ============================================================

    for i in range(n_designs):

        ax_F.bar(
            x + offsets[i],
            F[i],
            width=bar_width,
            color=colors[i],
            label=design_labels[i]
        )

        ax_M.bar(
            x + offsets[i],
            M[i],
            width=bar_width,
            color=colors[i],
            label=design_labels[i]
        )

    # ============================================================
    # Percentage differences
    # ============================================================

    def calculate_difference_percent(
            comparison, reference, percent_decimals ):
        diff =  ((comparison - reference) / reference) * 100
        diff = np.round(diff, percent_decimals)
        return diff


    if show_percent:

        F_ref = F[reference_index]
        M_ref = M[reference_index]

        for i in range(n_designs):

            if i == reference_index:
                continue

            with np.errstate(
                    divide="ignore",
                    invalid="ignore"):

                F_diff = calculate_difference_percent(
                    F[i], F_ref, percent_decimals
                )
                M_diff = calculate_difference_percent(
                    M[i], M_ref, percent_decimals
                )

            # Force labels
            for j in range(3):

                if np.isfinite(F_diff[j]) and not (
                    np.isclose( F_diff[j], 0.0 )
                ):

                    offset_y = (
                        0.04
                        * max(
                            abs(F[j]).max(),
                            1e-12
                        )
                    )

                    if F[i, j] >= 0:
                        y = F[i, j] + offset_y
                        va = "bottom"
                    else:
                        y = F[i, j] - offset_y
                        va = "top"

                    ax_F.text(
                        x[j] + offsets[i],
                        y,
                        f"{ F_diff[j] } %",
                        ha="center",
                        va=va
                    )

            # Moment labels
            for j in range(3):

                if np.isfinite(M_diff[j]) and not (
                    np.isclose( M_diff[j], 0.0 )
                ):

                    offset_y = (
                        0.04
                        * max(
                            abs(M[j]).max(),
                            1e-12
                        )
                    )

                    if M[i, j] >= 0:
                        y = M[i, j] + offset_y
                        va = "bottom"
                    else:
                        y = M[i, j] - offset_y
                        va = "top"

                    ax_M.text(
                        x[j] + offsets[i],
                        y,
                        f"{ M_diff[j] } %",
                        ha="center",
                        va=va
                    )

    # ============================================================
    # Force subplot
    # ============================================================

    ax_F.set_xticks(x)

    ax_F.set_xticklabels([
        r"$F_x$",
        r"$F_y$",
        r"$F_z$"
    ])

    ax_F.set_ylabel("Force [MN]")

    ax_F.axhline(
        0,
        color="black",
        linewidth=0.8
    )

    ax_F.grid(
        True,
        axis="y",
        alpha=0.4
    )

    ax_F.set_axisbelow(True)

    ax_F.legend(loc="lower left")

    # ============================================================
    # Moment subplot
    # ============================================================

    ax_M.set_xticks(x)

    ax_M.set_xticklabels([
        r"$M_x$",
        r"$M_y$",
        r"$M_z$"
    ])

    ax_M.set_ylabel("Moment [MNm]")

    ax_M.axhline(
        0,
        color="black",
        linewidth=0.8
    )

    ax_M.grid(
        True,
        axis="y",
        alpha=0.4
    )

    ax_M.set_axisbelow(True)

    # ============================================================
    # Overall figure
    # ============================================================

    fig.suptitle(
        "Tower-base Loads Comparison"
    )

    fig.tight_layout()

    return fig, axs, F, M

#%%
fig, axs, F, M = plot_tower_base_loads(
    csv_path=csv_all_results,

    design_labels=labels_compr,

    reference_index=0,

    colors= clrs_compr,

    figsize=(17,7),
    show_percent=True,
    percent_decimals=1
)

# save
if False: #flag_save_plots:
    path_twrBaseLoads_compr = os.path.join(
        run_dir, "outputs\\compr_twrBaseLoads.pdf")
    fig.savefig(
        path_twrBaseLoads_compr,
        bbox_inches="tight",
        dpi=300 )

plt.show()

#%%
# ============================================================
# Plot scalar variables for multiple designs
# ============================================================

def plot_comparison_bar_plot_of_float_vars_from_csv(
        csv_path,
        lst_vars,
        name_col="name",
        design_labels=None,
        colors=None,
        ncols=3,
        figsize=None,
        show_percent=True,
        reference_index=0,
        percent_decimals=1,
        title="Maximum Results Comparison",
        loc_save_img=None):
    """
    Compare scalar/float variables between an arbitrary number
    of designs stored as rows of a CSV.

    Parameters
    ----------
    csv_path : str
        Path to comparison CSV.

    lst_vars : list of tuples
        Each tuple must have the form:

            (variable_name, plot_label, unit)

        Example:
            ("raft.Max_Offset", r"$x_{max}$", "[m]")

    name_col : str
        CSV column containing the design names.

    design_labels : list[str] or None
        Optional custom labels for each CSV row/design.
        If None, labels are taken from `name_col`.

    colors : list or None
        Optional list of colors, one per design.
        If None, colors are generated automatically.

    ncols : int
        Maximum number of subplot columns.

    figsize : tuple or None
        Figure size. If None, automatically determined.

    show_percent : bool
        If True, write percentage differences above/below
        non-reference bars.

    reference_index : int
        Design/row treated as the reference for percentage
        differences.

    percent_decimals : int
        Number of decimal places shown in percentage values.

    title : str or None
        Figure title.

    loc_save_img : str or None
        Optional path for saving the figure.

    Returns
    -------
    fig : matplotlib.figure.Figure

    axs : ndarray
        Flat array containing only the active subplot axes.

    values : ndarray
        Shape:
            (n_designs, n_variables)

        values[i, j] is variable j for design i.

    differences : ndarray
        Percentage differences relative to reference_index.
        Same shape as values.
    """

    # ========================================================
    # Read CSV
    # ========================================================

    df = pd.read_csv(csv_path)

    n_designs = len(df)
    nvars = len(lst_vars)

    if n_designs < 1:
        raise ValueError("CSV contains no design rows.")

    if nvars < 1:
        raise ValueError("lst_vars contains no variables.")

    if not 0 <= reference_index < n_designs:
        raise ValueError(
            f"reference_index={reference_index} is invalid for "
            f"{n_designs} designs."
        )

    # ========================================================
    # Check requested variables
    # ========================================================

    missing_vars = [
        var
        for var, _, _ in lst_vars
        if var not in df.columns
    ]

    if missing_vars:
        raise KeyError(
            "The following variables are missing from the CSV:\n"
            + "\n".join(missing_vars)
        )

    # ========================================================
    # Variable labels / units
    # ========================================================

    labels = [
        label
        for _, label, _ in lst_vars
    ]

    units = [
        unit
        for _, _, unit in lst_vars
    ]

    # ========================================================
    # Extract values
    #
    # Shape:
    #     n_designs x nvars
    # ========================================================

    values = np.array(
        [
            [
                float(row[var])
                for var, _, _ in lst_vars
            ]
            for _, row in df.iterrows()
        ],
        dtype=float
    )

    # ========================================================
    # Design labels
    # ========================================================

    if design_labels is None:

        if name_col in df.columns:

            design_labels = (
                df[name_col]
                .astype(str)
                .tolist()
            )

        else:

            design_labels = [
                f"Design {i + 1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must equal the "
            "number of designs/rows in the CSV."
        )

    # ========================================================
    # Colors
    # ========================================================

    if colors is None:

        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    elif len(colors) < n_designs:

        raise ValueError(
            f"{n_designs} designs were found, but only "
            f"{len(colors)} colors were provided."
        )

    # ========================================================
    # Percentage differences relative to reference
    # ========================================================

    ref_values = values[reference_index]

    with np.errstate(
            divide="ignore",
            invalid="ignore"):

        differences = (
            (values - ref_values)
            / ref_values
            * 100.0
        )

    # Reference is exactly zero difference
    differences[reference_index, :] = 0.0

    # ========================================================
    # Subplot arrangement
    # ========================================================

    # Do not create more columns than variables
    ncols_plot = min(ncols, nvars)

    nrows = math.ceil(
        nvars / ncols_plot
    )

    if figsize is None:

        figsize = (
            5.5 * ncols_plot,
            4.5 * nrows
        )

    fig, axs = plt.subplots(
        nrows,
        ncols_plot,
        figsize=figsize,
        squeeze=False
    )

    axs = axs.flatten()

    # ========================================================
    # Adaptive bar positioning
    # ========================================================

    # Total width occupied by one group of bars
    group_width = 0.80

    bar_width = (
        group_width
        / n_designs
    )

    offsets = (
        np.arange(n_designs)
        - (n_designs - 1) / 2
    ) * bar_width

    # ========================================================
    # Plot each variable
    # ========================================================

    for j, ax in enumerate(axs[:nvars]):

        variable_values = values[:, j]

        # ----------------------------------------------------
        # Bars
        # ----------------------------------------------------

        for i in range(n_designs):

            ax.bar(
                offsets[i],
                variable_values[i],
                width=bar_width,
                color=colors[i],
                label=design_labels[i]
            )

        # ----------------------------------------------------
        # Percentage annotations
        # ----------------------------------------------------

        if show_percent:

            scale = max(
                np.max(
                    np.abs(variable_values)
                ),
                1e-12
            )

            text_offset = 0.04 * scale

            for i in range(n_designs):

                # Don't display +0% on reference
                if i == reference_index:
                    continue

                diff = differences[i, j]
                value = variable_values[i]

                if not np.isfinite(diff):
                    continue

                if value >= 0:

                    y = value + text_offset
                    va = "bottom"

                else:

                    y = value - text_offset
                    va = "top"

                ax.text(
                    offsets[i],
                    y,
                    f"{diff:+.{percent_decimals}f}%",
                    ha="center",
                    va=va
                )

        # ----------------------------------------------------
        # Axis formatting
        # ----------------------------------------------------

        ax.set_xticks([0])

        ax.set_xticklabels(
            [labels[j]]
        )

        ax.set_ylabel(
            units[j]
        )

        ax.grid(
            True,
            axis="y",
            alpha=0.4
        )

        ax.set_axisbelow(True)

        ax.axhline(
            0.0,
            color="black",
            # linewidth=0.8
        )

        # Additional space for annotations
        ymin, ymax = ax.get_ylim()

        yrange = ymax - ymin

        if yrange > 0:

            ax.set_ylim(
                ymin - 0.04 * yrange,
                ymax + 0.12 * yrange
            )

    # ========================================================
    # Remove unused subplots
    # ========================================================

    for ax in axs[nvars:]:
        ax.remove()

    # Keep only actually used axes in return
    axs_active = axs[:nvars]

    # ========================================================
    # Legend
    # ========================================================

    axs_active[0].legend()

    # ========================================================
    # Figure title
    # ========================================================

    if title is not None:
        fig.suptitle(title)

    fig.tight_layout()

    # Note:
    # intentionally no plt.show() here.
    # This lets you modify fig/axs afterwards.

    return (
        fig,
        axs_active,
        values,
        differences
    )
#%%
# =================
# Variables
# =================
lst_vars_max = [
    ("raft.Max_Offset",       r"$x_{max}$",           "[m]"),
    ("raft.heave_avg",        r"$z_{avg}$",           "[m]"),
    ("raft.Max_PtfmPitch",    r"$\theta_{max}$",      "[deg]"),
    ("raft.max_nac_accel",    r"$a^{nac}_{max}$",     "[m/s/s]"),
    ("raft.max_tower_base",   r"$M^{TwrBase}_{max}$",   "[Nm]"),
]


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
        title="Maximum Response Comparison"
    )
)

if False: #flag_save_plots:
    path_maxDynamicVariables_compr = os.path.join(
    run_dir, "outputs\\compr_maxDynamicVariables.png")
    fig.savefig(
        path_maxDynamicVariables_compr,
        bbox_inches="tight",
        dpi=300
    )

#%%[markdown]
# ### Plot changes in rigid body periods
#%%
def plot_comparison_bar_plot_of_1Darray_from_csv(
        csv_path,
        lst_vars,
        name_col="name",
        design_labels=None,
        colors=None,
        figsize=(10, 9),
        show_percent=True,
        reference_index=0,
        percent_decimals=1,
        title=None,
    ):

    # ========================================================
    # Read CSV
    # ========================================================

    df = pd.read_csv(csv_path)

    n_designs = len(df)

    if n_designs < 1:
        raise ValueError("CSV contains no design rows.")

    if not 0 <= reference_index < n_designs:
        raise ValueError(
            f"reference_index={reference_index} is invalid "
            f"for {n_designs} designs."
        )

    # ========================================================
    # Design labels
    # ========================================================

    if design_labels is None:

        if name_col in df.columns:
            design_labels = df[name_col].astype(str).tolist()

        else:
            design_labels = [
                f"Design {i + 1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must equal "
            "number of CSV rows/designs."
        )

    # ========================================================
    # Colors
    # ========================================================

    if colors is None:

        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    elif len(colors) < n_designs:

        raise ValueError(
            f"{n_designs} designs found but only "
            f"{len(colors)} colors supplied."
        )

    # ========================================================
    # Parse CSV array
    # ========================================================

    def parse_array(value):

        arr = np.asarray(
            ast.literal_eval(str(value)),
            dtype=float
        )

        return arr.squeeze().flatten()

    # ========================================================
    # Figure
    # ========================================================

    fig, axs = plt.subplots(
        2,
        1,
        figsize=figsize
    )

    all_values = {}
    all_differences = {}

    # Rigid-body modes
    mode_labels = [
        "Surge "    + r"$(x)$",
        "Sway "     + r"$(y)$",
        "Heave "    + r"$(z)$",
        "Roll "     + r"$(\phi)$",
        "Pitch "    + r"$(\theta)$",
        "Yaw "      +r"$(\psi)$",
    ]

    # ========================================================
    # Process variables
    # ========================================================

    for var, label, unit in lst_vars:

        if var not in df.columns:
            raise KeyError(
                f"Variable '{var}' not found in CSV."
            )

        arrays = [
            parse_array(df.iloc[i][var])
            for i in range(n_designs)
        ]

        lengths = [len(arr) for arr in arrays]

        if len(set(lengths)) != 1:
            raise ValueError(
                f"Different array lengths found for "
                f"'{var}': {lengths}"
            )

        n = lengths[0]

        if n != 6:
            raise ValueError(
                f"{var} has {n} elements. "
                "This layout expects the 6 rigid-body modes."
            )

        values = np.vstack(arrays)

        all_values[var] = values

        # ====================================================
        # Percentage differences
        # ====================================================

        ref_values = values[reference_index]

        with np.errstate(
                divide="ignore",
                invalid="ignore"):

            differences = (
                (values - ref_values)
                / ref_values
                * 100.0
            )

        differences[reference_index, :] = 0.0

        all_differences[var] = differences

        # ====================================================
        # Plot groups
        # ====================================================

        groups = [
            (
                axs[0],
                np.array([0, 1, 2]),
                mode_labels[:3]
            ),
            (
                axs[1],
                np.array([3, 4, 5]),
                mode_labels[3:]
            )
        ]

        for ax, indices, labels in groups:

            x = np.arange(len(indices))

            group_width = 0.80

            bar_width = (
                group_width
                / n_designs
            )

            offsets = (
                np.arange(n_designs)
                - (n_designs - 1) / 2
            ) * bar_width

            # ================================================
            # Plot designs
            # ================================================

            for i in range(n_designs):

                ax.bar(
                    x + offsets[i],
                    values[i, indices],
                    width=bar_width,
                    color=colors[i],
                    label=design_labels[i]
                )

            # ================================================
            # Percentage annotations
            # ================================================

            if show_percent:

                subset_values = values[:, indices]

                scale = max(
                    np.max(np.abs(subset_values)),
                    1e-12
                )

                text_offset = 0.025 * scale

                for i in range(n_designs):

                    if i == reference_index:
                        continue

                    for j, idx in enumerate(indices):

                        diff = differences[i, idx]
                        value = values[i, idx]

                        if not np.isfinite(diff):
                            continue

                        if value >= 0:
                            y = value + text_offset
                            va = "bottom"

                        else:
                            y = value - text_offset
                            va = "top"

                        ax.text(
                            x[j] + offsets[i],
                            y,
                            f"{diff:+.{percent_decimals}f}%",
                            ha="center",
                            va=va
                        )

            # ================================================
            # Formatting
            # ================================================

            ax.set_xticks(x)

            ax.set_xticklabels(labels)

            ax.set_ylabel(unit)

            ax.grid(
                True,
                axis="y",
                alpha=0.3
            )

            ax.set_axisbelow(True)

            ax.axhline(
                0.0,
                color="black",
                linewidth=0.8
            )

            # Give % labels additional space
            ymin, ymax = ax.get_ylim()

            yrange = ymax - ymin

            if yrange > 0:

                ax.set_ylim(
                    ymin - 0.03 * yrange,
                    ymax + 0.12 * yrange
                )

    # ========================================================
    # Axis titles
    # ========================================================

    axs[0].set_xlabel(
        "Translational Modes"
    )

    axs[1].set_xlabel(
        "Rotational Modes"
    )

    # only one legend required
    handles, labels = axs[0].get_legend_handles_labels()

    # avoid duplicate entries if lst_vars has >1 variable
    unique = dict(zip(labels, handles))

    axs[0].legend(
        unique.values(),
        unique.keys()
    )

    # ========================================================
    # Figure title
    # ========================================================

    if title is not None:
        fig.suptitle(title)

    fig.tight_layout()

    # ========================================================
    return (
        fig,
        axs,
        all_values,
        all_differences
    )

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
        title="Natural Periods of Rigid Body Modes Comparison"
    )
)

# Save
if False: #flag_save_plots:
    path_compr_RBM = os.path.join( run_dir, "outputs\\compr_RBM.pdf" )
    fig.savefig(
        path_compr_RBM,
        bbox_inches="tight",
        dpi=300
    )

plt.show()

#%%[markdown]
# ### Plot changes in stats (dynamics) of variables with wind speed
#%%
def plot_comparison_windspeed_series_from_csv(
        csv_path,
        lst_vars,
        wind_speeds=None,
        index_start_end=(),
        name_col="name",
        design_labels=None,
        colors=None,
        diff_colors=None,
        figsize=None,
        reference_index=0,
        title="Wind-Speed Response Comparison"):

    df = pd.read_csv(csv_path)

    n_designs = len(df)
    nvars = len(lst_vars)

    if n_designs < 1:
        raise ValueError("CSV contains no design rows.")

    if nvars < 1:
        raise ValueError("lst_vars contains no variables.")

    if not 0 <= reference_index < n_designs:
        raise ValueError(
            f"reference_index={reference_index} is invalid "
            f"for {n_designs} designs."
        )

    # ========================================================
    # Check variables
    # ========================================================

    missing_vars = [
        var
        for var, _, _ in lst_vars
        if var not in df.columns
    ]

    if missing_vars:
        raise KeyError(
            "Variables missing from CSV:\n"
            + "\n".join(missing_vars)
        )

    # ========================================================
    # Design labels
    # ========================================================

    if design_labels is None:

        if name_col in df.columns:
            design_labels = (
                df[name_col]
                .astype(str)
                .tolist()
            )

        else:
            design_labels = [
                f"Design {i + 1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must equal "
            "number of CSV rows/designs."
        )

    # ========================================================
    # Colors
    # ========================================================

    if colors is None:

        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    elif len(colors) < n_designs:

        raise ValueError(
            f"{n_designs} designs found but only "
            f"{len(colors)} colors supplied."
        )

    # Use same colors on difference plots by default
    if diff_colors is None:
        diff_colors = colors

    # ========================================================
    # Helper: parse array from CSV
    # ========================================================

    def parse_array(value):

        arr = np.asarray(
            ast.literal_eval(str(value)),
            dtype=float
        )

        return arr.squeeze().flatten()

    # ========================================================
    # Determine array slice
    # ========================================================

    if len(index_start_end) == 0:

        i_start = 0
        i_end = len(wind_speeds)

    elif len(index_start_end) == 2:

        i_start = index_start_end[0]
        i_end = index_start_end[1]

    else:

        raise ValueError(
            "index_start_end must be empty or "
            "(start_index, end_index)."
        )

    # ========================================================
    # Figure
    #
    # left  = actual values
    # right = percentage difference
    # ========================================================

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

    all_values = {}
    all_differences = {}

    # ========================================================
    # Plot each variable
    # ========================================================

    for j, (var, label, unit) in enumerate(lst_vars):

        ax_val = axs[j, 0]
        ax_diff = axs[j, 1]

        # ----------------------------------------------------
        # Extract values for every design
        # ----------------------------------------------------

        arrays = [
            parse_array(
                df.iloc[i][var]
            )[i_start:i_end]
            for i in range(n_designs)
        ]

        lengths = [
            len(arr)
            for arr in arrays
        ]

        if len(set(lengths)) != 1:

            raise ValueError(
                f"Different array lengths found for "
                f"'{var}': {lengths}"
            )

        n = lengths[0]

        values = np.vstack(arrays)

        all_values[var] = values

        # ----------------------------------------------------
        # Wind-speed x-axis
        # ----------------------------------------------------

        if wind_speeds is None:

            x = np.arange(n)

        else:

            if len(wind_speeds) != n:

                raise ValueError(
                    f"{var}: array length={n}, "
                    f"but len(wind_speeds)="
                    f"{len(wind_speeds)}."
                )

            x = np.asarray(
                wind_speeds,
                dtype=float
            )

        # ----------------------------------------------------
        # Percentage differences
        #
        # Everything relative to reference design
        # ----------------------------------------------------

        ref_values = values[reference_index]

        with np.errstate(
                divide="ignore",
                invalid="ignore"):

            differences = (
                (values - ref_values)
                / ref_values
                * 100.0
            )

        differences[reference_index, :] = 0.0

        all_differences[var] = differences

        # ====================================================
        # LEFT: actual values
        # ====================================================

        for i in range(n_designs):

            ax_val.plot(
                x,
                values[i],
                "-o",
                # linewidth=2,
                color=colors[i],
                label=design_labels[i]
            )

        ax_val.set_title(label)

        ax_val.set_ylabel(unit)

        ax_val.set_xticks(x)

        ax_val.grid(
            True,
            alpha=0.3
        )

        ax_val.set_axisbelow(True)

        # ====================================================
        # RIGHT: percentage differences
        # ====================================================

        for i in range(n_designs):

            # Reference is identically zero,
            # so don't plot another line over y=0
            if i == reference_index:
                continue

            ax_diff.plot(
                x,
                differences[i],
                "-o",
                # linewidth=2,
                color=diff_colors[i],
                label=design_labels[i]
            )

        ax_diff.axhline(
            0.0,
            color="black",
            linestyle="--",
            # linewidth=1
        )

        ax_diff.set_title(
            f"{label}: % Difference"
        )

        ax_diff.set_ylabel("[%]")

        ax_diff.set_xticks(x)

        ax_diff.grid(
            True,
            alpha=0.3
        )

        ax_diff.set_axisbelow(True)

        # ----------------------------------------------------
        # Symmetric difference axis around zero
        # ----------------------------------------------------

        non_ref_diff = np.delete(
            differences,
            reference_index,
            axis=0
        )

        finite_diff = non_ref_diff[
            np.isfinite(non_ref_diff)
        ]

        if finite_diff.size > 0:

            ymax = np.max(
                np.abs(finite_diff)
            )

            if ymax > 0:

                ax_diff.set_ylim(
                    -1.15 * ymax,
                    1.15 * ymax
                )

    # ========================================================
    # X labels
    # ========================================================

    axs[-1, 0].set_xlabel(
        "Wind Speed [m/s]"
    )

    axs[-1, 1].set_xlabel(
        "Wind Speed [m/s]"
    )

    # ========================================================
    # Shared figure-level legend
    # ========================================================

    handles, labels = axs[0, 0].get_legend_handles_labels()

    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.94),
        ncol=n_designs,
        frameon=True,
        fancybox=True
    )

    # ========================================================
    # Figure title
    # ========================================================

    if title is not None:
        fig.suptitle( title, y=0.995 )
        
    fig.tight_layout( rect=[0.0, 0.0, 1.0, 0.95] )

    return (
        fig,
        axs,
        all_values,
        all_differences
    )
# %%
lst_vars_wind = [
    ("raft.stats_surge_max",  r"$x_{max}$",           "[m]"),
    ("raft.stats_Mbase_max",  r"$M^{TwrBase}_{max}$",   "[Nm]"),
    ("raft.stats_AxRNA_max",  r"$a^{RNA}_{max}$",     "[m/s/s]")
]

wind_speeds = [
    3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25
]


fig, axs, values_WS, differences_WS = (
    plot_comparison_windspeed_series_from_csv(
        csv_path=csv_all_results,
        lst_vars=lst_vars_wind,
        wind_speeds=wind_speeds,
        reference_index=0,
        index_start_end=(0,12),

        figsize=(16, 12),
        design_labels=labels_compr,
        colors=["black", "tab:blue", "tab:red"],
        title="Maximum Response vs. Wind-Speed Comparison"
    )
)

if False: #flag_save_plots:
    path_compr_response_with_WS = os.path.join(
        run_dir, "outputs\\compr_response_with_WS.png")
    fig.savefig(
        path_compr_response_with_WS,
        bbox_inches="tight",
        dpi=300
    )

# %%
# Tendon tensions

str_Tmoor = 'raft.stats_Tmoor_max'

csv_iea15 = os.path.join( run_dir, lst_output_folder[0] )

df_iea15 = pd.read_csv(csv_iea15)

dict_iea15 = var_df2dict( df_iea15 )

val_Tmoor = np.asarray( eval(
                str( dict_iea15[ str_Tmoor ] )
                ), dtype=float
            )
val_Tmoor_tendon1_dlc61 = val_Tmoor[-1,1:3]
print(f" Tendon 1 (DLC 6.1) max tension: {val_Tmoor_tendon1_dlc61} N")

# %%
def plot_comparison_Tmoor_windspeed_from_csv(
        csv_path,
        var="raft.stats_Tmoor_max",
        wind_speeds=None,
        index_start_end=(0, 12),
        tendon_index=0,
        name_col="name",
        design_labels=None,
        colors=None,
        figsize=(14, 5),
        reference_index=0,
        title=None):

    df = pd.read_csv(csv_path)

    n_designs = len(df)

    if n_designs < 1:
        raise ValueError("CSV contains no design rows.")

    if not 0 <= reference_index < n_designs:
        raise ValueError(
            f"reference_index={reference_index} is invalid "
            f"for {n_designs} designs."
        )

    if var not in df.columns:
        raise KeyError(
            f"Variable '{var}' not found in CSV."
        )

    # ========================================================
    # Design labels
    # ========================================================

    if design_labels is None:

        if name_col in df.columns:

            design_labels = (
                df[name_col]
                .astype(str)
                .tolist()
            )

        else:

            design_labels = [
                f"Design {i + 1}"
                for i in range(n_designs)
            ]

    if len(design_labels) != n_designs:
        raise ValueError(
            "Number of design_labels must equal "
            "number of CSV rows/designs."
        )

    # ========================================================
    # Colors
    # ========================================================

    if colors is None:

        cmap = plt.get_cmap("tab10")

        colors = [
            cmap(i % 10)
            for i in range(n_designs)
        ]

    elif len(colors) < n_designs:

        raise ValueError(
            f"{n_designs} designs found but only "
            f"{len(colors)} colors supplied."
        )

    # ========================================================
    # Parse 2D array
    # ========================================================

    def parse_2d_array(value):

        arr = np.asarray(
            ast.literal_eval(str(value)),
            dtype=float
        )

        if arr.ndim != 2:
            raise ValueError(
                f"{var} expected to be 2D, "
                f"but received shape {arr.shape}."
            )

        return arr

    # ========================================================
    # Slice definition
    # ========================================================

    if len(index_start_end) != 2:
        raise ValueError(
            "index_start_end must be "
            "(start_index, end_index)."
        )

    i_start, i_end = index_start_end

    # ========================================================
    # Extract selected tendon for every design
    # ========================================================

    values_list = []

    for i in range(n_designs):

        arr = parse_2d_array(
            df.iloc[i][var]
        )

        if tendon_index >= arr.shape[1]:

            raise ValueError(
                f"tendon_index={tendon_index} is invalid. "
                f"{var} has {arr.shape[1]} tendon columns."
            )

        vals = arr[
            i_start:i_end,
            tendon_index
        ]

        values_list.append(vals)

    # Shape:
    #   n_designs x n_wind_speeds

    values = np.vstack(
        values_list
    ) / 1e6

    n = values.shape[1]

    # ========================================================
    # Wind speeds
    # ========================================================

    if wind_speeds is None:

        x = np.arange(n)

    else:

        if len(wind_speeds) != n:

            raise ValueError(
                f"Selected {n} values from {var}, "
                f"but len(wind_speeds)="
                f"{len(wind_speeds)}."
            )

        x = np.asarray(
            wind_speeds,
            dtype=float
        )

    # ========================================================
    # Percentage differences
    # ========================================================

    ref_values = values[reference_index]

    with np.errstate(
            divide="ignore",
            invalid="ignore"):

        differences = (
            (values - ref_values)
            / ref_values
            * 100.0
        )

    differences[reference_index, :] = 0.0

    # ========================================================
    # Plot
    #
    # left  = tendon tension
    # right = difference from reference
    # ========================================================

    fig, axs = plt.subplots(
        1,
        2,
        figsize=figsize
    )

    ax_val = axs[0]
    ax_diff = axs[1]

    # --------------------------------------------------------
    # Actual tension
    # --------------------------------------------------------

    for i in range(n_designs):

        ax_val.plot(
            x,
            values[i],
            "-o",
            linewidth=2,
            color=colors[i],
            label=design_labels[i]
        )

    # ax_val.set_title( f"Tendon {tendon_index + 1} Maximum Tension" )

    ax_val.set_xlabel(
        "Wind Speed [m/s]"
    )
    ax_val.set_xticks(x)

    ax_val.set_ylabel(
        "Tension [MN]"
    )

    ax_val.grid(
        True,
        alpha=0.3
    )

    ax_val.set_axisbelow(True)

    # --------------------------------------------------------
    # Percentage difference
    # --------------------------------------------------------

    for i in range(n_designs):

        if i == reference_index:
            continue

        ax_diff.plot(
            x,
            differences[i],
            "-o",
            linewidth=2,
            color=colors[i],
            label=design_labels[i]
        )

    ax_diff.axhline(
        0.0,
        color="black",
        linestyle="--",
        linewidth=1
    )

    # ax_diff.set_title( "Difference from Reference" )

    ax_diff.set_xlabel(
        "Wind Speed [m/s]"
    )

    ax_diff.set_ylabel(
        "Difference [%]"
    )

    ax_diff.set_xticks(x)

    ax_diff.grid(
        True,
        alpha=0.3
    )

    ax_diff.set_axisbelow(True)

    # ========================================================
    # Shared legend above both plots
    # ========================================================

    handles, legend_labels = (
        ax_val.get_legend_handles_labels()
    )

    fig.legend(
        handles,
        legend_labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.94),
        ncol=n_designs,
        frameon=True,
        fancybox=True
    )

    # ========================================================
    # Title
    # ========================================================

    if title is not None:

        fig.suptitle(
            title,
            y=0.995
        )

    fig.tight_layout(
        rect=[0.0, 0.0, 1.0, 0.99]
    )

    return (
        fig,
        axs,
        values,
        differences
    )
# %%
tendon_index = 0

fig, axs, Tmoor_DLC11, diff_DLC11 = (
    plot_comparison_Tmoor_windspeed_from_csv(
        csv_path=csv_all_results,
        wind_speeds=wind_speeds,
        index_start_end=(0, 12), # (0,12) = DLC 1.1; (12,24) = DLC 1.6
        var = "raft.stats_Tmoor_max",
        tendon_index=tendon_index,
        reference_index=0,
        figsize=(16,6),
        design_labels=labels_compr,
        colors=[
            "black",
            "tab:blue",
            "tab:red"
        ],
        title = f"Tendon {tendon_index+1} Maximum Tensions (DLC 1.1)"
    )
)

if False: #flag_save_plots:
    path_compr_TmoorMax = os.path.join(
        run_dir, "outputs\\compr_TmoorMax_with_WS.pdf")
    fig.savefig(
        path_compr_TmoorMax,
        bbox_inches="tight",
        dpi=300
    )

# %%
