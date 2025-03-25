"""
Configuration module for Form Automation settings.
Contains default form URLs and browser configurations.
"""

###########################################
# FORM URL CONFIGURATIONS
###########################################

# Common Google Form URLs - use generic placeholders
# Replace FORM_ID_PLACEHOLDER with your actual form ID when using
FORM_URLS = {
    # Example URL format: https://docs.google.com/forms/d/e/FORM_ID_HERE/viewform
    "general": "https://docs.google.com/forms/d/e/FORM_ID_PLACEHOLDER/viewform",
    "survey": "https://docs.google.com/forms/d/e/FORM_ID_PLACEHOLDER/viewform"
}

###########################################
# BROWSER SETTINGS
###########################################

# Default browser settings
BROWSER_CONFIG = {
    "headless": False,           # Run without visible browser UI
    "debug_port": "9222",        # Default Chrome debugging port
    "debug_address": "127.0.0.1:9222",  # Default debugging address
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

###########################################
# FORM SUBMISSION SETTINGS
###########################################

# Form submission settings
SUBMISSION_CONFIG = {
    "default_iterations": 100,    # Default number of form submissions
    "delay_between_submissions": 1.0,  # Delay in seconds between submissions
    "random_delay": True          # Use random delay between submissions
}

###########################################
# VERSION SCRIPT PATHS
###########################################

# Path to version-specific scripts
VERSION_SCRIPTS = {
    "general": "./versions.ps/general_form_submission.py",
    "multi_page": "./versions.ps/multi_page_form_submission.py"
}
