# PowerShell wrapper for Sphinx make.bat
# Usage: .\make.ps1 html
# or:    .\make.ps1 clean

param(
    [Parameter(Position=0)]
    [string]$Target = "help"
)

# Change to the script's directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $ScriptDir

try {
    # Call make.bat with the specified target
    & ".\make.bat" $Target
} finally {
    Pop-Location
}
