import os, itertools
import numpy as np
from openfast_io.FileTools import save_yaml

def save_case_matrix(matrix_out, change_vars, dir_matrix, filename_ext=''):
    # save matrix file
    if type(change_vars[0]) is tuple:
        n_header_lines = len(change_vars[0])
    else:
        change_vars = [(var,) for var in change_vars]
        n_header_lines = 1

    n_cases = np.shape(matrix_out)[0]
    matrix_out = np.hstack((np.asarray([[i] for i in range(n_cases)]), matrix_out))

    change_vars = [('Case_ID',)+('',)*(n_header_lines-1)] + change_vars
    # col_len = [max([len(val) for val in matrix_out[:,j]] + [len(change_vars[j][0]), len(change_vars[j][1])]) for j in range(len(change_vars))]
    col_len = [max([len(str(val)) for val in matrix_out[:,j]] + [len(change_vars[j][header_i]) for header_i in range(n_header_lines)]) for j in range(len(change_vars))]

    text_out = []
    for header_i in range(n_header_lines):
        text_out.append(''.join([val.center(col+2) for val, col in zip([var[header_i] for var in change_vars], col_len)])+'\n')

    for row in matrix_out:
        row_str = ''
        for val, col in zip(row, col_len):
            if val is not str:
                val = str(val)
            row_str += val.center(col+2)
        row_str += '\n'
        text_out.append(row_str)

    if not os.path.exists(dir_matrix):
        os.makedirs(dir_matrix)
    ofh = open(os.path.join(dir_matrix,f'case_matrix{filename_ext}.txt'),'w')
    for row in text_out:
        ofh.write(row)
    ofh.close()

def save_case_matrix_yaml(matrix_out, change_vars, dir_matrix, case_names, filename_ext=''):

    matrix_out_yaml = {}
    for var in change_vars:
        matrix_out_yaml[var] = []
    matrix_out_yaml['Case_ID'] = []
    matrix_out_yaml['Case_Name'] = []

    for i, row in enumerate(matrix_out):
        matrix_out_yaml['Case_ID'].append(i)
        matrix_out_yaml['Case_Name'].append(case_names[i])
        for val, var in zip(row, change_vars):
            if type(val) is list:
                if len(val) == 1:
                    val = val[0]
            if type(val) in [np.float32, np.float64, np.single, np.double, np.longdouble]:
                val = float(val)
            elif type(val) in [np.int8, np.int16, np.int32, np.int64, np.uint8, np.uint16, np.uint32, np.uint64, np.intc, np.uintc, np.uint]:
                val = int(val)
            elif type(val) in [np.array, np.ndarray]:
                val = val.tolist()
            elif type(val) in [np.str_]:
                val = str(val)
            # elif len(val) > 0:
            #     val = val.tolist()
            matrix_out_yaml[var].append(val)

    if not os.path.exists(dir_matrix):
        os.makedirs(dir_matrix)

    save_yaml(dir_matrix, f'case_matrix{filename_ext}.yaml', matrix_out_yaml)

def case_naming(n_cases, namebase=None):
    # case naming
    case_name = [('%d'%i).zfill(len('%d'%(n_cases-1))) for i in range(n_cases)]
    if namebase:
        case_name = [namebase+'_'+caseid for caseid in case_name]

    return case_name

def convert_str(val):
    def try_type(val, data_type):
        try:
            data_type(val)
            return True
        except:
            return False
#        return isinstance(val, data_type)  ### this doesn't work b/c of numpy data types; they're not instances of base types
    def try_list(val):
        try:
            val[0]
            return True
        except:
            return False

    if try_type(val, int) and int(val) == float(val):
        return int(val)
    elif try_type(val, float):
        return float(val)
    elif val=='True':
        return True
    elif val=='False':
        return False
    elif try_type(val,str):
        try:
            return(eval(val))
        except Exception:
            return str(val)
    # elif type(val)!=str and try_list(val):
    #     return ", ".join(['{:}'.format(i) for i in val])
    else:
        return val

