# from selenium import webdriver
# from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# from utils import select_aerosol_type
# from utils import select_particle_shape_model
import panda as pd

import os
import time

download_path = "/Users/dada/Desktop/TFM/EARLINET Database/BCN_27_03_2022"

chrome_options = Options()
prefs = {
    "download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
chrome_options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://boreal.loa.univ-lille.fr/")

wait = WebDriverWait(driver, 20) 
submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".widget-button")))
submit_button.click()

time.sleep(60)
wait = WebDriverWait(driver, timeout=300)  # Adjust the timeout as needed
wait.until(EC.visibility_of_element_located((By.XPATH, "//pre[contains(text(), 'Finished the inversion at')]")))

output_link = wait.until(EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "Output results in text format")))
output_link.click()

time.sleep(10)

driver.switch_to.window(driver.window_handles[1])

full_text_content = driver.find_element(By.TAG_NAME,'body').text

# Define the start and end markers
start_marker = "******************************   Retrievals   ******************************"
end_marker = "******************************   Fittings   ******************************"

# Find the start and end
start_index = full_text_content.find(start_marker) + len(start_marker)
end_index = full_text_content.find(end_marker)

# Extract the specific part of the text
specific_text_content = full_text_content[start_index:end_index].strip()

# Save the extracted part to a file
with open('/Users/dada/Desktop/TFM/EARLINET Database/BCN_27_03_2022/prova.txt', 'w') as file:
    file.write(specific_text_content)

driver.close()
driver.switch_to.window(driver.window_handles[0])


driver.quit()

df = pd.read_csv('prova.txt', sep=",")
