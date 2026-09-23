param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $Root "experiments\EXP-001-pulid-reaging-stress-test\environment\observed"
}
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$Envs = @{
    "generation" = (Join-Path $Root ".venv-exp001-generation\Scripts\python.exe")
    "identity"   = (Join-Path $Root ".venv-exp001-identity\Scripts\python.exe")
    "age"        = (Join-Path $Root ".venv-exp001-age\Scripts\python.exe")
    "analysis"   = (Join-Path $Root ".venv-exp001-analysis\Scripts\python.exe")
}

foreach ($Name in $Envs.Keys) {
    $PythonExe = $Envs[$Name]
    if (-not (Test-Path $PythonExe)) {
        throw "Missing environment: $PythonExe"
    }

    & $PythonExe -m pip freeze --all | Set-Content -Encoding UTF8 (Join-Path $OutputDir "$Name.lock.txt")
    & $PythonExe --version 2>&1 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "$Name.python.txt")
    & $PythonExe -c "import sys; print(sys.version)" 2>&1 | Add-Content -Encoding UTF8 (Join-Path $OutputDir "$Name.python.txt")

    if ($Name -ne "analysis") {
        & $PythonExe -c "import torch; print('torch=', torch.__version__); print('cuda_runtime=', torch.version.cuda); print('cuda_available=', torch.cuda.is_available()); print('gpu=', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NONE')" 2>&1 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "$Name.torch.txt")
    }
}

Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion, OsArchitecture | Format-List | Out-String | Set-Content -Encoding UTF8 (Join-Path $OutputDir "windows.txt")
nvidia-smi 2>&1 | Set-Content -Encoding UTF8 (Join-Path $OutputDir "nvidia-smi.txt")

Write-Host "Captured observed environment under $OutputDir"
