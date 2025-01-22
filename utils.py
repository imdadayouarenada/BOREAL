from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import math
import os

xpaths_extinction = {
    'value' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[2]/div[2]/input', # XPath for 355
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[2]/div[3]/input', # XPath for 532 
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[2]/div[4]/input', # XPath for 1064
    ],
    'error' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[3]/div[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[3]/div[3]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[3]/div[4]/input',
    ]
}
xpaths_backscatter = {
        'value' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[2]/div[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[2]/div[3]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[2]/div[4]/input',
        ],
        'error' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[3]/div[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[3]/div[3]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[3]/div[4]/input',           
        ]
}
xpaths_particle_depolarization = {
    'value' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[2]/div[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[2]/div[3]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[2]/div[4]/input',
    ],
    'error' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[3]/div[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[3]/div[3]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[3]/div[4]/input',
    ]
}
wavelengths_xpaths = {
    'extinction' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[1]/div[2]/label[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[1]/div[3]/label[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[5]/div/div/div[1]/div[4]/label[2]/input',
    ], 
    'backscatter' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[1]/div[2]/label[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[1]/div[3]/label[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[7]/div/div/div[1]/div[4]/label[2]/input',
    ], 
    'particle depolarization' : [
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[1]/div[2]/label[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[1]/div[3]/label[2]/input',
        '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[9]/div/div/div[1]/div[4]/label[2]/input',
    ]
}
button_paths = {
    'clear' : '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[10]/div/div/button[3]',
    'submit' : '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[10]/div/div/button[1]',
    'debug' : '/html/body/div/div[2]/div/div/div[6]/div/div/div[2]/div[10]/div/div/div/label[2]/input',
}

# FUNCTION TO PRESS CLEAR OR SUBMIT INPUTS
def press_button(driver, what_button):
    try:
        button = None
        if what_button == 'clear':
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_paths['clear']))
            )
            button.click()
        elif what_button == 'submit':
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_paths['submit']))
            )
            button.click()
        elif what_button == 'debug':
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_paths['debug']))
            )
            if not button.is_selected():
                button.click()
        else:
            print("Wrong button option, it should be 'clear', 'submit' or 'debug'.")
    
    except Exception as e:
        print(f"An error occurred when trying to press '{what_button}' button: {e}")

# FUNCTION TO SELECT THE AEROSOL TYPE
def select_aerosol_type(driver, aerosol_type):
    aerosol_types = {
        'absorbing': '0',
        'dust': '1',
        'non-absorbing': '2'
    }

    value_to_select = aerosol_types.get(aerosol_type.lower())
    if value_to_select is not None:
        radio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                f"div[style='margin-bottom: 2px;'] input[type='radio'][value='{value_to_select}']"))
        )
        radio_button.click()
    else:
        print(f"Aerosol type '{aerosol_type}' is not recognized.")

# FUNCTION TO SELECT THE SHAPE MODEL 
def select_particle_shape_model(driver, shape_model):
    model_values = {
        'sphere': '0',
        'spheroid': '1'
    }

    value_to_select = model_values.get(shape_model.lower())
    if value_to_select is not None:
        # Using inline style for selection
        radio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                f"div[style='margin-bottom: 2px;'] input[type='radio'][value='{value_to_select}']"))
        )
        radio_button.click()
    else:
        print(f"Particle shape model '{shape_model}' is not recognized.")

# FUNCTION TO SELECT WAVELENGTHS
def select_wavelengths(driver, wavelengths_to_select):
    for parameter, vector in wavelengths_to_select.items():
        xpaths_to_use = wavelengths_xpaths[parameter]
        for index, select in enumerate(vector):
            try:
                checkbox = driver.find_element(By.XPATH, xpaths_to_use[index])
                if select == 1 and not checkbox.is_selected():
                    checkbox.click()
                elif select == 0 and checkbox.is_selected():
                    checkbox.click()
            except Exception as e:
                action = "selecting" if select == 1 else "un-selecting"
                print(f"An error occurred in {action} path for {parameter}: {e}")

def input_extinction(driver, extinction):
    for xpath, value in zip(xpaths_extinction['value'], extinction['value']):
        try: 
            input_element_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            ) 
            input_element_box.send_keys(str(value))  
        except Exception as e:
            print(f"An error occurred while inputting value {value} with XPath {xpath}: {e}")
    for xpath, error in zip(xpaths_extinction['error'], extinction['error']):
        try: 
            input_element_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )  
            input_element_box.send_keys(str(error)) 
        except Exception as e: 
            print(f"An error occurred while inputting value {error} with XPath {xpath}: {e}")

# FUNCTION TO PUT BACKSCATTERS (VALUES & ERRORS)
def input_backscatter(driver, backscatter):
    for xpath, value in zip(xpaths_backscatter['value'], backscatter['value']):
        try: 
            input_element_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            ) 
            input_element_box.send_keys(str(value))
        except Exception as e:
            print(f"An error occurred while inputting value {value} with XPath {xpath}: {e}")
    for xpath, error in zip(xpaths_backscatter['error'], backscatter['error']):
        try: 
            input_element_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )  
            input_element_box.send_keys(str(error))
        except Exception as e: 
            print(f"An error occurred while inputting value {error} with XPath {xpath}: {e}")

# FUNCTION TO PUT PARTICLE DEPOLARIZATION RATIOS (VALUES & ERRORS)
def input_pd(driver, particle_depolarization):
    for xpath, value in zip(xpaths_particle_depolarization['value'], particle_depolarization['value']):
        try: 
            input_element_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            ) 
            input_element_box.send_keys(str(value))
        except Exception as e:
            print(f"An error occurred while inputting value {value} with XPath {xpath}: {e}")
    for xpath, error in zip(xpaths_particle_depolarization['error'], particle_depolarization['error']):
        try: 
            input_element_box = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )  
            input_element_box.send_keys(str(error))
        except Exception as e: 
            print(f"An error occurred while inputting value {error} with XPath {xpath}: {e}")

# FUNCTION TO CHECK INVALID INPUTS
def check_input_value(driver, xpath):
    input_element_box = driver.find_element(By.XPATH, xpath)
    value_str = input_element_box.get_attribute('value')
    try:
        value = float(value_str)
        if not is_valid_number(value):
            raise ValueError(f"The value {value_str} is not a valid number.")
    except ValueError as e:
        print(f"Validation failed for input at {xpath}: {e}")
        return False
    return True

def is_valid_number(value):
    return not (math.isnan(value) or math.isinf(value))
        
def trigger_change_event(driver, element):
    driver.execute_script("arguments[0].dispatchEvent(new Event('change'))", element)
    driver.execute_script("arguments[0].dispatchEvent(new Event('blur'))", element)

def rename_files(directory_path, combinations):
    # Iterate over each file in the directory
    for idx, file in enumerate(sorted(os.listdir(directory_path))):
        if file.endswith(".txt"):
            if idx < len(combinations):
                combo = combinations[idx]
                # Format the values from the combination dictionary
                extinction = "".join(map(str, combo['extinction']))
                backscatter = "".join(map(str, combo['backscatter']))
                particle_depolarization = "".join(map(str, combo['particle depolarization']))
                # Generate the new file name
                new_name = f"Case{idx+1}_{extinction}_{backscatter}_{particle_depolarization}.txt"
                old_file_path = os.path.join(directory_path, file)
                new_file_path = os.path.join(directory_path, new_name)
                # Rename the file
                os.rename(old_file_path, new_file_path)
                print(f"Renamed {file} to {new_name}")
            else:
                print("Not enough combinations for the number of files.")
                break
    print("Renaming complete.")




