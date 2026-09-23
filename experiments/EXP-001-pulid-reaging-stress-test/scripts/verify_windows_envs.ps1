param()

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = (Resolve-Path (Join-Path $ScriptDir "..\..\..")).Path

function Invoke-Checked {
    param(
        [string]$Name,
        [string]$PythonExe,
        [string]$Code
    )

    if (-not (Test-Path $PythonExe)) {
        throw "$Name environment is missing: $PythonExe"
    }

    Write-Host ""
    Write-Host "=== $Name ==="
    & $PythonExe -c $Code
    if ($LASTEXITCODE -ne 0) {
        throw "$Name verification failed."
    }
}

$GenPython = Join-Path $Root ".venv-exp001-generation\Scripts\python.exe"
$IdPython = Join-Path $Root ".venv-exp001-identity\Scripts\python.exe"
$AgePython = Join-Path $Root ".venv-exp001-age\Scripts\python.exe"
$AnalysisPython = Join-Path $Root ".venv-exp001-analysis\Scripts\python.exe"

$PulidRepo = Join-Path $Root "third_party\PuLID"
$AdaFaceRepo = Join-Path $Root "third_party\AdaFace"
$MiVOLORepo = Join-Path $Root "third_party\MiVOLO"

$GenCode = @"
import sys
from pathlib import Path
repo = Path(r'$PulidRepo')
sys.path.insert(0, str(repo))
import torch
import torchvision
import diffusers
import transformers
import huggingface_hub
import cv2
import insightface
import onnxruntime
import accelerate
import safetensors
import yaml
import flux.util
from pulid.pipeline_flux import PuLIDPipeline
assert torch.cuda.is_available(), 'CUDA is not available in generation environment'
arch_list = torch.cuda.get_arch_list()
assert 'sm_120' in arch_list or 'compute_120' in arch_list, f'Blackwell sm_120 missing from PyTorch build: {arch_list}'
x = torch.ones(1, device='cuda')
torch.cuda.synchronize()
print('python=ok')
print('torch=', torch.__version__)
print('torchvision=', torchvision.__version__)
print('cuda_runtime=', torch.version.cuda)
print('gpu=', torch.cuda.get_device_name(0))
print('arch_list=', arch_list)
print('onnxruntime_providers=', onnxruntime.get_available_providers())
print('pulid_import=ok')
"@

$IdCode = @"
import sys
from pathlib import Path
repo = Path(r'$AdaFaceRepo')
sys.path.insert(0, str(repo))
import torch
import cv2
from PIL import Image
import yaml
import net
from face_alignment import mtcnn
assert torch.cuda.is_available(), 'CUDA is not available in identity environment'
arch_list = torch.cuda.get_arch_list()
assert 'sm_120' in arch_list or 'compute_120' in arch_list, f'Blackwell sm_120 missing from PyTorch build: {arch_list}'
x = torch.ones(1, device='cuda')
torch.cuda.synchronize()
m = net.build_model('ir_101')
del m
print('python=ok')
print('torch=', torch.__version__)
print('cuda_runtime=', torch.version.cuda)
print('gpu=', torch.cuda.get_device_name(0))
print('arch_list=', arch_list)
print('adaface_import=ok')
"@

$AgeCode = @"
import sys
from pathlib import Path
repo = Path(r'$MiVOLORepo')
sys.path.insert(0, str(repo))
import torch
import cv2
import timm
import ultralytics
import yaml
from mivolo.predictor import Predictor
assert torch.cuda.is_available(), 'CUDA is not available in age environment'
arch_list = torch.cuda.get_arch_list()
assert 'sm_120' in arch_list or 'compute_120' in arch_list, f'Blackwell sm_120 missing from PyTorch build: {arch_list}'
x = torch.ones(1, device='cuda')
torch.cuda.synchronize()
print('python=ok')
print('torch=', torch.__version__)
print('cuda_runtime=', torch.version.cuda)
print('gpu=', torch.cuda.get_device_name(0))
print('arch_list=', arch_list)
print('timm=', timm.__version__)
print('ultralytics=', ultralytics.__version__)
print('mivolo_import=ok')
"@

$AnalysisCode = @"
import numpy
import pandas
import pyarrow
import yaml
print('python=ok')
print('numpy=', numpy.__version__)
print('pandas=', pandas.__version__)
print('pyarrow=', pyarrow.__version__)
print('analysis_import=ok')
"@

Invoke-Checked -Name "generation" -PythonExe $GenPython -Code $GenCode
Invoke-Checked -Name "identity" -PythonExe $IdPython -Code $IdCode
Invoke-Checked -Name "age" -PythonExe $AgePython -Code $AgeCode
Invoke-Checked -Name "analysis" -PythonExe $AnalysisPython -Code $AnalysisCode

Write-Host ""
Write-Host "EXP-001 Windows environment verification PASSED."
