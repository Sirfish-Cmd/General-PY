<#
.SYNOPSIS
    Tests all form automation versions against a specific Google Form.
.DESCRIPTION
    This script runs each version of the form automation code sequentially
    against the same Google Form URL to help identify errors or differences.
.PARAMETER FormUrl
    The URL of the Google Form to test with all versions.
.PARAMETER Count
    Number of form submissions to perform with each version.
.PARAMETER Email
    Email to record in the form if needed.
.PARAMETER Headless
    Run Chrome in headless mode.
.EXAMPLE
    .\Test-AllVersions.ps1 -FormUrl "https://docs.google.com/forms/d/e/your_form_id/viewform" -Count 2
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$FormUrl,
    
    [Parameter(Mandatory=$false)]
    [int]$Count = 1,
    
    [Parameter(Mandatory=$false)]
    [string]$Email = $null,
    
    [Parameter(Mandatory=$false)]
    [switch]$Headless = $false
)

# Define the versions to test
$versions = @(
    "general_form_submission", 
    "v1_next", 
    "v2_incognito", 
    "v3_random", 
    "v4_emailcheck", 
    "FULL_VERSION"
)

# Function to run a test for a given version
function Test-Version {
    param (
        [string]$VersionName
    )
    
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "   TESTING VERSION: $VersionName" -ForegroundColor Cyan
    Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "Form URL: $FormUrl"
    Write-Host "Count: $Count"
    if ($Email) { Write-Host "Email: $Email" }
    Write-Host "Headless Mode: $($Headless.IsPresent)"
    Write-Host ""
    
    # Create temporary Python script
    $tempScript = Join-Path -Path $env:TEMP -ChildPath "form_test_${VersionName}.py"

    # Write import and execution code to temporary file
    @"
import sys
import os
import traceback

# Add the root directory to the path
sys.path.insert(0, os.path.abspath('.'))

# Import the automation function directly
sys.path.insert(0, os.path.abspath('./versions.ps'))

try:
    print(f"Importing version: {os.path.abspath('./versions.ps/${VersionName}.py')}")
    from ${VersionName} import run_form_automation
    
    # Fix URL format if needed
    form_url = '$FormUrl'
    if '/edit' in form_url:
        form_url = form_url.replace('/edit', '/viewform')

    # Run the automation
    run_form_automation(form_url, count=$Count, email='$($Email)', headless=$(if($Headless.IsPresent) { "True" } else { "False" }))
    
    print("Test completed successfully")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: {str(e)}")
    print("Detailed traceback:")
    traceback.print_exc()
    sys.exit(1)
"@ | Out-File -FilePath $tempScript -Encoding utf8

    # Run the automation
    Write-Host "Starting test for version $VersionName..."
    
    $startTime = Get-Date
    python $tempScript
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    $exitCode = $LASTEXITCODE
    if ($exitCode -eq 0) {
        Write-Host "✓ Test for $VersionName completed successfully." -ForegroundColor Green
    } else {
        Write-Host "✗ Test for $VersionName completed with errors (Exit code: $exitCode)." -ForegroundColor Red
    }
    
    Write-Host "Duration: $($duration.TotalSeconds) seconds" -ForegroundColor Yellow
    Write-Host ""
    
    # Clean up
    Remove-Item -Path $tempScript -Force
    
    return $exitCode
}

#------------------------------------------
# MAIN EXECUTION
#------------------------------------------

$results = @{}
$overallStart = Get-Date

foreach ($version in $versions) {
    $exitCode = Test-Version -VersionName $version
    $results[$version] = $exitCode
    
    # Add a short pause between versions to ensure clean browser shutdown
    Write-Host "Pausing for 3 seconds before next test..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 3
}

$overallEnd = Get-Date
$totalDuration = $overallEnd - $overallStart

#------------------------------------------
# SUMMARY REPORT
#------------------------------------------

Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "   SUMMARY REPORT" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "Total test duration: $($totalDuration.TotalMinutes) minutes" -ForegroundColor Yellow
Write-Host ""

$passCount = 0
$failCount = 0

foreach ($version in $versions) {
    if ($results[$version] -eq 0) {
        Write-Host "✓ $version : PASSED" -ForegroundColor Green
        $passCount++
    } else {
        Write-Host "✗ $version : FAILED" -ForegroundColor Red
        $failCount++
    }
}

Write-Host ""
Write-Host "Summary: $passCount passed, $failCount failed" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan

# Return overall success or failure
if ($failCount -gt 0) {
    exit 1
} else {
    exit 0
}
