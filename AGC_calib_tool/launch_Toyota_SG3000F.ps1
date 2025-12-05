# Calibration Offset Tool launcher for Toyota SG3000F Master
$calibFile = "c:\DATA\clients\Toyota\Active gain calibration of 'SG3000F Master' (2025-11-21 09h52).calib"
$exePath = Join-Path $PSScriptRoot "dist\CalibOffsetTool.exe"
& $exePath $calibFile
