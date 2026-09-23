param(
    [switch]$ForceReset
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
$ThirdParty = Join-Path $Root "third_party"
$PatchDir = Join-Path $Root "experiments\EXP-001-pulid-reaging-stress-test\patches"

New-Item -ItemType Directory -Force -Path $ThirdParty | Out-Null

function Invoke-Git {
    param([string[]]$GitArgs)
    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "git failed: git $($GitArgs -join ' ')"
    }
}

function Sync-Repo {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Commit
    )

    $Dir = Join-Path $ThirdParty $Name

    if (-not (Test-Path (Join-Path $Dir ".git"))) {
        Write-Host "Cloning $Name..."
        Invoke-Git -GitArgs @("clone", $Url, $Dir)
    }

    Invoke-Git -GitArgs @("-C", $Dir, "config", "core.autocrlf", "false")
    Invoke-Git -GitArgs @("-C", $Dir, "fetch", "--all", "--tags", "--prune")

    if ($ForceReset) {
        Invoke-Git -GitArgs @("-C", $Dir, "reset", "--hard")
        Invoke-Git -GitArgs @("-C", $Dir, "clean", "-fd")
    }

    Invoke-Git -GitArgs @("-C", $Dir, "checkout", "--detach", $Commit)
    $Actual = (& git -C $Dir rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read HEAD for $Name"
    }
    if ($Actual -ne $Commit) {
        throw "$Name revision mismatch. Expected $Commit, got $Actual"
    }

    Write-Host "$Name -> $Actual"
}

Sync-Repo -Name "PuLID" -Url "https://github.com/ToTheBeginning/PuLID.git" -Commit "a66a6a1901729897fa1dc11d10397943caf15470"
Sync-Repo -Name "AdaFace" -Url "https://github.com/mk-minchul/AdaFace.git" -Commit "c60eaa786a42c03444f3df7096dbaf9d57ae010d"
Sync-Repo -Name "MiVOLO" -Url "https://github.com/WildChlamydia/MiVOLO.git" -Commit "37475e3f8818b5f22448003feec3e64b01bfb188"

$PulidDir = Join-Path $ThirdParty "PuLID"
$Patch = Join-Path $PatchDir "pulid_reproducibility.patch"

& git -C $PulidDir apply --reverse --check $Patch 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "PuLID reproducibility patch already applied."
}
else {
    Invoke-Git -GitArgs @("-C", $PulidDir, "apply", "--check", $Patch)
    Invoke-Git -GitArgs @("-C", $PulidDir, "apply", $Patch)
    Write-Host "Applied PuLID reproducibility patch."
}

Write-Host ""
Write-Host "EXP-001 third-party repositories are ready:"
Write-Host "  $ThirdParty\PuLID"
Write-Host "  $ThirdParty\AdaFace"
Write-Host "  $ThirdParty\MiVOLO"
