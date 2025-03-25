<#
.SYNOPSIS
    Runs form automation with various configuration options.
.DESCRIPTION
    This script provides an interface to run the form automation scripts
    with different configurations and form URLs.
.PARAMETER FormType
    Type of form to automate. Options: general, multi_page, v1_next, v2_incognito, v3_random, v4_emailcheck, FULL_VERSION
.PARAMETER FormUrl
    The URL of the Google Form to automate.
.PARAMETER Count
    Number of form submissions to perform.
.PARAMETER Email
    Email to record in the form if needed.
.PARAMETER Headless
    Run Chrome in headless mode.
.EXAMPLE
    .\Run-FormAutomation.ps1 -FormType general -FormUrl "https://docs.google.com/forms/d/e/your_form_id/viewform" -Count 10
#>

param (
    [Parameter(Mandatory=$true)]
    [ValidateSet("general", "multi_page", "v1_next", "v2_incognito", "v3_random", "v4_emailcheck", "FULL_VERSION")]
    [string]$FormType,
    
    [Parameter(Mandatory=$true)]
    [string]$FormUrl,
    
    [Parameter(Mandatory=$false)]
    [int]$Count = 10,
    
    [Parameter(Mandatory=$false)]
    [string]$Email = $null,
    
    [Parameter(Mandatory=$false)]
    [switch]$Headless = $false
)

# Ensure required directories exist
$requiredDirs = @("src", "tests", "data", "docs", "versions.ps")
foreach ($dir in $requiredDirs) {
    $dirPath = Join-Path -Path $PSScriptRoot -ChildPath $dir
    if (-not (Test-Path -Path $dirPath)) {
        Write-Host "Creating directory: $dir" -ForegroundColor Yellow
        New-Item -Path $dirPath -ItemType Directory | Out-Null
    }
}

# Validate Python installation
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH"
    exit 1
}

# Validate required modules
$requiredModules = @("selenium", "webdriver-manager")
foreach ($module in $requiredModules) {
    $moduleInstalled = python -c "import $module" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "Module '$module' is not installed. Installing..."
        pip install $module
    }
}

# Create temporary Python script
$tempScript = Join-Path -Path $env:TEMP -ChildPath "form_automation_temp.py"

# Handle FormType transformations for general and multi_page
$importName = $FormType
if ($FormType -eq "general") {
    $importName = "general_form_submission"
} elseif ($FormType -eq "multi_page") {
    $importName = "multi_page_form_submission"
}

# Write import and execution code to temporary file
@"
import sys
import os

# Add the root directory to the path
sys.path.insert(0, os.path.abspath('.'))

# Import the automation function directly
sys.path.insert(0, os.path.abspath('./versions.ps'))
from ${importName} import run_form_automation

# Fix URL format if needed
form_url = '$FormUrl'
if '/edit' in form_url:
    form_url = form_url.replace('/edit', '/viewform')

print(f"Running form automation with URL: {form_url}")
# Run the automation
run_form_automation(form_url, count=$Count, email='$($Email)', headless=$(if($Headless.IsPresent) { "True" } else { "False" }))
"@ | Out-File -FilePath $tempScript -Encoding utf8

# Run the automation
Write-Host "Running form automation with the following settings:"
Write-Host "Form Type: $FormType"
Write-Host "Form URL: $FormUrl"
Write-Host "Submissions: $Count"
if ($Email) { Write-Host "Email: $Email" }
Write-Host "Headless Mode: $($Headless.IsPresent)"
Write-Host ""
Write-Host "Starting automation..."

python $tempScript

$exitCode = $LASTEXITCODE
if ($exitCode -eq 0) {
    Write-Host "Form automation completed successfully." -ForegroundColor Green
} else {
    Write-Host "Form automation completed with errors (Exit code: $exitCode)." -ForegroundColor Red
}

# Clean up
Remove-Item -Path $tempScript -Force

exit $exitCode
