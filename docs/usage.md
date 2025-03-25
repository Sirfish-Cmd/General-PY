# Usage Guide

## Installation

1. Clone the repository
2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Basic Usage

### Using Python

```python
from src.form_automation import FormAutomator

# Create an instance with your form URL
automator = FormAutomator("https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform")

# Run a batch of submissions
automator.run_batch(10, email_text="your.email@example.com")
```

### Using PowerShell Script

The included PowerShell script makes it easy to run form automation:

```powershell
# Run general form automation
.\Run-FormAutomation.ps1 -FormType general -FormUrl "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" -Count 10

# Run with email recording
.\Run-FormAutomation.ps1 -FormType general -FormUrl "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" -Count 5 -Email "your.email@example.com"

# Run in headless mode
.\Run-FormAutomation.ps1 -FormType multi_page -FormUrl "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" -Headless
```

## Advanced Options

### Headless Mode

Run the browser in headless mode (without UI):

```python
automator = FormAutomator("https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform", headless=True)
```

### Connect to Existing Browser Session

Connect to a running Chrome instance (useful for debugging):

```python
automator = FormAutomator(
    "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform",
    debug_address="127.0.0.1:9222"
)
```

To start Chrome with remote debugging enabled:

```bash
chrome.exe --remote-debugging-port=9222
```

## Customizing Form Submissions

You can customize individual submissions:

```python
automator = FormAutomator("https://your-form-url")

# Custom text prefix for input fields
automator.fill_and_submit(1, text_prefix="CustomUser")

# Custom email handling
automator.fill_and_submit(2, email_text="your.email@example.com")
```
