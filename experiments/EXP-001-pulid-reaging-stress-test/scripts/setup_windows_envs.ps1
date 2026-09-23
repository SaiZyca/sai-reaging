param(
    [string]$PythonLauncher = "py"
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
$EnvDir = Join-Path $Root "experiments\EXP-001-pulid-reaging-stress-test\environment"

function Invoke-Checked {
    param(
        [string]$Exe,
        [string[]]$Args
    )
    & $Exe @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Exe $($Args -join ' ')"
    }
}

function New-Python310Venv {
    param([string]$Name)
    $Venv = Join-Path $Root $Name
    if (-not (Test-Path (Join-Path $Venv "Scripts\python.exe"))) {
        Write-Host "Creating $Name..."
        Invoke-Checked $PythonLauncher @("-3.10", "-m", "venv", $Venv)
    }
    return (Join-Path $Venv "Scripts\python.exe")
}

function Install-NonTorchRequirements {
    param(
        [string]$PythonExe,
        [string]$InputFile
    )
    $Temp = [System.IO.Path]::GetTempFileName()
    try {
        Get-Content $InputFile |
            Where-Object {
                $_ -notmatch '^\s*(torch|torchvision)(==|<=|>=|~=|$)'
            } |
            Set-Content -Encoding UTF8 $Temp

        Invoke-Checked $PythonExe @("-m", "pip", "install", "--upgrade", "pip")
        Invoke-Checked $PythonExe @("-m", "pip", "install", "-r", $Temp)
    }
    finally {
        Remove-Item -Force -ErrorAction SilentlyContinue $Temp
    }
}

Write-Host "Checking Python 3.10..."
Invoke-Checked $PythonLauncher @("-3.10", "--version")

$GenPython = New-Python310Venv ".venv-exp001-generation"
Invoke-Checked $GenPython @("-m", "pip", "install", "torch==2.0.1", "torchvision==0.15.2", "--index-url", "https://download.pytorch.org/whl/cu118")
Install-NonTorchRequirements -PythonExe $GenPython -InputFile (Join-Path $EnvDir "generation.requirements.in")

$IdPython = New-Python310Venv ".venv-exp001-identity"
Invoke-Checked $IdPython @("-m", "pip", "install", "torch==1.13.1+cu117", "torchvision==0.14.1+cu117", "--extra-index-url", "https://download.pytorch.org/whl/cu117")
Install-NonTorchRequirements -PythonExe $IdPython -InputFile (Join-Path $EnvDir "identity.requirements.in")

$AgePython = New-Python310Venv ".venv-exp001-age"
Invoke-Checked $AgePython @("-m", "pip", "install", "torch==2.0.1", "torchvision==0.15.2", "--index-url", "https://download.pytorch.org/whl/cu118")
Install-NonTorchRequirements -PythonExe $AgePython -InputFile (Join-Path $EnvDir "age.requirements.in")

$AnalysisPython = New-Python310Venv ".venv-exp001-analysis"
Invoke-Checked $AnalysisPython @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked $AnalysisPython @("-m", "pip", "install", "-r", (Join-Path $EnvDir "analysis.requirements.in"))

Write-Host ""
Write-Host "Running pip check..."
foreach ($PythonExe in @($GenPython, $IdPython, $AgePython, $AnalysisPython)) {
    Invoke-Checked $PythonExe @("-m", "pip", "check")
}

Write-Host ""
Write-Host "Windows environments created successfully."
Write-Host "Generation : $GenPython"
Write-Host "Identity   : $IdPython"
Write-Host "Age        : $AgePython"
Write-Host "Analysis   : $AnalysisPython"
