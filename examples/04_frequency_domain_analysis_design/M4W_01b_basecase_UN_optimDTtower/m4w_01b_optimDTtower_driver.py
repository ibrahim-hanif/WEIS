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
# TEST_RUN will reduce the number and duration of simulations
TEST_RUN = False # TODO
flag_GBO = False # TODO

wt_innovative = False # turbine to analyse: True = new optim / False = base case

#%%
## File management
run_dir = os.path.dirname( os.path.abspath(__file__) )
basecase_dir = os.path.join( run_dir, os.path.pardir, "M4W_01_base_case_UN_TLPwamit" )
# -- geometry
if wt_innovative:
    geo_input = "geometryOpt.yaml"
    

else: # base case
    geo_input = "prac_IEA-15-VolturnUS_rect.yaml" 
    fname_wt_input = os.path.join(basecase_dir, geo_input)

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
print(" ")
print("--- constr_ max ---")
print("- lss: ",
      np.max(wt_opt["drivese.constr_lss_vonmises"])
      )
print("- bedplate: ",
      np.max(wt_opt["drivese.constr_bedplate_vonmises"])
      )

print("\nTower-top / drivetrain bedplate base loads:")
print(" - base_F: ", wt_opt['drivese.base_F'])
print(" - base_M: ", wt_opt['drivese.base_M'])
#
print("\n--- obj: masses ---")
# print(f"MSA mass: {wt_opt["drivese.msa_mass"]}")
print(f"nacelle mass: {wt_opt["drivese.nacelle_mass"]}")
print(f"nacelle cm: {wt_opt["drivese.nacelle_cm"]}")

print("\n--- RNA properties ---")
print(f"RNA mass: {wt_opt["drivese.rna_mass"]}")
print(f"RNA cm: {wt_opt["drivese.rna_cm"]}")
# -----------------------------------------------------------------------
# %%
