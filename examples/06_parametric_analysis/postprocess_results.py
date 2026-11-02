#%%
"""
Simple script to show how to grab all cases from a DOE run. User can then
postprocess or plot further.
"""

import glob
import os

import numpy as np
import pandas as pd 
import multiprocessing as mp 

import openmdao.api as om

def load_OMsql(log):
    print("loading {}".format(log))
    cr = om.CaseReader(log)
    rec_data = {}
    #driver_cases = cr.list_cases("driver")
    cases = cr.get_cases("driver")
    for case in cases:
        for key in case.outputs.keys():
            if key not in rec_data:
                rec_data[key] = []
            rec_data[key].append(case[key])
        
    return rec_data
#%%
# (Vasudev Gupta) added this function, on 20.8.2026
def save_csv_of_parametric_runs( post_multi, dir_sql_output ):
    """
    Inputs
    _______
    post_multi: bool

        use Multiprocssing?

    dir_sql_output: str

        path to directory of outputs from sql of DOE runs
    """
    doe_logs = glob.glob(os.path.join(dir_sql_output,"log_opt.sql*"))
    if len(doe_logs) < 1:
        raise FileExistsError("No output logs to post process!")
        
    # Remove the "meta" log
    for idx, log in enumerate(doe_logs):
        if "meta" in log:
            doe_logs.pop(idx)

    # run multiprocessing
    if post_multi:
        cores = mp.cpu_count()
        pool = mp.Pool(min(len(doe_logs), cores))

        # load sql file
        outdata = pool.map(load_OMsql, doe_logs)
        pool.close()
        pool.join()
    # no multiprocessing
    else:
        outdata = [load_OMsql(log) for log in doe_logs]

    collected_data = {}
    for data in outdata:
        for key in data.keys():
            if key not in collected_data.keys():
                collected_data[key] = []

            for key_idx, _ in enumerate(data[key]):
                if isinstance(data[key][key_idx], int):
                    collected_data[key].append(np.array(data[key][key_idx]))
                elif len(data[key][key_idx]) == 1:
                    try:
                        collected_data[key].append(np.array(data[key][key_idx][0]))
                    except:
                        collected_data[key].append(np.array(data[key][key_idx]))
                else:
                    collected_data[key].append(np.array(data[key][key_idx]))

    df = pd.DataFrame.from_dict(collected_data)
    
    # write to file
    outdata_fname = "doe_outdata"
    outdata_fpath = os.path.join(dir_sql_output,outdata_fname) 
    df.to_csv(outdata_fpath + ".csv", index=False)
    print("Saved {}".format(outdata_fpath + ".csv"))
    # FileTools.save_yaml(output_dir, outdata_fname + ".yaml", collected_data, package=2)   

#%%
if __name__ == "__main__":
    # Multiprocssing?
    post_multi = True

    # sql outfile directory
    run_dir = os.path.dirname(os.path.realpath(__file__))   
    output_dir = os.path.join(run_dir, "outputs/06_raft_doe") # def: 06_openfast_doe
    save_csv_of_parametric_runs(post_multi,output_dir)
