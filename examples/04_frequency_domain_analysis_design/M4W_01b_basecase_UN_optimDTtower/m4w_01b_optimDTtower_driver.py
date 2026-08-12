#%%[markdown]
# Status: copy of M4W_01_base_case_UN_TLPwamit, but with optimization of the DT tower
#
# Progress:
# 1. TODO: 

#%%
import os
import numpy as np
from weis import weis_main
from wisdem.inputs.validation import load_yaml
#%%
# Define MDAO flags
TEST_RUN = False # TEST_RUN will reduce the number and duration of simulations

flag_GBO = True # To perform optimization (True) or not (False)

wt_optim = True # turbine to analyse: True = new optim / False = base case

#%%
## File management
run_dir = os.path.dirname( os.path.abspath(__file__) )
basecase_dir = os.path.join( run_dir, os.path.pardir, "M4W_01_base_case_UN_TLPwamit" )

# -- modelling
fname_modeling_options = os.path.join(run_dir, "modelOpts.yaml")

# -- analysis
analysisOpt = os.path.join(run_dir, "analysisOpt.yaml")
analysisNOopt = os.path.join(run_dir, "analysisNOOpt.yaml")

if flag_GBO:
    fname_analysis_options = analysisOpt
else:
    fname_analysis_options = analysisNOopt

# -- geometry
if wt_optim:
    dict_modelOpts = load_yaml(analysisOpt)
    fname_wt_input = os.path.join(
        dict_modelOpts['general']['folder_output'],
        dict_modelOpts['general']['fname_output']
    ) + ".yaml"
else: # base case
    geo_input = "prac_IEA-15-VolturnUS_rect.yaml" 
    fname_wt_input = os.path.join(basecase_dir, geo_input)

#%%
# run WEIS
wt_opt, modeling_options, opt_options = weis_main(fname_wt_input, 
                                                 fname_modeling_options, 
                                                 fname_analysis_options,
                                                 test_run=TEST_RUN
                                                 )

# %%
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

print("\n--- Merit figures ---")
print(f" LCOE [USD/kW/h]: {wt_opt["financese.lcoe"]}")
# -----------------------------------------------------------------------
# %%
