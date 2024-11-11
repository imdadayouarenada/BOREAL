import numpy as np
import re
import pandas as pd
import glob
import os 
# import chardet


def parse_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as file:
        lines = file.readlines()

    # with open(filepath, 'rb') as file:
    #     raw_data = file.read(10000)  # Reading a portion of the file
    #     result = chardet.detect(raw_data)
    #     encoding = result['encoding']
    # with open(filepath, 'r', encoding=encoding) as file:
    #     lines = file.readlines()

    # Mapping from file parameter names to dictionary keys
    parameter_mapping = {
        'mR': ('mR', 'mean', 'mR', 'std'),
        'mI': ('mI', 'mean', 'mI', 'std'),
        'Vt(um^3/cm^3)': ('Vt', 'mean', 'Vt', 'std'),
        'Reff(um)': ('Reff', 'mean', 'Reff', 'std'),
        'Tot_residual': ('Tot_residual', 'mean' ,'Tot_residual', 'std'),
    }
    # Initialize data for df_type1 with placeholders for each value
    data_type1 = {
        ('IS', ''): None,
        ('mR', 'mean'): np.nan, ('mR', 'std'): np.nan,
        ('mI', 'mean'): np.nan, ('mI', 'std'): np.nan,
        ('Vt(um^3/cm^3)', 'mean'): np.nan, ('Vt(um^3/cm^3)', 'std'): np.nan,
        ('Reff(um)', 'mean'): np.nan, ('Reff(um)', 'std'): np.nan,
        ('Tot_residual', 'mean'): np.nan, ('Tot_residual', 'std'): np.nan,
        ('Warning',''): "no",
        ('Quality factor',''): None,
    }

    # Check for "Warning"
    for line in lines:
        if "Warning" in line:
            data_type1[('Warning','')] = "yes"

    # Extract IS
    # if data_type1[('Warning','')] == "no":
    num_solutions_line = next((line for line in lines if "Num. of selected individual solutions" in line), None)
    if num_solutions_line is None:
        print(f"No 'Num. of selected individual solutions' line found in {filepath}")
        num_solutions = np.nan  # or set to 0 or another appropriate default value
    else:
        num_solutions = int(re.search(r'\d+', num_solutions_line).group())

    data_type1[('IS', '')] = num_solutions
    



    # Extract mR, mI, Vt, Reff, Tot_residual
    start_index = lines.index(" mean std\n") + 1
    end_index = lines.index("r(um) dv/dlnr_mean(um^3/cm^3) dv/dlnr_std(um^3/cm^3)\n")
    section_lines = lines[start_index:end_index]

    for line in section_lines:
        parts = line.split()
        if len(parts) < 3:
            print(f"Skipping line due to unexpected format: {line}")
            continue

        parameter_full, mean, std = parts[0], parts[1], parts[2]
        if parameter_full not in parameter_mapping:
            print(f"Skipping unrecognized parameter: {parameter_full}")
            continue

        try:
            data_type1[(parameter_full, 'mean')] = float(mean)
            # print(float(mean))
            # print(data_type1[(parameter_full, 'mean')])
            data_type1[(parameter_full, 'std')] = float(std)
            # print(float(std))
            # print(data_type1[(parameter_full, 'std')])
        except ValueError as e:
            print(f"Error processing line: '{line.strip()}'. Error: {e}")
    
    
    # Extract Tot_residual and Tot_residual_std
    tot_residual_line = next(line for line in lines if "Tot_residual" in line)
    tot_residual, tot_residual_std = re.findall(r'\d+\.\d+', tot_residual_line)
    data_type1[('Tot_residual', 'mean')] = float(tot_residual)
    data_type1[('Tot_residual', 'std')] = float(tot_residual_std)
    # if data_type1[('Warning','')] == "no":
    data_type1[('Quality factor','')] = num_solutions * float(tot_residual)

    # Create DataFrame for df_type1
    df_type1 = pd.DataFrame(data_type1, index=[os.path.splitext(os.path.basename(filepath))[0]])
    df_type1.columns = pd.MultiIndex.from_tuples([(key, '') if isinstance(key, str) else key for key in df_type1.columns])
    # df_type1 = df_type1.round(2)

    # Create DataFrame of for df_type2
    start_index2 = end_index + 1
    end_index2 = next(i for i, line in enumerate(lines) if "Fittings" in line)
    section_lines2 = lines[start_index2:end_index2]
    section_lines2 = [line for line in section_lines2 if line.strip() and len(line.split()) == 3]
    df_type2 = pd.DataFrame([line.split() for line in section_lines2], columns=['r(um)', 'VSD(um^3/cm^3)', 'VSD_std(um^3/cm^3)'])
    
    filename = os.path.splitext(os.path.basename(filepath))[0]
    df_type1.index = [filename]

    return df_type1, df_type2


# def create_combined_dataframe(folder_path, file_pattern='Case*.txt'):
#     full_pattern = os.path.join(folder_path, file_pattern)
#     filepaths = glob.glob(full_pattern)
    
#     filepaths = sorted(filepaths)
    
#     dataframe_list = []
    
#     for filepath in filepaths:
#         df_type1, _ = parse_file(filepath)
#         dataframe_list.append(df_type1)
    
#     combined_dataframe = pd.concat(dataframe_list, ignore_index=False)
    
#     return combined_dataframe


def create_combined_dataframe(folder_path, file_pattern='Case*.txt'):
    filepaths = glob.glob(os.path.join(folder_path, file_pattern))
    filepaths.sort(key=lambda x: int(re.search(r'Case(\d+)', os.path.basename(x)).group(1)))
    
    dataframe_list = []
    for filepath in filepaths:
        try:
            df_type1, _ = parse_file(filepath)
            dataframe_list.append(df_type1)
        except ValueError as e:
            # Print the name of the file with the error
            print(f"Error in file {os.path.basename(filepath)}: {e}")
            continue  # Skip the rest of the loop and proceed with the next file

    if not dataframe_list:
        return None  # or an empty DataFrame if you prefer

    combined_dataframe = pd.concat(dataframe_list, ignore_index=False)
    return combined_dataframe


