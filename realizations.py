from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from utils import rename_files
import utils
import os
import time
from itertools import product
from tqdm import tqdm
import numpy as np

chrome_options = Options()
chrome_options.add_argument("--headless")

#-------------------------------------------#
#         OUTPUT DIRECTORY SETUP            #
#-------------------------------------------#
directory = '/Users/dada/Desktop/TFM/EARLINET_Database/LILLE_30_05_2020/Retrieval_Uncertainty'
if not os.path.exists(directory):
    os.makedirs(directory)
print(f'Directory where to save results: {directory}')

#-------------------------------------------#
#      SELECT WAVELENGTHS TO BE USED        #
#-------------------------------------------#
wavelengths_to_select = {
    'extinction': [1, 1, 0],
    'backscatter': [1, 1, 0],
    'particle depolarization': [0, 0, 0],
}

#-------------------------------------------#
#             INPUT PARAMETERS              #
#-------------------------------------------#
# Lille 30th May 2024
ext_355 = {'value': 139.8, 'error': 0.0422}
ext_532 = {'value': 77.305, 'error': 0.0469}
back_355 = {'value': 3.0558, 'error': 0.0746}
back_532 = {'value': 1.1371, 'error': 0.0133}
# back_1064 = {'value': 0.36536, 'error': 0.2049}
# pd_355 = {'value': 0.3710, 'error': 0.2259}
# pd_532 = {'value': 0.4365, 'error': 0.1199}

#-------------------------------------------#
#         GENERATE REALIZATIONS             #
#-------------------------------------------#
n = 100 # Number of realizations
np.random.seed(0) # Seed for reproducibility
ext_355_realizations = np.random.normal(loc=ext_355['value'] , scale=ext_355['error']*ext_355['value'] , size=n)
ext_532_realizations = np.random.normal(loc=ext_532['value'] , scale=ext_532['error']*ext_532['value'] , size=n)

back_355_realizations = np.random.normal(loc=back_355['value'], scale=back_355['error']*back_355['value'], size=n)
back_532_realizations = np.random.normal(loc=back_532['value'], scale=back_532['error']*back_532['value'], size=n)
# back_1064_realizations = np.random.normal(loc=back_1064['value'], scale=back_1064['error']*back_1064['value'], size=n)

# pd_355_realizations = np.random.normal(loc=pd_355['value'] , scale=pd_355['error']*pd_355['value'] , size=n)
# pd_532_realizations = np.random.normal(loc=pd_532['value'] , scale=pd_532['error']*pd_532['value'] , size=n)

#-------------------------------------------#
#          INPUT VALUES DEFINITION          #
#-------------------------------------------#
extinction = {
    'value' : [139.8, 77.305],
    # 'error' : [0.1, 0.1],
    'error' : [0.0422, 0.0469],
}
backscatter = {
    'value' : [3.0558, 1.1371],
    # 'error' : [0.1, 0.1],
    'error' : [0.0746, 0.0133],
}
# particle_depolarization = {
#     'value' : [0.3710, 0.4365],
#     # 'error' : [0.1, 0.1],
#     'error' : [0.2259, 0.1199],
# }

# figure = plt.figure(figsize=(10,10))
# plt.hist(ext_355_realizations, bins=20, density=True, alpha=0.7)
# plt.xlabel('Extinction (355 nm)')
# plt.ylabel('Frequency')
# plt.title('Distribution of Extinction Realizations')
# plt.show()

#-------------------------------------------#
#      STARTING WITH ORIGINAL DATA          #
#-------------------------------------------#
print('Starting Realization 00 (original data)')
# driver = webdriver.Chrome(options=chrome_options)
driver = webdriver.Chrome()
driver.get("https://boreal.loa.univ-lille.fr/")
utils.press_button(driver,'clear') # Clear input parameters
# utils.press_button(driver,'debug') # Allow debug

#-------------------------------------------#
#       INSERTING INPUT PARAMETERS          #
#-------------------------------------------#
# Select aerosol type
utils.select_aerosol_type(driver, 'absorbing') 
# Select particle shape model
utils.select_particle_shape_model(driver, 'sphere') 
# Select wavlengths 
utils.select_wavelengths(driver, wavelengths_to_select)
# Insert extinctions
utils.input_extinction(driver, extinction)
# Insert backscatters
utils.input_backscatter(driver, backscatter)
# # Insert particle depolarization ratios
# utils.input_pd(driver, particle_depolarization)

#-------------------------------------------#
#           STARTING INVERSION              #
#-------------------------------------------#
utils.press_button(driver,'submit')
# time.sleep(60) 
WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]")))

#-------------------------------------------#
#            SAVING RESULTS                 #
#-------------------------------------------#
output_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format")))
output_link.click()
time.sleep(2)
driver.switch_to.window(driver.window_handles[1])
full_text_content = driver.find_element(By.TAG_NAME,'body').text
# file_path = os.path.join(directory, 'Case01_110_111_110.txt')
file_path = os.path.join(directory, f'Realization00_absorbing.txt')
with open(file_path, 'w') as file:
    file.write(full_text_content)

driver.close()
driver.switch_to.window(driver.window_handles[0])

#-------------------------------------------#
#       RUNNING 100 REALIZATIONS            #
#-------------------------------------------#
print('Starting 100 realizations')

for i in tqdm(range(n), desc='100 realizations'):
    utils.press_button(driver,'clear') # Clear input parameters
    extinction = {
    'value' : [ext_355_realizations[i], ext_532_realizations[i]],
    # 'error' : [0.2690, 0.2970],
    'error' : [0.001, 0.001]
    }
    backscatter = {
        'value' : [back_355_realizations[i], back_532_realizations[i]],
        # 'error' : [0.0613, 0.0455, 0.2049],
        'error' : [0.001, 0.001]
    }
    # particle_depolarization = {
    #     'value' : [pd_355_realizations[i], pd_355_realizations[i]],
    #     'error' : [0.2259, 0.1199],
    #     # 'error' : [0.001, 0.001]
    # }
    print(f'Realization: {i+2}')

    print(f'Starting with input parameters:')
    print(f'Extinctions: {extinction}')
    print(f'Backscatter: {backscatter}')
    # print(f'Particle depolarizations: {particle_depolarization}')
    time.sleep(120)
    # Select wavelengths 
    utils.select_wavelengths(driver, wavelengths_to_select)
    # Insert extinctions
    utils.input_extinction(driver, extinction)
    # Insert backscatters
    utils.input_backscatter(driver, backscatter)
    # # Insert particle depolarization ratios
    # utils.input_pd(driver, particle_depolarization)
    
    #-------------------------------------------#
    #           STARTING INVERSION              #
    #-------------------------------------------#
    utils.press_button(driver,'submit') 
    WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]")))
    
    #-------------------------------------------#
    #             SAVING RESULTS                #
    #-------------------------------------------#
    time.sleep(60)
    output_link = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format")))
    output_link.click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    full_text_content = driver.find_element(By.TAG_NAME,'body').text
    filename = f'{directory}/Realization_{i+2}.txt'

    with open(filename, 'w') as file:
        file.write(full_text_content)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])

driver.quit()
