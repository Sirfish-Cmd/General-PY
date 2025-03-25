"""
Main entry point for the form automation package.
Allows running the package directly with 'python -m src'.
"""
import sys
import argparse
from .form_automation import FormAutomator
from .config import FORM_URLS, SUBMISSION_CONFIG

###########################################
# MAIN ENTRY POINT FUNCTION
###########################################

def main():
    """
    Parse command line arguments and run form automation.
    """
    #------------------------------------------
    # COMMAND LINE ARGUMENT PARSING
    #------------------------------------------
    
    parser = argparse.ArgumentParser(description="Automate Google Forms submissions")
    
    parser.add_argument("--url", "-u", 
                        help="Google Form URL to automate", 
                        default=FORM_URLS["general"])
    
    parser.add_argument("--count", "-c", 
                        type=int, 
                        help="Number of submissions to make", 
                        default=SUBMISSION_CONFIG["default_iterations"])
    
    parser.add_argument("--email", "-e", 
                        help="Email text to record in form")
    
    parser.add_argument("--headless", 
                        action="store_true", 
                        help="Run in headless mode")
    
    parser.add_argument("--debug-address", "-d", 
                        help="Chrome debugger address to connect to")
    
    args = parser.parse_args()
    
    #------------------------------------------
    # CONFIGURATION DISPLAY
    #------------------------------------------
    
    print(f"Form Automation Starting with configuration:")
    print(f"  Form URL: {args.url}")
    print(f"  Submissions: {args.count}")
    if args.email:
        print(f"  Email: {args.email}")
    print(f"  Headless: {args.headless}")
    if args.debug_address:
        print(f"  Debug Address: {args.debug_address}")
    print()
    
    #------------------------------------------
    # AUTOMATION EXECUTION
    #------------------------------------------
    
    try:
        automator = FormAutomator(
            form_url=args.url,
            headless=args.headless,
            debug_address=args.debug_address
        )
        
        automator.run_batch(
            count=args.count,
            email_text=args.email
        )
        
        print("Form automation completed successfully!")
        return 0
        
    except Exception as e:
        print(f"Error during form automation: {e}")
        return 1

#------------------------------------------
# SCRIPT EXECUTION
#------------------------------------------

if __name__ == "__main__":
    sys.exit(main())
