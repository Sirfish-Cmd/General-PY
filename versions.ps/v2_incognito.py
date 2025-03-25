"""
Google Forms automation script with enhanced privacy features.
Uses incognito mode and clears all cookies and storage on exit.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import random
import time

###########################################
# CONFIGURATION
###########################################

# Generic form URL - replace with actual form URL when using
# Format: https://docs.google.com/forms/d/e/{YOUR_FORM_ID_HERE}/viewform
FORM_URL = "https://docs.google.com/forms/d/e/FORM_ID_PLACEHOLDER/viewform"

###########################################
# DRIVER SETUP
###########################################

def setup_driver(debugger_address=None, headless=False):
    """Set up and configure the Chrome WebDriver with enhanced privacy options."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Use incognito mode for privacy
    chrome_options.add_argument("--incognito")
    
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-software-rasterizer")
        
    if debugger_address:
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Clear cookies and cache on startup
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    
    return driver

###########################################
# FORM FILLING FUNCTIONS
###########################################

def fill_form(driver, iteration, email_text=None):
    """Fill all form fields including text, email, password fields and select options."""
    #------------------------------------------
    # TEXT AND EMAIL FIELDS
    #------------------------------------------
    text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea')
    for idx, field in enumerate(text_inputs):
        try:
            field.clear()
            if field.get_attribute('type') == 'email':
                field.send_keys(f'user{iteration}@example.com')
            else:
                field.send_keys(f'Sample Text {iteration}-{idx + 1}')
        except Exception as e:
            print(f"Error filling text field {idx + 1}: {e}")
    
    #------------------------------------------
    # PASSWORD FIELDS
    #------------------------------------------
    password_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
    for field in password_fields:
        try:
            field.clear()
            field.send_keys(f'Password{iteration}_{random.randint(1000, 9999)}')
        except Exception as e:
            print(f"Error filling password field: {e}")
    
    #------------------------------------------
    # EMAIL RECORDING
    #------------------------------------------
    if email_text:
        try:
            email_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), 'Record {email_text}')]"))
            )
            email_button.click()
            print(f"Email recorded for form {iteration}.")
        except Exception as e:
            print(f"Email button not found or not clickable: {e}")
    
    #------------------------------------------
    # RADIO BUTTONS AND CHECKBOXES
    #------------------------------------------
    selectable_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="radio"], div[role="checkbox"]')
    for idx, element in enumerate(selectable_elements):
        try:
            element.click()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error selecting option {idx + 1}: {e}")

###########################################
# FORM SUBMISSION
###########################################

def submit_form(driver):
    """Submit the form by clicking the submit button or moving to next page."""
    try:
        # Try to find and click "Submit"
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        submit_button.click()
        return True
    except:
        try:
            # If "Submit" is not found, click "Next"
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]'))
            )
            next_button.click()
            return False
        except Exception as e:
            print(f"Error clicking submit or next button: {e}")
            return False

###########################################
# MAIN AUTOMATION FUNCTION
###########################################

def run_form_automation(form_url, count=100, email=None, headless=False, debug_address=None):
    """Run automated form submissions with privacy enhancements."""
    driver = setup_driver(debug_address, headless)
    
    try:
        for i in range(1, count + 1):
            print(f"Starting submission {i} of {count} in incognito mode")
            
            # Load the form
            driver.get(form_url)
            
            # Wait for form to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea, div[role="radio"], div[role="checkbox"]'))
            )
            
            # Process all form pages
            form_completed = False
            while not form_completed:
                fill_form(driver, i, email)
                form_completed = submit_form(driver)
            
            print(f"Form {i} submitted successfully")
            
            # Clear browsing data between submissions
            driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
            time.sleep(1)
            
    except Exception as e:
        print(f"Error during form automation: {e}")
    finally:
        try:
            # Clear local storage before quitting
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
        except:
            pass
        driver.quit()

###########################################
# SCRIPT EXECUTION
###########################################

if __name__ == "__main__":
    # Replace this with your actual form URL when running the script directly
    # Example: https://docs.google.com/forms/d/e/1FAIpQLSc7Cgqtf7cd46zF0nx4-3E79QAJs80J7We8ANTGGduudFYMng/viewform
    YOUR_FORM_URL = "https://docs.google.com/forms/d/e/FORM_ID_PLACEHOLDER/viewform"
    
    print("Starting form automation")
    print("NOTE: Replace FORM_ID_PLACEHOLDER with your actual form ID")
    run_form_automation(YOUR_FORM_URL, count=10)