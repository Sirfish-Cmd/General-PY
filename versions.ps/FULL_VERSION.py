"""
FULL VERSION Google Forms automation script.
Combines all specialized features into one comprehensive solution:
- Next button navigation
- Incognito privacy
- Realistic random data
- Email validation
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
import re

###########################################
# CONFIGURATION
###########################################

# Generic form URL - replace with actual form URL when using
# Format: https://docs.google.com/forms/d/e/{YOUR_FORM_ID_HERE}/viewform
FORM_URL = "https://docs.google.com/forms/d/e/FORM_ID_PLACEHOLDER/viewform"

###########################################
# HELPER FUNCTIONS
###########################################

def is_valid_email(email):
    """Validate email using regex pattern checking."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def generate_name(iteration):
    """Generate random but realistic names."""
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", 
                  "Michael", "Linda", "William", "Elizabeth", "David", "Susan"]
    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", 
                 "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    return f"{first} {last} ({iteration})"

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
    """Generate random valid email addresses."""
    domains = ["gmail.com", "yahoo.com", "outlook.com", "example.com"]
    username = f"user{iteration}.{random.randint(100, 999)}"
    domain = random.choice(domains)
    email = f"{username}@{domain}"
    
    # Verify it passes our regex check from v4_emailcheck
    if not is_valid_email(email):
        email = f"user{iteration}@example.com"
    
    return email

###########################################
# DRIVER SETUP
###########################################

