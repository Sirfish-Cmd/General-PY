"""
Advanced Google Forms automation script for multi-page forms.
Handles complex form structures with multiple pages and various input types.
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
    """Set up and configure the Chrome WebDriver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-software-rasterizer")
        
    if debugger_address:
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

###########################################
# FORM FIELD HANDLING FUNCTIONS
###########################################

def fill_text_fields(driver, iteration):
    """Fill text and email fields on the current page."""
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

def fill_password_fields(driver, iteration):
    """Fill password fields on the current page."""
    password_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
    for idx, field in enumerate(password_fields):
        try:
            field.clear()
            field.send_keys(f'Password{iteration}_{random.randint(1000, 9999)}')
        except Exception as e:
            print(f"Error filling password field {idx}: {e}")

def select_options(driver):
    """Select radio buttons or checkboxes on the current page."""
    selectable_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="radio"], div[role="checkbox"]')
    for idx, element in enumerate(selectable_elements):
        try:
            element.click()
            time.sleep(0.1)
        except Exception as e:
            print(f"Error selecting option {idx + 1}: {e}")

###########################################
# SPECIAL INTERACTIONS
###########################################

def handle_email_recording(driver, email_text, iteration):
    """Handle the email recording button if present."""
    if not email_text:
        return
        
    try:
        email_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), 'Record {email_text}')]"))
        )
        email_button.click()
        print(f"Email recorded for form {iteration}.")
    except Exception as e:
        print(f"Email button not found or not clickable: {e}")

def navigate_form(driver):
    """Navigate to the next page or submit the form. Returns True if form is submitted."""
    try:
        # Try to find and click the "Submit" button
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        submit_button.click()
        return True
    except:
        try:
            # If "Submit" not found, find and click "Next" button
            next_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]'))
            )
            next_button.click()
            time.sleep(0.5)  # Wait for page transition
            return False
        except Exception as e:
            print(f"Error navigating form: {e}")
            return False

###########################################
# FORM PROCESSING FUNCTIONS
###########################################

def process_form(driver, iteration, email_text=None):
    """Process all pages of a form until completion."""
    try:
        form_completed = False
        page_count = 0
        
        while not form_completed and page_count < 10:  # Limit to 10 pages to prevent infinite loops
            page_count += 1
            print(f"Processing page {page_count} of form {iteration}")
            
            # Handle email recording if needed
            handle_email_recording(driver, email_text, iteration)
            
            # Fill all field types
            fill_text_fields(driver, iteration)
            fill_password_fields(driver, iteration)
            select_options(driver)
            
            # Navigate to next page or submit
            form_completed = navigate_form(driver)
            
        if form_completed:
            print(f"Form {iteration} completed after {page_count} pages")
        else:
            print(f"Form {iteration} might not have been fully completed")
            
    except Exception as e:
        print(f"Error processing form {iteration}: {e}")

###########################################
# MAIN AUTOMATION FUNCTION
###########################################

def run_form_automation(form_url, count=100, email=None, headless=False, debug_address=None):
    """Run automated form submissions for the specified count."""
    driver = setup_driver(debug_address, headless)
    
    try:
        for i in range(1, count + 1):
            print(f"Starting submission {i} of {count}")
            
            # Load the form
            driver.get(form_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea, div[role="radio"], div[role="checkbox"]'))
            )
            
            # Process the entire form
            process_form(driver, i, email)
            
            # Add delay between submissions
            time.sleep(1)
            
    except Exception as e:
        print(f"Error during form automation: {e}")
    finally:
        driver.quit()

###########################################
# SCRIPT EXECUTION
###########################################

if __name__ == "__main__":
    # Replace this with your actual form URL when running the script directly
    # Example: https://docs.google.com/forms/d/e/1FAIpQLSeBgdkmK6KpcOysLOprp1njHzjm8Ow2R-A4jeqvqzFV4B4cYg/viewform
    YOUR_FORM_URL = "https://docs.google.com/forms/d/e/FORM_ID_PLACEHOLDER/viewform"
    
    print("Starting multi-page form automation")
    print("NOTE: Replace FORM_ID_PLACEHOLDER with your actual form ID")
    run_form_automation(YOUR_FORM_URL, count=10)
