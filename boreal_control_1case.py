from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import utils
import os
import time
from itertools import product
from tqdm import tqdm

chrome_options = Options()
chrome_options.add_argument("--headless")  # Run the browser in the background

#-------------------------------------------#
#    SELECT WAVELENGTHS TO BE CONSIDERED    #
#-------------------------------------------#
wavelengths_to_select = {
    'extinction' : [1,1,0],
    'backscatter' : [1,1,1],
    'particle depolarization' : [1,1,0],
} 

#-------------------------------------------#
#          INPUT VALUES DEFINITION          #
#-------------------------------------------#
extinction = {
    'value' : [67.837, 30.308],
    'error' : [0.1283, 0.1480],
}
backscatter = {
    'value' : [1.7279, 1.3920, 0.86137],
    'error' : [0.0418, 0.0483, 0.0336],
}
particle_depolarization = {
    'value' : [0.0992, 0.1377],
    'error' : [0.0399, 0.0707],
}

#-------------------------------------------#
#         OUTPUT DIRECTORY SETUP            #
#-------------------------------------------#
# directory = '/Users/dada/Documents/Selenium/outputs'
directory = '/home/cgile/Documents/boreal/outputs'
if not os.path.exists(directory):
    os.makedirs(directory)

#-------------------------------------------#
#                   MAIN                    #
#-------------------------------------------#
# driver = webdriver.Chrome(options=chrome_options)
driver = webdriver.Chrome()
driver.get("https://boreal.loa.univ-lille.fr/")
utils.press_button(driver,'clear') # Clear input parameters
# utils.press_button(driver,'debug') # Allow debug

#-------------------------------------------#
#       INSERTING INPUT PARAMETERS          #
#-------------------------------------------#
# Select aerosol type
utils.select_aerosol_type(driver, 'dust') 
# Select particle shape model
utils.select_particle_shape_model(driver, 'spheroid') 
# Select wavlengths 
utils.select_wavelengths(driver, wavelengths_to_select)
# Insert extinctions
utils.input_extinction(driver, extinction)
# Insert backscatters
utils.input_backscatter(driver, backscatter)
# Insert particle depolarization ratios
utils.input_pd(driver, particle_depolarization)

#-------------------------------------------#
#            STARTING INVERSION             #
#-------------------------------------------#
utils.press_button(driver,'submit')
# time.sleep(60) 
WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]")))

#-------------------------------------------#
#              SAVING RESULTS               #
#-------------------------------------------#
output_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format")))
output_link.click()
time.sleep(2)
driver.switch_to.window(driver.window_handles[1])
full_text_content = driver.find_element(By.TAG_NAME,'body').text
# Save the results in a file
# file_path = os.path.join(directory, 'Case01_110_111_110.txt')
file_path = os.path.join(directory, '6samples_altitude_1765.txt')
with open(file_path, 'w') as file:
    file.write(full_text_content)
driver.close()
driver.switch_to.window(driver.window_handles[0])
driver.quit()