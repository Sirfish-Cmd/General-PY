"""
Google Forms automation script specializing in multi-page navigation.
Focuses exclusively on reliable Next button functionality.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, StaleElementReferenceException
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
    
    # Add these to avoid common errors but remove headless=new which causes issues
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-popup-blocking")
    
    if headless:
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
    
    chrome_options.add_argument("--no-sandbox")
    
    # Add a user agent to avoid detection
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
    if debugger_address:
        chrome_options.add_experimental_option("debuggerAddress", debugger_address)
    
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

###########################################
# FORM FILLING FUNCTIONS
###########################################

def fill_form(driver, iteration, email_text=None):
    """Fill form fields with simplified approach and better error handling."""
    try:
        # TEXT AND EMAIL FIELDS
        text_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea')
        if text_inputs:
            print(f"Found {len(text_inputs)} text/email fields to fill")
            
            for idx, field in enumerate(text_inputs):
                try:
                    # Only interact with visible and enabled fields
                    if field.is_displayed() and field.is_enabled():
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", field)
                        time.sleep(0.3)
                        
                        field.clear()
                        if field.get_attribute('type') == 'email':
                            field.send_keys(f'user{iteration}@example.com')
                        else:
                            field.send_keys(f'Sample Text {iteration}-{idx + 1}')
                        print(f"Filled field {idx+1}")
                except Exception as e:
                    print(f"Could not fill field {idx+1}: {e}")
        else:
            print("No text/email fields found")
        
        # RADIO BUTTONS AND CHECKBOXES
        selectable_elements = driver.find_elements(By.CSS_SELECTOR, 'div[role="radio"], div[role="checkbox"]')
        if selectable_elements:
            print(f"Found {len(selectable_elements)} radio/checkbox options")
            
            # Group radio buttons by container to only select one per question
            radio_groups = {}
            
            for elem in selectable_elements:
                if elem.get_attribute('role') == 'radio':
                    # Try to find parent container
                    try:
                        parent = elem.find_element(By.XPATH, "ancestor::div[contains(@class, 'freebirdFormviewerViewItemsItemItem')]")
                        parent_id = parent.get_attribute('id') or parent.get_attribute('data-item-id') or f"group_{len(radio_groups)}"
                        
                        if parent_id not in radio_groups:
                            radio_groups[parent_id] = []
                        radio_groups[parent_id].append(elem)
                    except:
                        # Fallback if we can't find proper parent
                        if "default_group" not in radio_groups:
                            radio_groups["default_group"] = []
                        radio_groups["default_group"].append(elem)
            
            # Select one option from each radio group
            for group_id, options in radio_groups.items():
                if options:
                    option = random.choice(options)
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", option)
                        time.sleep(0.2)
                        option.click()
                        print(f"Selected radio option in group {group_id}")
                    except Exception as e:
                        print(f"Error selecting radio option: {e}")
            
            # Handle checkboxes
            checkboxes = [elem for elem in selectable_elements if elem.get_attribute('role') == 'checkbox']
            if checkboxes:
                # Select at least one checkbox
                checkbox = random.choice(checkboxes)
                try:
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", checkbox)
                    time.sleep(0.2)
                    checkbox.click()
                    print("Selected a checkbox")
                except Exception as e:
                    print(f"Error selecting checkbox: {e}")
        else:
            print("No radio/checkbox elements found")
        
        # Attempt to handle record email button if provided
        if email_text:
            try:
                email_button = driver.find_element(By.XPATH, f"//span[contains(text(), 'Record {email_text}')]")
                if email_button.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", email_button)
                    time.sleep(0.2)
                    email_button.click()
                    print(f"Recorded email: {email_text}")
            except:
                print("No email recording button found")
        
    except Exception as e:
        print(f"Error during form filling: {e}")

###########################################
# FORM SUBMISSION
###########################################

def wait_for_form_load(driver, timeout=30):
    """Enhanced wait for form loading with multiple element detection strategies."""
    try:
        print("Waiting for form to load...")
        # First check for standard form elements (most common)
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 
                    'input[type="text"], input[type="email"], textarea, div[role="radio"], div[role="checkbox"]'))
            )
            print("Form elements detected successfully")
            return True
        except TimeoutException:
            print("Could not find standard form elements, checking for any form-related elements...")
            
            # Try to find any form-related elements
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        'form, .freebirdFormviewerViewFormContent, .freebirdFormviewerViewItemList'))
                )
                print("Found Google Form container")
                return True
            except TimeoutException:
                # Last resort: Check if the page has any content at all
                body_content = driver.find_element(By.TAG_NAME, 'body').text
                if "question" in body_content.lower() or "form" in body_content.lower():
                    print("Found form content in page body")
                    return True
                    
                print(f"Form did not load properly in {timeout} seconds.")
                print("Current URL:", driver.current_url)
                print("Page title:", driver.title)
                
                # Take a screenshot for debugging
                try:
                    screenshot_path = f"form_load_error_{time.strftime('%Y%m%d_%H%M%S')}.png"
                    driver.save_screenshot(screenshot_path)
                    print(f"Screenshot saved to {screenshot_path}")
                except:
                    pass
                return False
    except Exception as e:
        print(f"Error during form load check: {e}")
        return False

def check_iframes(driver):
    """Check if form is in an iframe and switch to it."""
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"Found {len(iframes)} iframes on page, checking each...")
            
            # Try each iframe
            for i, iframe in enumerate(iframes):
                try:
                    print(f"Switching to iframe {i+1}")
                    driver.switch_to.frame(iframe)
                    
                    # Check if this iframe contains form elements
                    form_elements = driver.find_elements(By.CSS_SELECTOR, 
                        'input[type="text"], input[type="email"], textarea, div[role="radio"], div[role="checkbox"]')
                    
                    if form_elements:
                        print(f"Found form elements in iframe {i+1}")
                        return True
                    
                    # No elements found, switch back to main content
                    driver.switch_to.default_content()
                except Exception as e:
                    print(f"Error checking iframe {i+1}: {e}")
                    driver.switch_to.default_content()
            
            print("No form elements found in any iframe")
        return False
    except Exception as e:
        print(f"Error during iframe check: {e}")
        return False

def find_and_click_button(driver, button_text, fallback_text=None):
    """Generic function to find and click a button by its text content."""
    try:
        # Try multiple selector strategies
        for xpath in [
            f"//span[text()='{button_text}']/ancestor::div[@role='button']",
            f"//div[@role='button']/span[text()='{button_text}']/..",
            f"//div[@role='button'][contains(., '{button_text}')]",
            f"//button[contains(., '{button_text}')]"
        ]:
            try:
                button = driver.find_element(By.XPATH, xpath)
                if button.is_displayed() and button.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.5)
                    button.click()
                    print(f"Clicked '{button_text}' button")
                    return True
            except (NoSuchElementException, ElementNotInteractableException):
                continue
        
        # Try fallback text if provided
        if fallback_text:
            return find_and_click_button(driver, fallback_text)
            
        # Last resort: Look for any button-like element
        buttons = driver.find_elements(By.CSS_SELECTOR, "div[role='button'], button")
        for button in buttons:
            if button.is_displayed() and button.is_enabled():
                text = button.text.strip().lower()
                if button_text.lower() in text or (fallback_text and fallback_text.lower() in text):
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.5)
                    button.click()
                    print(f"Found and clicked button containing '{button_text}'")
                    return True
        
        print(f"No '{button_text}' button found")
        return False
    except Exception as e:
        print(f"Error finding button '{button_text}': {e}")
        return False

def submit_form(driver):
    """Specialized next button handling with fallbacks for edge cases."""
    # First look for Next button with high priority
    if find_and_click_button(driver, "Next", "Continue"):
        print("Found and clicked Next button")
        time.sleep(1)  # Wait for page transition
        return False   # Not done with form
        
    # If Next not found, look for Submit button
    if find_and_click_button(driver, "Submit", "Done"):
        print("Found and clicked Submit button")
        time.sleep(1)  # Wait for submission
        return True    # Form is complete
    
    # If no standard buttons found, try to find any navigation buttons
    buttons = driver.find_elements(By.CSS_SELECTOR, "div[role='button'], button")
    for button in buttons:
        try:
            if button.is_displayed() and button.is_enabled():
                button_text = button.text.strip().lower()
                if any(keyword in button_text for keyword in ["next", "continue", "forward", "submit", "done", "finish"]):
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                    time.sleep(0.5)
                    button.click()
                    print(f"Clicked button with text: {button.text}")
                    time.sleep(1)
                    return "submit" in button_text or "done" in button_text or "finish" in button_text
        except:
            continue
    
    # If we get here, we couldn't find any navigation buttons
    print("No navigation buttons found")
    return False

###########################################
# MAIN AUTOMATION FUNCTION
###########################################

def run_form_automation(form_url, count=100, email=None, headless=False, debug_address=None):
    """Run form automation with improved form loading and navigation focus."""
    driver = None
    try:
        # Set up WebDriver with more reliable options
        driver = setup_driver(debug_address, headless)
        print("WebDriver initialized")
        
        for i in range(1, count + 1):
            print(f"\n========================\nStarting submission {i} of {count}\n========================")
            
            # Load the form with retry logic
            max_retries = 3
            form_loaded = False
            
            for retry in range(max_retries):
                try:
                    print(f"Loading form (attempt {retry+1}/{max_retries})...")
                    driver.get(form_url)
                    
                    # Add a fixed delay for initial page load
                    time.sleep(3)
                    
                    # First check if content is in an iframe
                    if check_iframes(driver):
                        form_loaded = True
                        break
                    
                    # Otherwise check main document
                    if wait_for_form_load(driver):
                        form_loaded = True
                        break
                    
                    # Not loaded properly, retry
                    if retry < max_retries - 1:
                        print("Retrying form load...")
                        time.sleep(2)
                except Exception as e:
                    print(f"Error during form load: {e}")
                    if retry < max_retries - 1:
                        time.sleep(2)
            
            if not form_loaded:
                raise Exception("Failed to load form after multiple attempts")
            
            # Give the form extra time to fully render after initial load
            time.sleep(2)
            print("Form loaded successfully")
            
            # Process form pages with focus on navigation
            page_count = 0
            max_pages = 15  # Increased limit for multi-page forms
            
            form_completed = False
            while not form_completed and page_count < max_pages:
                page_count += 1
                print(f"\nProcessing page {page_count}...")
                
                # Allow extra time for page elements to fully render
                time.sleep(1)
                
                # Fill visible form elements on this page
                fill_form(driver, i, email)
                
                # Allow time for form validation before navigation
                time.sleep(1)
                
                # Navigate using dedicated button handling
                form_completed = submit_form(driver)
                
                # Wait for page transition to complete
                time.sleep(2)
            
            if form_completed:
                print(f"Form {i} completed successfully after {page_count} pages")
            elif page_count >= max_pages:
                print(f"Reached maximum page limit ({max_pages}) without finding a Submit button")
            
            # Pause before next submission
            time.sleep(2)
            
    except Exception as e:
        print(f"Error during form automation: {e}")
        if driver:
            try:
                screenshot_path = f"error_{time.strftime('%Y%m%d_%H%M%S')}.png"
                driver.save_screenshot(screenshot_path)
                print(f"Screenshot saved to {screenshot_path}")
                
                # Also print page source for debugging
                print("\nPage HTML at time of error:")
                print(driver.page_source[:1000] + "...") # Print first 1000 chars
            except:
                pass
        raise  # Re-raise to allow PowerShell to detect the failure
    finally:
        if driver:
            try:
                driver.quit()
                print("Browser closed")
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