"""
Google Forms automation script with email validation.
Ensures all email inputs have proper format before submission.
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
import re

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
# EMAIL VALIDATION FUNCTIONS
###########################################

def is_valid_email(email):
    """Validate email using regex pattern checking."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_valid_email(iteration):
    """Generate a valid email that passes regex validation."""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
    username = f"user{iteration}.{random.randint(100, 999)}"
    domain = random.choice(domains)
    email = f"{username}@{domain}"
    
    # Verify it passes our regex check
    if not is_valid_email(email):
        # Fallback to a guaranteed valid format
        email = f"user{iteration}@example.com"
    
    return email

###########################################
# FORM FILLING FUNCTIONS
###########################################

def fill_form(driver, iteration, email_text=None):
    """Fill all form fields with validated email data."""
    # TEXT AND EMAIL FIELDS
    text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea')
    for idx, field in enumerate(text_inputs):
        try:
            field.clear()
            if field.get_attribute('type') == 'email':
                # Create a valid email
                valid_email = f'user{iteration}_{random.randint(100, 999)}@example.com'
                print(f"Using validated email: {valid_email}")
                field.send_keys(valid_email)
            else:
                field.send_keys(f'Sample Text {iteration}-{idx + 1}')
        except Exception as e:
            print(f"Error filling text field {idx + 1}: {e}")
    
    # EMAIL RECORDING - with validation
    if email_text:
        try:
            # Validate if it's an email
            if '@' in email_text and not is_valid_email(email_text):
                print(f"Warning: Email '{email_text}' doesn't appear valid, fixing...")
                # Add domain if missing
                if not '.' in email_text.split('@')[1]:
                    email_text = email_text.split('@')[0] + '@example.com'
            
            email_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), 'Record {email_text}')]"))
            )
            email_button.click()
            print(f"Email recorded: {email_text}")
        except Exception as e:
            print(f"Email button not found or not clickable: {e}")
    
    # RADIO BUTTONS AND CHECKBOXES
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
    """Submit form with email validation."""
    # Check all email fields before submitting
    email_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="email"]')
    for field in email_fields:
        try:
            email_value = field.get_attribute('value')
            if email_value and not is_valid_email(email_value):
                print(f"Fixing invalid email: {email_value}")
                field.clear()
                field.send_keys(f"fixed_{random.randint(100,999)}@example.com")
        except:
            pass
    
    # Standard submission process
    try:
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
        submit_button.click()
        return True
    except:
        try:
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
    """Run automated form submissions for the specified count."""
    driver = setup_driver(debug_address, headless)
    
    try:
        for i in range(1, count + 1):
            print(f"Starting submission {i} of {count}")
            
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
            
            print(f"Form {i} submitted successfully.")
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
    # Example: https://docs.google.com/forms/d/e/1FAIpQLSc7Cgqtf7cd46zF0nx4-3E79QAJs80J7We8ANTGGduudFYMng/viewform
    YOUR_FORM_URL = "https://docs.google.com/forms/d/e/FORM_ID_PLACEHOLDER/viewform"
    
    print("Starting form automation")
    print("NOTE: Replace FORM_ID_PLACEHOLDER with your actual form ID")
    run_form_automation(YOUR_FORM_URL, count=10)