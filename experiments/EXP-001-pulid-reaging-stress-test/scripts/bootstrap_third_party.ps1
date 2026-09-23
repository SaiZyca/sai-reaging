param(
    [switch]$ForceReset
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path
$ThirdParty = Join-Path $Root "third_party"

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
        Write-Host "Cloning $Name with core.autocrlf=false..."
        Invoke-Git -GitArgs @("-c", "core.autocrlf=false", "clone", $Url, $Dir)
    }

    Invoke-Git -GitArgs @("-C", $Dir, "config", "core.autocrlf", "false")
    Invoke-Git -GitArgs @("-C", $Dir, "fetch", "--all", "--tags", "--prune")

    Invoke-Git -GitArgs @("-C", $Dir, "reset", "--hard")
    Invoke-Git -GitArgs @("-C", $Dir, "clean", "-fd")
    Invoke-Git -GitArgs @("-C", $Dir, "checkout", "--detach", $Commit)
    Invoke-Git -GitArgs @("-C", $Dir, "reset", "--hard", $Commit)
    Invoke-Git -GitArgs @("-C", $Dir, "clean", "-fd")

    $Actual = (& git -C $Dir rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read HEAD for $Name"
    }
    if ($Actual -ne $Commit) {
        throw "$Name revision mismatch. Expected $Commit, got $Actual"
    }

    $Dirty = @(& git -C $Dir status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect working tree for $Name"
    }
    if ($Dirty.Count -ne 0) {
        throw "$Name is unexpectedly dirty immediately after reset/checkout."
    }

    Write-Host "$Name -> $Actual"
}

