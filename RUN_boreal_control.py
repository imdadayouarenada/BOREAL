#!/usr/local/bin/python3.11
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
import utils
import os
import time
import math
from itertools import product
from utils import rename_files
from tqdm import tqdm
from Emailer import Emailer, create_parser 

download_path = "/Users/dada/Documents/RESULTS"
chrome_options = Options()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)
# Headless option is used to use Selenium in headless mode 
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # Disables GPU hardware acceleration. If software renderer is not in place, then the headless browser will not launch on Windows.
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model, MUST BE THE VERY FIRST OPTION.
chrome_options.add_argument("--disable-dev-shm-usage") # Overcome limited resource problems.

# read config file
p = create_parser()
args = p.parse_args()
with open(args.config) as f:
    config = yaml.load(f, Loader=yaml.Loader)

# EMAIL setup
email_config = config["email"]
host, port = email_config["server"]
emailer = Emailer(host, port, email_config["account"], email_config["password"])

################## SELECT WAVELENGTHS TO BE CONSIDERED ################## 
wavelengths_to_select = {
    'extinction' : [1,1,0],
    'backscatter' : [1,1,0],
    'particle depolarization' : [0,1,0],
} 
print(wavelengths_to_select)
################## INPUT VALUES #########################################
extinction = {
    'value' : [116.96, 62.348],
    # 'error' : [0.1, 0.1],
    'error' : [0.0211, 0.0279],
}
backscatter = {
    'value' : [2.3589, 0.95621],
    # 'error' : [0.1, 0.1],
    'error' : [0.0431, 0.0087],
}
particle_depolarization = {
    'value' : [0],
    'error' : [0],
}
try : 
    driver = webdriver.Chrome(options=chrome_options)
    # driver = webdriver.Chrome()
    driver.get("https://boreal.loa.univ-lille.fr/")
    utils.press_button(driver,'clear') # Clear input parameters
    # utils.press_button(driver,'debug') # Allow debug

    ################## INSERTING INPUT PARAMETERS #########################################
    # Select aerosol type
    utils.select_aerosol_type(driver, 'non-absorbing') 
    # Select particle shape model
    utils.select_particle_shape_model(driver, 'sphere') 
    # Select wavlengths 
    utils.select_wavelengths(driver, wavelengths_to_select)
    # Insert extinctions
    utils.input_extinction(driver, extinction)
    # Insert backscatters
    utils.input_backscatter(driver, backscatter)
    # Insert particle depolarization ratios
    utils.input_pd(driver, particle_depolarization)
    ################### STARTING INVERSION ##########################################
    utils.press_button(driver,'submit')
    # time.sleep(60) 
    WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]")))
    ################### SAVING RESULTS ##############################################
    output_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format")))
    output_link.click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    full_text_content = driver.find_element(By.TAG_NAME,'body').text

    # Save the extracted part to a file
    with open('/Users/dada/Documents/RESULTS/Results_Lille30thMay2020/Case01.txt', 'w') as file:
        file.write(full_text_content)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
except Exception as error: 
    inf = traceback.format_exc()
    emailer.add_error(str(error) + "\n" + str(inf))

# # BCN 27th March 2022
# possible_values = [0, 1]
# extinction_combinations = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)] # Extinction valid combinations
# particle_depolarization_combinations = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)] # Particle depolarization valid combinations
# backscatter_combinations = list(product(possible_values, repeat=3)) # All backscatter combinations are allowed

# Lille 20th May 2020
extinction_combinations = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)] # Extinction valid combinations
backscatter_combinations = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)] # Backscatter valid combinations
particle_depolarization_combinations = [(0,0,0)]

################### CREATING ALL POSSIBLE COMBINATIONS #########################
valid_combinations = [] # List to store all possible combinations
for ext in extinction_combinations:
    for back in backscatter_combinations:
        for part in particle_depolarization_combinations:
            total_selected = sum(ext) + sum(back) + sum(part)
            
            current_combination = {
                'extinction': list(ext),
                'backscatter': list(back),
                'particle depolarization': list(part)
            }
            
            # Check if the combination meets the algorithm's criteria: 
            # >= 3, at least on extinction, at least one backscatter
            if (total_selected >= 3 and sum(ext) >= 1 and sum(back) >= 1):
                # Exclude the initial combination
                if current_combination['extinction'] != wavelengths_to_select['extinction'] or current_combination['backscatter'] != wavelengths_to_select['backscatter'] or current_combination['particle depolarization'] != wavelengths_to_select['particle depolarization']:
                    valid_combinations.append({
                        'extinction': ext,
                        'backscatter': back,
                        'particle depolarization': part,
                        'total_selected': total_selected
                    })
                else: 
                    print(current_combination)

n = 2 # Needed to name each file
for combination in tqdm(valid_combinations, desc='Collecting data'):
    # Create again the "wavelengths_to_select"
    wavelengths_to_select = {
        'extinction': combination['extinction'],
        'backscatter': combination['backscatter'],
        'particle depolarization': combination['particle depolarization'],
    }
    print("Starting: ", wavelengths_to_select)
    time.sleep(120)
    utils.select_wavelengths(driver, wavelengths_to_select) 
    ################### STARTING INVERSION ##########################################
    utils.press_button(driver,'submit') 
    WebDriverWait(driver, 300).until(EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]")))
    ################### SAVING RESULTS ##############################################
    time.sleep(60)
    output_link = WebDriverWait(driver, 50).until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format")))
    output_link.click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    full_text_content = driver.find_element(By.TAG_NAME,'body').text


    # Construct the filename
    ext_str = ''.join(map(str, combination['extinction']))
    back_str = ''.join(map(str, combination['backscatter']))
    part_str = ''.join(map(str, combination['particle depolarization']))
    filename = f'/Users/dada/Documents/RESULTS/Results_Lille30thMay2020/Case{n}_{ext_str}_{back_str}_{part_str}.txt'

    # Save the extracted part to a file
    with open(filename, 'w') as file:
        file.write(full_text_content)
    n += 1

    driver.close()
    driver.switch_to.window(driver.window_handles[0])


driver.quit()

with emailer as em: 
    msg = em.send(email_config["to"], email_config["cc"])
    print(msg)