# PowerShell script to build the Log Analyzer executable
# Requires PyInstaller to be installed: pip install pyinstaller

param (
    [Switch]$Clean
)

# Set the working directory to the script's location
$ProjectRoot = $PSScriptRoot
Set-Location $ProjectRoot

if ($Clean) {
    Write-Host "Cleaning build artifacts..." -ForegroundColor Yellow
    $foldersToRemove = @("build", "dist")
    foreach ($folder in $foldersToRemove) {
        if (Test-Path $folder) {
            Write-Host "Removing folder: $folder"
            Remove-Item -Recurse -Force $folder
        }
    }
    Write-Host "Clean complete." -ForegroundColor Green
    exit 0
}

# Check if PyInstaller is installed
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: PyInstaller is not installed." -ForegroundColor Red
    Write-Host "Install it with: pip install pyinstaller"
    exit 1
}

Write-Host "Building Log Analyzer executable..."
Write-Host ""

# Build the executable
Write-Host "Running PyInstaller with LogAnalyzer.spec..." -ForegroundColor Green
python -m PyInstaller LogAnalyzer.spec --noconfirm

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "SUCCESS! Executable created:" -ForegroundColor Green
    Write-Host "  Location: dist\LogAnalyzer\LogAnalyzer.exe"
    Write-Host ""
    Write-Host "You can now run the application from the dist folder."
} else {
    Write-Host ""
    Write-Host "Build failed. Check the error messages above." -ForegroundColor Red
    exit 1
}