def CaseGen_General(case_inputs, dir_matrix='', namebase='', save_matrix=True, filename_ext=''):
    """ Cartesian product to enumerate over all combinations of set of variables that are changed together"""

    # put case dict into lists
    change_vars = sorted(case_inputs.keys())
    change_vals = [case_inputs[var]['vals'] for var in change_vars]
    change_group = [case_inputs[var]['group'] for var in change_vars]

    # find number of groups and length of groups
    group_set = list(set(change_group))
    group_len = [len(change_vals[change_group.index(i)]) for i in group_set]

    # case matrix, as indices
    group_idx = [range(n) for n in group_len]
    matrix_idx = list(itertools.product(*group_idx))

    # index of each group
    matrix_group_idx = [np.where([group_i == group_j for group_j in change_group])[0].tolist() for group_i in group_set]

    # build final matrix of variable values
    matrix_out = []
    for i, row in enumerate(matrix_idx):
        row_out = [None]*len(change_vars)
        for j, val in enumerate(row):
            for g in matrix_group_idx[j]:
                row_out[g] = change_vals[g][val]
        matrix_out.append(row_out)
    try:
        matrix_out = np.array([[str(item) for item in row] for row in matrix_out])
    except:
        matrix_out = np.asarray(matrix_out)
    n_cases = np.shape(matrix_out)[0]

    # case naming
    case_name = case_naming(n_cases, namebase=namebase)
    
    # Save case matrix
    if save_matrix:
        if not dir_matrix:
            dir_matrix = os.getcwd()
        try:
            save_case_matrix(matrix_out, change_vars, dir_matrix, filename_ext=filename_ext)
            save_case_matrix_yaml(matrix_out, change_vars, dir_matrix, case_name, filename_ext=filename_ext)
        except: 
            save_case_matrix_yaml(matrix_out, change_vars, dir_matrix, case_name, filename_ext=filename_ext)

    case_list = []
    for i in range(n_cases):
        case_list_i = {}
        for j, var in enumerate(change_vars):
            case_list_i[var] = convert_str(matrix_out[i,j])
        case_list.append(case_list_i)


    return case_list, case_name
"""(v) What CaseGen_General.py does — summary and key details (copilot chat)

Purpose: Generates a set of cases by taking a Cartesian product of input variable sets (with grouping support) and returns:

case_list: a list of dictionaries (one dict per case) mapping variable name → value
case_name: a list of case name strings (zero-padded indices, optionally prefixed by namebase)
Optionally writes out a human-readable text matrix and a YAML (case_matrix.yaml) describing all cases to a specified directory.
Main function: CaseGen_General(case_inputs, dir_matrix='', namebase='', save_matrix=True, filename_ext='')

case_inputs must be a dict where each key is a variable name and each value is a dict with at least:
'vals': list of possible values
'group': an identifier (int/str) that groups variables that should vary together

Behavior:
Sorts variable names and collects values and group IDs.
Builds the Cartesian product over unique groups (so variables in same group change together).
Constructs matrix_out (rows of values for each case), converts items to strings for matrix storage where possible.
Builds zero-padded case names via case_naming.
Optionally saves matrix files:
human-readable text (case_matrix{ext}.txt) produced by save_case_matrix
YAML file (case_matrix{ext}.yaml) produced by save_case_matrix_yaml
Returns (case_list, case_name).
Helper functions

case_naming(n_cases, namebase=None):
Returns zero-padded numeric names (like 00, 01, ...) sized according to max index digits, optionally prefixed by namebase.
convert_str(val):
Tries to coerce string values back to int/float/bool or eval to produce lists/tuples when possible. Falls back to the original value if conversion fails.
Uses small helper try_type to attempt conversion without throwing.
save_case_matrix(matrix_out, change_vars, dir_matrix, filename_ext=''):
Writes a text table with column headers (supports multi-line headers if change_vars items are tuples).
Pads columns to align text.
save_case_matrix_yaml(matrix_out, change_vars, dir_matrix, case_names, filename_ext=''):
Builds a dictionary and converts numpy types into Python types (floats, ints, lists, strings) before calling save_yaml (from openfast_io.FileTools) to write YAML.
Grouping behavior:

Variables that share the same group index vary together. The Cartesian product is over groups, not over all variables independently.
Format and outputs

case_list: Python-native types (converted by convert_str), ready for programmatic use.
case_name: list of strings describing each case.
Files written (if enabled):
case_matrix{filename_ext}.txt — aligned text representation
case_matrix{filename_ext}.yaml — structured YAML with Case_ID and Case_Name and variable columns
"""