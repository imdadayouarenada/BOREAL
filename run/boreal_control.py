from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import run.utils as utils
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
    'extinction': [1, 1, 0],
    'backscatter': [1, 1, 1],
    'particle depolarization': [1, 1, 0],
}

#-------------------------------------------#
#          INPUT VALUES DEFINITION          #
#-------------------------------------------#
extinction = {
    'value': [67.837, 30.308],
    'error': [0.1283, 0.1480],
}
backscatter = {
    'value': [1.7279, 1.3920, 0.86137],
    'error': [0.0418, 0.0483, 0.0336],
}
particle_depolarization = {
    'value': [0.0992, 0.1377],
    'error': [0.0399, 0.0707],
}

#-------------------------------------------#
#         OUTPUT DIRECTORY SETUP            #
#-------------------------------------------#
directory = '/Users/dada/Documents/Selenium/outputs'
if not os.path.exists(directory):
    os.makedirs(directory)

#-------------------------------------------#
#                 MAIN SCRIPT               #
#-------------------------------------------#
driver = webdriver.Chrome(options=chrome_options)
# driver = webdriver.Chrome()  # Run the browser in the foreground
driver.get("https://boreal.loa.univ-lille.fr/")
utils.press_button(driver, 'clear')  # Clear input parameters
# utils.press_button(driver, 'debug')  # Allow debug

#-------------------------------------------#
#       INSERTING INPUT PARAMETERS          #
#-------------------------------------------#
# Select aerosol type
utils.select_aerosol_type(driver, 'dust')
# Select particle shape model
utils.select_particle_shape_model(driver, 'spheroid')
# Select wavelengths
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
utils.press_button(driver, 'submit')
WebDriverWait(driver, 300).until(
    EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]"))
)

#-------------------------------------------#
#           SAVING INITIAL RESULTS          #
#-------------------------------------------#
output_link = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format"))
)
output_link.click()
time.sleep(2)
driver.switch_to.window(driver.window_handles[1])
full_text_content = driver.find_element(By.TAG_NAME, 'body').text

file_path = os.path.join(directory, '6samples_altitude_1765.txt')
with open(file_path, 'w') as file:
    file.write(full_text_content)
driver.close()
driver.switch_to.window(driver.window_handles[0])

#-------------------------------------------#
#       GENERATE WAVELENGTH COMBINATIONS    #
#-------------------------------------------#
possible_values = [0, 1]
extinction_combinations = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)]  # Extinction valid combinations
particle_depolarization_combinations = [(0, 0, 0), (0, 1, 0), (1, 0, 0), (1, 1, 0)]  # Particle depolarization combinations
backscatter_combinations = list(product(possible_values, repeat=3))  # All backscatter combinations allowed

valid_combinations = []  # Store all valid combinations
for ext in extinction_combinations:
    for back in backscatter_combinations:
        for part in particle_depolarization_combinations:
            total_selected = sum(ext) + sum(back) + sum(part)

            current_combination = {
                'extinction': list(ext),
                'backscatter': list(back),
                'particle depolarization': list(part)
            }
            # Check if combination meets criteria: >= 3, at least one extinction, one backscatter
            if total_selected >= 3 and sum(ext) >= 1 and sum(back) >= 1:
                # Exclude the initial combination
                if (
                    current_combination['extinction'] != wavelengths_to_select['extinction'] or
                    current_combination['backscatter'] != wavelengths_to_select['backscatter'] or
                    current_combination['particle depolarization'] != wavelengths_to_select['particle depolarization']
                ):
                    valid_combinations.append({
                        'extinction': ext,
                        'backscatter': back,
                        'particle depolarization': part,
                        'total_selected': total_selected
                    })

#-------------------------------------------#
#            ITERATION PROCEDURE            #
#-------------------------------------------#
n = 2  # File naming counter
for combination in tqdm(valid_combinations, desc='Collecting data'):
    wavelengths_to_select = {
        'extinction': combination['extinction'],
        'backscatter': combination['backscatter'],
        'particle depolarization': combination['particle depolarization'],
    }
    print("Starting: ", wavelengths_to_select)
    time.sleep(120)
    utils.select_wavelengths(driver, wavelengths_to_select)

    #-------------------------------------------#
    #            STARTING INVERSION             #
    #-------------------------------------------#
    utils.press_button(driver, 'submit')
    WebDriverWait(driver, 300).until(
        EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]"))
    )

    #-------------------------------------------#
    #             SAVING RESULTS                #
    #-------------------------------------------#
    time.sleep(60)
    output_link = WebDriverWait(driver, 50).until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format"))
    )
    output_link.click()
    time.sleep(2)
    driver.switch_to.window(driver.window_handles[1])
    full_text_content = driver.find_element(By.TAG_NAME, 'body').text

    ext_str = ''.join(map(str, combination['extinction']))
    back_str = ''.join(map(str, combination['backscatter']))
    part_str = ''.join(map(str, combination['particle depolarization']))

    filename = f'{directory}/Case{n}_{ext_str}_{back_str}_{part_str}.txt'
    with open(filename, 'w') as file:
        file.write(full_text_content)

    n += 1
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

driver.quit()

