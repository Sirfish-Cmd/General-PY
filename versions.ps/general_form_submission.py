"""
General purpose Google Forms automation script.
Provides functionality for submitting various types of Google Forms.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException, StaleElementReferenceException
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
# FORM FILLING FUNCTIONS
###########################################

def wait_for_form_load(driver, timeout=20):
    """Wait for the form to fully load with explicit error handling."""
    try:
        print("Waiting for form to load...")
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                'input[type="text"], input[type="email"], textarea, div[role="radio"], div[role="checkbox"]'))
        )
        print("Form elements loaded successfully")
        return True
    except TimeoutException:
        print(f"Form did not load properly in {timeout} seconds.")
        print("Current URL:", driver.current_url)
        # Take a screenshot for debugging
        try:
            screenshot_path = f"form_load_error_{time.strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
        except:
            pass
        return False

def fill_form(driver, iteration, email_text=None):
    """Fill all form fields including text, email, password fields and select options."""
    #------------------------------------------
    # TEXT AND EMAIL FIELDS - with improved error handling
    #------------------------------------------
    text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea')
    for idx, field in enumerate(text_inputs):
        try:
            # Add extra wait to ensure element is interactable
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, f".//*[self::textarea or self::input]")))
            driver.execute_script("arguments[0].scrollIntoView(true);", field)
            
            # Clear and fill with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    field.clear()
                    if field.get_attribute('type') == 'email':
                        field.send_keys(f'user{iteration}@example.com')
                    else:
                        field.send_keys(f'Sample Text {iteration}-{idx + 1}')
                    break  # Success, exit retry loop
                except (ElementNotInteractableException, StaleElementReferenceException) as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Retry {attempt+1} for field {idx+1}: {e}")
                    time.sleep(0.5)
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
    for attempt in range(3):  # Try up to 3 times
        try:
            # Try to find and click "Submit"
            try:
                submit_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                time.sleep(0.5)  # Give time for scrolling
                submit_button.click()
                return True
            except:
                # If "Submit" is not found, click "Next"
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)  # Give time for scrolling
                next_button.click()
                return False
        except Exception as e:
            if attempt == 2:  # Last attempt
                print(f"Error clicking submit or next button after 3 attempts: {e}")
                # Try generic button click as last resort
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, 'div[role="button"]')
                    for button in buttons:
                        try:
                            if button.is_displayed() and button.is_enabled():
                                button_text = button.text.lower()
                                if "submit" in button_text or "next" in button_text:
                                    button.click()
                                    return "submit" in button_text
                        except:
                            continue
                except:
                    pass
                return False
            print(f"Attempt {attempt+1} failed: {e}, retrying...")
            time.sleep(1)

###########################################
# MAIN AUTOMATION FUNCTION
###########################################

def run_form_automation(form_url, count=100, email=None, headless=False, debug_address=None):
    """Run automated form submissions for the specified count."""
    try:
        driver = setup_driver(debug_address, headless)
        time.sleep(1)  # Wait for driver to initialize fully
        
        for i in range(1, count + 1):
            print(f"Starting submission {i} of {count}")
            
            # Load the form with retries
            max_retries = 3
            for retry in range(max_retries):
                try:
                    driver.get(form_url)
                    if wait_for_form_load(driver):
                        break
                    if retry == max_retries - 1:
                        raise Exception("Failed to load form after multiple attempts")
                except Exception as e:
                    if retry == max_retries - 1:
                        raise
                    print(f"Form load attempt {retry+1} failed: {e}")
                    time.sleep(2)
            
            # Track form pages
            page_count = 0
            max_pages = 10  # Safety limit
            
            # Process all form pages
            form_completed = False
            while not form_completed and page_count < max_pages:
                page_count += 1
                print(f"Processing page {page_count}...")
                
                # Fill the form
                fill_form(driver, i, email)
                
                # Submit the form
                form_completed = submit_form(driver)
                time.sleep(1)  # Wait for page transition
            
            print(f"Form {i} completed after {page_count} pages")
            time.sleep(1)
            
    except Exception as e:
        print(f"Error during form automation: {e}")
        # Take a screenshot for debugging
        try:
            screenshot_path = f"error_{time.strftime('%Y%m%d_%H%M%S')}.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")
        except:
            pass
        raise  # Re-raise to show real error
    finally:
        try:
            driver.quit()
        except:
            pass

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
