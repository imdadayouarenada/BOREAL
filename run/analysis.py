import pandas as pd
import numpy as np
import run.utils_analysis as utils_analysis
from run.utils_analysis import parse_file, create_combined_dataframe
import os

# # 15 April 2022
# input_folder_path = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_15_04_2022/boreal_outputs/VSD_Column'
# output_folder_path_VSD = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_15_04_2022/boreal_outputs/VSD_Column/VSDs_BCN15thApril2022_altitudes'
# output_folder_path_data = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_15_04_2022/boreal_outputs/VSD_Column/DATA_BCN15thApril2022_altitudes'

# # 27 March 2022
# input_folder_path = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_15_04_2022/boreal_outputs/VSD_Column'
# output_folder_path_VSD = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_15_04_2022/boreal_outputs/VSD_Column/VSDs_BCN15thApril2022_altitudes'
# output_folder_path_data = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_15_04_2022/boreal_outputs/VSD_Column/DATA_BCN15thApril2022_altitudes'

# # 12 April 2024
# input_folder_path = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Boreal_Outputs/VSD_column2'
# output_folder_path_VSD = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Boreal_Outputs/VSD_column2/VSDs_BCN12thApril2024_altitudes_6_samples'
# output_folder_path_data = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Boreal_Outputs/VSD_column2/DATA_BCN12thApril2024_altitudes_6_samples'

# # Retrieval Uncertainty 
# input_folder_path = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Retrieval_Uncertainty'
# output_folder_path_VSD = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Retrieval_Uncertainty_VSDs_BCN12thApril2024'
# output_folder_path_data = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Retrieval_Uncertainty_DATA_BCN12thApril2024'

# # Retrieval Uncertainty 
# input_folder_path = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Retrieval_Uncertainty_right_error_sphere_model'
# output_folder_path_VSD = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Retrieval_Uncertainty_right_error_sphere_model_VSDs_BCN12thApril2024'
# output_folder_path_data = '/Users/dada/Desktop/TFM/EARLINET_Database/FINAL_CASES/BCN_12_04_2024/Retrieval_Uncertainty_right_error_sphere_model_DATA_BCN12thApril2024'

# # Lille 30th May 2024
# input_folder_path = '/Users/dada/Desktop/TFM/EARLINET_Database/LILLE_30_05_2020/Retrieval_Uncertainty/realizations'
# output_folder_path_VSD = '/Users/dada/Desktop/TFM/EARLINET_Database/LILLE_30_05_2020/Retrieval_Uncertainty/VSDs_Lille30thMay2020'
# output_folder_path_data = '/Users/dada/Desktop/TFM/EARLINET_Database/LILLE_30_05_2020/Retrieval_Uncertainty/DATA_Lille30thMay2020'

# EXAMPLE 
input_folder_path = '/home/cgile/Documents/boreal/realizations/realizations'
output_folder_path_VSD = '/home/cgile/Documents/boreal/VSDs_Lille30thMay2020'
output_folder_path_data = '/home/cgile/Documents/boreal/DATA_Lille30thMay2020'

if not os.path.exists(output_folder_path_VSD):
    os.makedirs(output_folder_path_VSD)
if not os.path.exists(output_folder_path_data):
    os.makedirs(output_folder_path_data)

for filename in os.listdir(input_folder_path):
    file_path = os.path.join(input_folder_path, filename)
    
    # Check if it's a file and not a directory
    if os.path.isfile(file_path):
        # Apply processing function
        df1,df2 = parse_file(file_path)
        
        # Construct the output file path
        output_file_path_VSD = os.path.join(output_folder_path_VSD, filename.replace('.txt', '.csv'))
        output_file_path_data = os.path.join(output_folder_path_data, filename.replace('.txt','.csv'))
        
        # Export the DataFrame to CSV
        df2.to_csv(output_file_path_VSD, index=False)
        df1.to_csv(output_file_path_data, index=False)