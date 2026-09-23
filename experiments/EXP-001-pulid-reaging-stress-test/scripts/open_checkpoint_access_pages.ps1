param()

$ErrorActionPreference = "Stop"

$Urls = @(
    "https://huggingface.co/black-forest-labs/FLUX.1-dev",
    "https://drive.google.com/file/d/1dswnavflETcnAuplZj1IOKKP0eM8ITgT/view",
    "https://drive.google.com/file/d/1NlsNEVijX2tjMe8LBb1rI56WB_ADVHeP/view",
    "https://drive.google.com/file/d/1CGNCkZQNj5WkP3rLpENWAOgrBQkUWRdw/view"
)

foreach ($Url in $Urls) {
    Start-Process $Url
}

Write-Host "Opened:"
Write-Host "  FLUX.1-dev gated access page"
Write-Host "  AdaFace R100 WebFace12M checkpoint"
Write-Host "  MiVOLO face-only age+gender checkpoint"
Write-Host "  MiVOLO face/person detector checkpoint"
