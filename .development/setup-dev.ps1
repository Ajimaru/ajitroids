# Setup script for development environment (Windows)
# PowerShell counterpart to setup-dev.sh - installs pre-commit hooks and
# development dependencies into a project-local .venv.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File .development\setup-dev.ps1

$ErrorActionPreference = "Stop"

Write-Host "Setting up ajitroids development environment..."

# Resolve directories so the script works no matter where it's called from.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvDir = Join-Path $ProjectRoot ".venv"

# Supported interpreter range. The upper bound is not cosmetic: pygame has no
# prebuilt wheel beyond MaxMinor yet, and on a newer interpreter its font
# module fails to import, which breaks the whole test suite. Raise MaxMinor
# only together with the CI matrix in .github/workflows/ci.yml.
$MinMinor = 10
$MaxMinor = 13

# Report a candidate interpreter's minor version, or $null if unusable.
function Get-PyMinor {
    param([string]$Exe, [string[]]$PreArgs = @())
    try {
        $code = 'import sys; print(sys.version_info[1] if sys.version_info[0] == 3 else "")'
        $out = & $Exe @PreArgs -c $code 2>$null
        if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($out)) { return $null }
        return [int]$out.Trim()
    } catch {
        return $null
    }
}

# Prefer the py launcher, which can select an exact version, then fall back to
# whatever python.exe is on PATH. This keeps the script working on a machine
# whose default interpreter has moved ahead of the supported range.
$PythonExe = $null
$PythonArgs = @()

if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($minor in $MaxMinor..$MinMinor) {
        $probe = Get-PyMinor -Exe "py" -PreArgs @("-3.$minor")
        if ($null -ne $probe) {
            $PythonExe = "py"
            $PythonArgs = @("-3.$minor")
            break
        }
    }
}

if (-not $PythonExe) {
    foreach ($candidate in @("python", "python3")) {
        if (-not (Get-Command $candidate -ErrorAction SilentlyContinue)) { continue }
        $minor = Get-PyMinor -Exe $candidate
        if ($null -ne $minor -and $minor -ge $MinMinor -and $minor -le $MaxMinor) {
            $PythonExe = $candidate
            break
        }
    }
}

if (-not $PythonExe) {
    Write-Host "ERROR: No supported Python found. ajitroids needs 3.$MinMinor - 3.$MaxMinor."
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Host "   Detected default: $(python -V 2>&1)"
    }
    Write-Host "   Install a supported version, e.g. 3.$MaxMinor, and re-run this script."
    exit 1
}

Write-Host "Using $(& $PythonExe @PythonArgs -V 2>&1)"

$VenvPython = Join-Path $VenvDir "Scripts\python.exe"

# An existing venv built on an unsupported interpreter is replaced rather than
# reused, otherwise the version check above would pass while the broken
# environment stays in place.
if (Test-Path $VenvDir) {
    $existing = Get-PyMinor -Exe $VenvPython
    if ($null -eq $existing -or $existing -lt $MinMinor -or $existing -gt $MaxMinor) {
        Write-Host "Existing .venv uses an unsupported Python - recreating it..."
        Remove-Item -Recurse -Force $VenvDir
    }
}

if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    & $PythonExe @PythonArgs -m venv $VenvDir
}

if (-not (Test-Path $VenvPython)) {
    Write-Host "ERROR: Virtual environment is missing $VenvPython."
    exit 1
}

# Install through the venv interpreter explicitly, so nothing can land in the
# system environment by accident.
Write-Host "Installing dependencies..."
& $VenvPython -m pip install --upgrade pip setuptools wheel
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements.txt")
& $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements-docs.txt")

Write-Host "Installing pre-commit hooks..."
& $VenvPython -m pip install pre-commit
Push-Location $ProjectRoot
try {
    & $VenvPython -m pre_commit install
} finally {
    Pop-Location
}

Write-Host "Development environment setup complete!"
Write-Host "Pre-commit hooks are now active. They will run on git commit."
Write-Host "   To run hooks manually on all files: .venv\Scripts\pre-commit run --all-files"
