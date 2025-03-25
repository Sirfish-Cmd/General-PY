<#
.SYNOPSIS
    Cleans up the project by removing extra files and keeping only the essential structure.
.DESCRIPTION
    This script removes all unnecessary files from the project directory,
    maintaining only the core files needed for the SeleniumMeadow project.
#>

# Define the essential directories and files to keep
$essentialPaths = @(
    "src",
    "tests",
    "data",
    "docs",
    "versions.ps",
    "README.md",
    "requirements.txt",
    "Run-FormAutomation.ps1",
    "Clean-Project.ps1",
    ".gitignore"
)

# Get the current script directory
$projectRoot = $PSScriptRoot

# Function to check if a path should be preserved
function ShouldPreserve($path) {
    foreach ($essential in $essentialPaths) {
        $fullEssentialPath = Join-Path -Path $projectRoot -ChildPath $essential
        if ($path -eq $fullEssentialPath -or $path.StartsWith($fullEssentialPath)) {
            return $true
        }
    }
    return $false
}

# Check if project root exists
if (-not (Test-Path -Path $projectRoot)) {
    Write-Error "Project root directory not found: $projectRoot"
    exit 1
}

# Get all items in the project directory
$allItems = Get-ChildItem -Path $projectRoot -Recurse -Force -ErrorAction SilentlyContinue

# Collect items to remove (excluding essential paths)
$itemsToRemove = @()
foreach ($item in $allItems) {
    if (-not (ShouldPreserve($item.FullName))) {
        $itemsToRemove += $item.FullName
    }
}

# Check if there are any items to remove
if ($itemsToRemove.Count -eq 0) {
    Write-Host "No extra files found to remove. Project is already clean." -ForegroundColor Green
    exit 0
}

# Display what will be removed
Write-Host "The following files/directories will be removed:" -ForegroundColor Yellow
foreach ($item in $itemsToRemove) {
    Write-Host "  $item" -ForegroundColor Red
}

# Confirm before deletion
$confirmation = Read-Host "Do you want to proceed with deletion? (Y/N)"
if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
    # Remove the files/directories
    $successCount = 0
    $errorCount = 0
    
    foreach ($item in $itemsToRemove) {
        if (Test-Path $item) {
            try {
                if ((Get-Item $item -ErrorAction SilentlyContinue).PSIsContainer) {
                    Remove-Item -Path $item -Recurse -Force -ErrorAction Stop
                    Write-Host "Removed directory: $item" -ForegroundColor Green
                } else {
                    Remove-Item -Path $item -Force -ErrorAction Stop
                    Write-Host "Removed file: $item" -ForegroundColor Green
                }
                $successCount++
            } catch {
                Write-Host "Error removing: $item - $_" -ForegroundColor Red
                $errorCount++
            }
        }
    }
    
    Write-Host "`nClean-up completed with $successCount successful removals and $errorCount errors." -ForegroundColor Cyan
} else {
    Write-Host "Operation cancelled." -ForegroundColor Cyan
}

# Verify the final structure
Write-Host "`nCurrent project structure:" -ForegroundColor Cyan
Get-ChildItem -Path $projectRoot -Depth 1 | Format-Table Name, LastWriteTime
