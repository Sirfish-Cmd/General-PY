"""
Core module for automating Google Forms submissions using Selenium.
Provides utilities for form manipulation, submission and driver management.
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
# MAIN AUTOMATION CLASS
###########################################

class FormAutomator:
    """Class to handle automated form submission with various customization options."""
    
    #------------------------------------------
    # INITIALIZATION AND SETUP
    #------------------------------------------
    
    def __init__(self, form_url, headless=False, debug_address=None):
        """Initialize the form automator with the specified URL and configuration."""
        self.form_url = form_url
        self.headless = headless
        self.debug_address = debug_address
        self.driver = self._setup_driver()
        
    def _setup_driver(self):
        """Set up and configure the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        if self.headless:
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-software-rasterizer")
            
        if self.debug_address:
            chrome_options.add_experimental_option("debuggerAddress", self.debug_address)
        
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    #------------------------------------------
    # FORM FIELD HANDLING
    #------------------------------------------
    
    def fill_text_fields(self, prefix, iteration):
        """Fill all text and email input fields in the form."""
        text_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea')
        for idx, field in enumerate(text_inputs):
            try:
                field.clear()
                if field.get_attribute('type') == 'email':
                    field.send_keys(f'{prefix}{iteration}@example.com')
                else:
                    field.send_keys(f'{prefix} {iteration}-{idx + 1}')
            except Exception as e:
                print(f"Error filling text field {idx + 1}: {e}")
    
    def fill_password_fields(self, iteration):
        """Fill all password fields in the form."""
        password_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
        for field in password_fields:
            try:
                field.clear()
                field.send_keys(f'Password{iteration}_{random.randint(1000, 9999)}')
            except Exception as e:
                print(f"Error filling password field: {e}")
    
    def select_options(self):
        """Select radio buttons or checkboxes in the form."""
        selectable_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="radio"], div[role="checkbox"]')
        for idx, element in enumerate(selectable_elements):
            try:
                element.click()
                time.sleep(0.1)
            except Exception as e:
                print(f"Error selecting option {idx + 1}: {e}")
    
    #------------------------------------------
    # SPECIAL INTERACTIONS
    #------------------------------------------
    
    def click_email_button(self, email_text, iteration):
        """Click the button to record email if present."""
        try:
            email_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, f"//span[contains(text(), 'Record {email_text}')]"))
            )
            email_button.click()
            print(f"Email recorded for form {iteration}.")
        except Exception as e:
            print(f"Email button not found or not clickable: {e}")
    
    def submit_form(self):
        """Submit the form by clicking the submit button."""
        try:
            submit_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, '//span[text()="Submit"]/ancestor::div[@role="button"]'))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
            submit_button.click()
            return True
        except Exception as e:
            try:
                next_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[text()="Next"]/ancestor::div[@role="button"]'))
                )
                next_button.click()
                return False
            except Exception as e:
                print(f"Error clicking submit or next button: {e}")
                return False
    
    #------------------------------------------
    # MAIN WORKFLOW METHODS
    #------------------------------------------
    
    def fill_and_submit(self, iteration, email_text=None, text_prefix="TestUser"):
        """Fill and submit a form completely."""
        try:
            self.driver.get(self.form_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="text"], input[type="email"], textarea'))
            )
            
            form_completed = False
            while not form_completed:
                if email_text:
                    self.click_email_button(email_text, iteration)
                
                self.fill_text_fields(text_prefix, iteration)
                self.fill_password_fields(iteration)
                self.select_options()
                
                form_completed = self.submit_form()
            
            print(f"Form {iteration} submitted successfully.")
            time.sleep(1)
            
        except Exception as e:
            print(f"Error with form {iteration}: {e}")
    
    def run_batch(self, count, email_text=None, text_prefix="TestUser"):
        """Run a batch of form submissions."""
        try:
            for i in range(1, count + 1):
                self.fill_and_submit(i, email_text, text_prefix)
        finally:
            self.close()
    
    #------------------------------------------
    # CLEANUP
    #------------------------------------------
    
    def close(self):
        """Close the WebDriver."""
        try:
            self.driver.quit()
        except Exception as e:
            print(f"Error closing driver: {e}")