function Apply-PuLIDReproducibilityInstrumentation {
    param([string]$PulidDir)

    $Pipeline = Join-Path $PulidDir "pulid\pipeline_flux.py"
    if (-not (Test-Path $Pipeline)) {
        throw "Missing PuLID pipeline file: $Pipeline"
    }

    $Text = [System.IO.File]::ReadAllText($Pipeline)
    $Text = $Text.Replace("`r`n", "`n")
    if (-not $Text.StartsWith("import gc`n")) {
        throw "PuLID instrumentation anchor missing: import gc"
    }
    $Text = $Text.Replace("import gc`n", "import gc`nimport os`n")

    $OldAntelope = @(
        "        snapshot_download('DIAMONIK7777/antelopev2', local_dir='models/antelopev2')"
        "        providers = ['CPUExecutionProvider'] if onnx_provider == 'cpu' \"
        "            else ['CUDAExecutionProvider', 'CPUExecutionProvider']"
        "        self.app = FaceAnalysis(name='antelopev2', root='.', providers=providers)"
        "        self.app.prepare(ctx_id=0, det_size=(640, 640))"
        "        self.handler_ante = insightface.model_zoo.get_model('models/antelopev2/glintr100.onnx',"
        "                                                            providers=providers)"
    ) -join "`n"
    $NewAntelope = @(
        "        antelope_root = os.getenv('EXP001_ANTELOPE_ROOT', '.')"
        "        antelope_dir = os.path.join(antelope_root, 'models', 'antelopev2')"
        "        snapshot_download("
        "            'DIAMONIK7777/antelopev2',"
        "            revision='ba0c3e10f4548361eb9a63265d87ce1140ab5a05',"
        "            local_dir=antelope_dir,"
        "            local_files_only=bool(os.getenv('EXP001_OFFLINE_ASSETS')),"
        "        )"
        "        providers = ['CPUExecutionProvider'] if onnx_provider == 'cpu' \"
        "            else ['CUDAExecutionProvider', 'CPUExecutionProvider']"
        "        self.app = FaceAnalysis(name='antelopev2', root=antelope_root, providers=providers)"
        "        self.app.prepare(ctx_id=0, det_size=(640, 640))"
        "        self.handler_ante = insightface.model_zoo.get_model(os.path.join(antelope_dir, 'glintr100.onnx'),"
        "                                                            providers=providers)"
    ) -join "`n"

    $OldFaceHelper = @(
        "        self.face_helper = FaceRestoreHelper("
        "            upscale_factor=1,"
        "            face_size=512,"
        "            crop_ratio=(1, 1),"
        "            det_model='retinaface_resnet50',"
        "            save_ext='png',"
        "            device=self.device,"
        "        )"
    ) -join "`n"
    $NewFaceHelper = @(
        "        self.face_helper = FaceRestoreHelper("
        "            upscale_factor=1,"
        "            face_size=512,"
        "            crop_ratio=(1, 1),"
        "            det_model='retinaface_resnet50',"
        "            save_ext='png',"
        "            device=self.device,"
        "            model_rootpath=os.getenv('EXP001_FACEXLIB_WEIGHTS'),"
        "        )"
    ) -join "`n"

    $OldParsing = "        self.face_helper.face_parse = init_parsing_model(model_name='bisenet', device=self.device)"
    $NewParsing = "        self.face_helper.face_parse = init_parsing_model(model_name='bisenet', device=self.device, model_rootpath=os.getenv('EXP001_FACEXLIB_WEIGHTS'))"

    $OldEva = "        model, _, _ = create_model_and_transforms('EVA02-CLIP-L-14-336', 'eva_clip', force_custom_clip=True)"
    $NewEva = "        model, _, _ = create_model_and_transforms('EVA02-CLIP-L-14-336', os.getenv('EXP001_EVA_CLIP_PATH', 'eva_clip'), force_custom_clip=True)"

    $OldPretrain = @(
        "        hf_hub_download('guozinan/PuLID', f'pulid_flux_{version}.safetensors', local_dir='models')"
        "        ckpt_path = f'models/pulid_flux_{version}.safetensors'"
        "        if pretrain_path is not None:"
        "            ckpt_path = pretrain_path"
    ) -join "`n"

    $NewPretrain = @(
        "        if pretrain_path is None:"
        "            ckpt_path = hf_hub_download("
        "                'guozinan/PuLID', f'pulid_flux_{version}.safetensors', local_dir='models'"
        "            )"
        "        else:"
        "            ckpt_path = pretrain_path"
    ) -join "`n"

    if (-not $Text.Contains($OldAntelope)) {
        throw "PuLID instrumentation anchor missing: AntelopeV2 block. Upstream content does not match the pinned contract."
    }
    if (-not $Text.Contains($OldFaceHelper)) {
        throw "PuLID instrumentation anchor missing: FaceRestoreHelper block."
    }
    if (-not $Text.Contains($OldParsing)) {
        throw "PuLID instrumentation anchor missing: BiSeNet parser block."
    }
    if (-not $Text.Contains($OldEva)) {
        throw "PuLID instrumentation anchor missing: EVA-CLIP block."
    }
    if (-not $Text.Contains($OldPretrain)) {
        throw "PuLID instrumentation anchor missing: load_pretrain block. Upstream content does not match the pinned contract."
    }

    $Text = $Text.Replace($OldAntelope, $NewAntelope)
    $Text = $Text.Replace($OldFaceHelper, $NewFaceHelper)
    $Text = $Text.Replace($OldParsing, $NewParsing)
    $Text = $Text.Replace($OldEva, $NewEva)
    $Text = $Text.Replace($OldPretrain, $NewPretrain)

    $Utf8NoBom = [System.Text.UTF8Encoding]::new($false)
    [System.IO.File]::WriteAllText($Pipeline, $Text, $Utf8NoBom)

    $Written = [System.IO.File]::ReadAllText($Pipeline)
    if (-not $Written.Contains("revision='ba0c3e10f4548361eb9a63265d87ce1140ab5a05'")) {
        throw "PuLID instrumentation verification failed: AntelopeV2 revision marker missing."
    }
    if (-not $Written.Contains("        if pretrain_path is None:")) {
        throw "PuLID instrumentation verification failed: local checkpoint guard missing."
    }
    if (-not $Written.Contains("EXP001_FACEXLIB_WEIGHTS")) {
        throw "PuLID instrumentation verification failed: FaceXLib local asset marker missing."
    }
    if (-not $Written.Contains("EXP001_EVA_CLIP_PATH")) {
        throw "PuLID instrumentation verification failed: EVA-CLIP local asset marker missing."
    }
    if (-not $Written.Contains("EXP001_ANTELOPE_ROOT")) {
        throw "PuLID instrumentation verification failed: Antelope local asset marker missing."
    }

    Invoke-Git -GitArgs @("-C", $PulidDir, "diff", "--check")

    $Changed = @(& git -C $PulidDir status --porcelain)
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to inspect PuLID working tree after instrumentation."
    }
    if ($Changed.Count -ne 1 -or $Changed[0] -notmatch "pulid/pipeline_flux\.py$") {
        throw "Unexpected PuLID changes after instrumentation: $($Changed -join '; ')"
    }

    Write-Host "Applied PuLID reproducibility instrumentation."
}

Sync-Repo -Name "PuLID" -Url "https://github.com/ToTheBeginning/PuLID.git" -Commit "a66a6a1901729897fa1dc11d10397943caf15470"
Sync-Repo -Name "AdaFace" -Url "https://github.com/mk-minchul/AdaFace.git" -Commit "c60eaa786a42c03444f3df7096dbaf9d57ae010d"
Sync-Repo -Name "MiVOLO" -Url "https://github.com/WildChlamydia/MiVOLO.git" -Commit "37475e3f8818b5f22448003feec3e64b01bfb188"

$PulidDir = Join-Path $ThirdParty "PuLID"
Apply-PuLIDReproducibilityInstrumentation -PulidDir $PulidDir

Write-Host ""
Write-Host "EXP-001 third-party repositories are ready:"
Write-Host "  $ThirdParty\PuLID"
Write-Host "  $ThirdParty\AdaFace"
Write-Host "  $ThirdParty\MiVOLO"
