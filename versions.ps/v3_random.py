"""
Google Forms automation script with realistic data generation.
Creates natural-looking dummy data for form submissions.
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
import string

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
# FORM FILLING FUNCTIONS
###########################################

def generate_name():
    """Generate random but realistic names."""
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_address():
    """Generate random but realistic addresses."""
    streets = ["Main St", "Oak Ave", "Maple Rd", "Washington Blvd", "Park Dr", 
              "Lake View", "Pine St", "Cedar Ln", "Elm St", "Hill Rd"]
    cities = ["Springfield", "Franklin", "Greenville", "Bristol", "Clinton", 
             "Kingston", "Marion", "Salem", "Georgetown", "Fairview"]
    states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA"]
    
    number = random.randint(100, 9999)
    street = random.choice(streets)
    city = random.choice(cities)
    state = random.choice(states)
    zip_code = random.randint(10000, 99999)
    
    return f"{number} {street}, {city}, {state} {zip_code}"

def generate_phone():
    """Generate random but realistic phone numbers."""
    area_code = random.randint(200, 999)
    prefix = random.randint(200, 999)
    line = random.randint(1000, 9999)
    return f"({area_code}) {prefix}-{line}"

def generate_email(iteration):
    """Generate random email addresses."""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
    return f"user{iteration}_{random.randint(100, 999)}@{random.choice(domains)}"

def fill_form(driver, iteration, email_text=None):
    """Fill all form fields with realistic random data."""
    # TEXT AND EMAIL FIELDS
    text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea')
    for idx, field in enumerate(text_inputs):
        try:
            field.clear()
            field_type = field.get_attribute('type')
            
            # Generate data based on field type
            if field_type == 'email':
                field.send_keys(generate_email(iteration))
            else:
                if idx == 0:  # First field is often name
                    field.send_keys(generate_name())
                else:
                    field.send_keys(f"Random Data {iteration}-{idx}")
        except Exception as e:
            print(f"Error filling text field {idx + 1}: {e}")
    
    # PASSWORD FIELDS
    password_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
    for field in password_fields:
        try:
            field.clear()
            field.send_keys(f'Password{iteration}_{random.randint(1000, 9999)}')
        except Exception as e:
            print(f"Error filling password field: {e}")
    
    # EMAIL RECORDING
    if email_text:
        try:
            email_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), 'Record {email_text}')]"))
            )
            email_button.click()
            print(f"Email recorded for form {iteration}.")
        except Exception as e:
            print(f"Email button not found or not clickable: {e}")
    
    # RADIO BUTTONS AND CHECKBOXES
    radio_buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="radio"]')
    if radio_buttons:
        groups = {}
        for button in radio_buttons:
            # Try to group by parent container
            try:
                parent = button.find_element(By.XPATH, "../..")
                group_id = parent.get_attribute("id")
                if group_id not in groups:
                    groups[group_id] = []
                groups[group_id].append(button)
            except:
                # Fallback to treating all buttons individually
                if "ungrouped" not in groups:
                    groups["ungrouped"] = []
                groups["ungrouped"].append(button)
        
        # Select one random button from each group
        for group_buttons in groups.values():
            if group_buttons:
                try:
                    random.choice(group_buttons).click()
                except Exception as e:
                    print(f"Error selecting radio button: {e}")
    
    # Handle checkboxes
    checkboxes = driver.find_elements(By.CSS_SELECTOR, 'div[role="checkbox"]')
    if checkboxes and len(checkboxes) > 0:
        # Select random number of checkboxes
        num_to_select = min(random.randint(1, 3), len(checkboxes))
        for checkbox in random.sample(checkboxes, num_to_select):
            try:
                checkbox.click()
            except Exception as e:
                print(f"Error selecting checkbox: {e}")

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