def setup_driver(debugger_address=None, headless=False):
    """Set up and configure the Chrome WebDriver with combined advanced options."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Feature from v2_incognito: incognito mode
    chrome_options.add_argument("--incognito")
    
    # Feature from v2_incognito: cache disabling
    chrome_options.add_argument("--disable-application-cache")
    chrome_options.add_argument("--disk-cache-size=1")
    chrome_options.add_argument("--media-cache-size=1")
    
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-software-rasterizer")
        
    if debugger_address:
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    
    # Create driver with privacy settings
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Feature from v2_incognito: setup memory cleaning
    driver.execute_cdp_cmd('Network.clearBrowserCache', {})
    driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
    
    return driver

###########################################
# FORM FILLING FUNCTIONS
###########################################

def fill_form(driver, iteration, email_text=None):
    """Combined advanced form filling with all features."""
    #------------------------------------------
    # TEXT AND EMAIL FIELDS
    #------------------------------------------
    text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea')
    for idx, field in enumerate(text_inputs):
        try:
            field.clear()
            
            # Smart data generation from v3_random based on field attributes
            field_type = field.get_attribute('type')
            field_name = field.get_attribute('name') or ""
            field_id = field.get_attribute('id') or ""
            field_placeholder = field.get_attribute('placeholder') or ""
            
            # Check field identifiers for common patterns
            field_info = (field_name + field_id + field_placeholder).lower()
            
            # Generate appropriate data based on field type
            if field_type == 'email':
                # Feature from v4_emailcheck: validated email
                valid_email = generate_email(iteration)
                field.send_keys(valid_email)
            elif 'name' in field_info:
                field.send_keys(generate_name(iteration))
            elif any(x in field_info for x in ['address', 'street', 'city']):
                field.send_keys(generate_address())
            elif any(x in field_info for x in ['phone', 'mobile', 'cell']):
                field.send_keys(generate_phone())
            elif 'comment' in field_info or field.tag_name == 'textarea':
                sentences = [
                    "This is a sample response.",
                    "I'm providing feedback as requested.",
                    "Thank you for the opportunity to participate.",
                    "The questions were clear and easy to understand.",
                    "I enjoyed filling out this form."
                ]
                field.send_keys(" ".join(random.sample(sentences, k=min(3, len(sentences)))))
            else:
                # Generic text for unrecognized fields
                field.send_keys(f"Sample data {iteration}-{idx + 1}")
        except Exception as e:
            print(f"Error filling text field {idx + 1}: {e}")
    
    #------------------------------------------
    # PASSWORD FIELDS
    #------------------------------------------
    password_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
    for field in password_fields:
        try:
            field.clear()
            # Generate more secure password with mixed characters
            password = f"Pass{iteration}_{random.randint(1000, 9999)}"
            field.send_keys(password)
        except Exception as e:
            print(f"Error filling password field: {e}")
    
    #------------------------------------------
    # EMAIL RECORDING
    #------------------------------------------
    if email_text:
        try:
            # Feature from v4_emailcheck: validate the email_text
            if '@' in email_text and not is_valid_email(email_text):
                print(f"Warning: The email '{email_text}' doesn't appear to be valid.")
                # Try to fix simple issues
                if not '.' in email_text.split('@')[1]:
                    fixed_email = email_text.split('@')[0] + '@example.com'
                    print(f"Corrected to: {fixed_email}")
                    email_text = fixed_email
            
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
    
    # Feature from v3_random: Group radio buttons by container
    radio_groups = {}
    for elem in selectable_elements:
        if elem.get_attribute('role') == 'radio':
            # Try to find a group identifier
            try:
                # Look up in the DOM to find a parent with a question id
                parent = elem
                for _ in range(5):  # Look at most 5 levels up
                    parent = parent.find_element(By.XPATH, '..')
                    parent_id = parent.get_attribute('id') or parent.get_attribute('data-item-id')
                    if parent_id:
                        if parent_id not in radio_groups:
                            radio_groups[parent_id] = []
                        radio_groups[parent_id].append(elem)
                        break
            except:
                # If we can't group properly, use a default group
                if 'default_radio_group' not in radio_groups:
                    radio_groups['default_radio_group'] = []
                radio_groups['default_radio_group'].append(elem)
    
    # Select one radio button from each group (more realistic)
    for group_name, buttons in radio_groups.items():
        if buttons:
            # Select one random button from each group
            selected_button = random.choice(buttons)
            try:
                selected_button.click()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error selecting radio button: {e}")
    
    # Handle checkboxes separately - select a random number
    checkboxes = [elem for elem in selectable_elements if elem.get_attribute('role') == 'checkbox']
    if checkboxes:
        # Select 1-3 checkboxes or up to the number available
        num_to_select = min(random.randint(1, 3), len(checkboxes))
        selected_boxes = random.sample(checkboxes, num_to_select)
        
        for checkbox in selected_boxes:
            try:
                checkbox.click()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error selecting checkbox: {e}")

###########################################
# FORM SUBMISSION
###########################################

def submit_form(driver):
    """Combined form submission with all features."""
    # Feature from v4_emailcheck: Double-check all email fields have valid format before submitting
    email_fields = driver.find_elements(By.CSS_SELECTOR, 'input[type="email"]')
    for field in email_fields:
        try:
            email_value = field.get_attribute('value')
            if email_value and not is_valid_email(email_value):
                print(f"Warning: Found invalid email '{email_value}' before submission")
                # Generate a new valid email and replace
                valid_email = generate_email(random.randint(1000, 9999))
                field.clear()
                field.send_keys(valid_email)
                print(f"Corrected to: {valid_email}")
        except:
            pass
    
    # Feature from v1_next: Focus on finding the Next button first
    try:
        # Look for the Next button first (v1_next priority)
        next_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]'))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
        next_button.click()
        print("Moving to next page...")
        return False
    except:
        try:
            # If Next button not found, try to find Submit
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            submit_button.click()
            print("Form submitted on final page.")
            return True
        except Exception as e:
            print(f"Error navigating form: {e}")
            return False

###########################################
# MAIN AUTOMATION FUNCTION
###########################################

def run_form_automation(form_url, count=100, email=None, headless=False, debug_address=None):
    """Combined full automation with all features."""
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
            
            # Feature from v1_next: Track pages to prevent infinite loops
            page_count = 0
            max_pages = 20  # Safety limit
            
            # Process all form pages
            form_completed = False
            while not form_completed and page_count < max_pages:
                page_count += 1
                print(f"Processing page {page_count}...")
                
                fill_form(driver, i, email)
                
                # Short pause to ensure form elements are processed before navigation
                time.sleep(0.5)
                form_completed = submit_form(driver)
                
                # Wait for page transition
                time.sleep(0.5)
            
            if form_completed:
                print(f"Form {i} submitted successfully after {page_count} pages.")
            else:
                print(f"Navigation stopped after {page_count} pages without completion.")
            
            # Feature from v2_incognito: Clear browsing data between submissions
            driver.execute_cdp_cmd('Network.clearBrowserCache', {})
            driver.execute_cdp_cmd('Network.clearBrowserCookies', {})
            print("Cleared browsing data for privacy.")
            
            time.sleep(1)
            
    except Exception as e:
        print(f"Error during form automation: {e}")
    finally:
        # Feature from v2_incognito: Final cleanup before quitting
        try:
            driver.execute_script("window.localStorage.clear();")
            driver.execute_script("window.sessionStorage.clear();")
            print("Memory wiped on close for enhanced privacy.")
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
