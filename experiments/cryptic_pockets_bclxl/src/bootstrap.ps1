param([string]$Python = 'C:/Users/Don/AppData/Roaming/uv/python/cpython-3.11.16-windows-x86_64-none/python.exe')
$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
foreach ($folder in @('data/raw','data/processed','manifests/runs','results','tests','.cache','results/tmp')) {
    New-Item -ItemType Directory -Force -Path (Join-Path $root $folder) | Out-Null
}
$stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
$record = [ordered]@{
    started_at = [DateTime]::UtcNow.ToString('o')
    command = "powershell -File src/bootstrap.ps1 -Python $Python"
    status = 'RUNNING'
    inputs = @{}
    outputs = @{}
    commands = @()
}
foreach ($rel in @('src/bootstrap.ps1','configs/requirements-reference.txt','PROTOCOL.md')) {
    $record.inputs[$rel] = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $root $rel)).Hash.ToLower()
}
$recordPath = Join-Path $root "manifests/runs/bootstrap-$stamp.json"
$record | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -LiteralPath $recordPath
try {
    $venv = Join-Path $root '.venv'
    $venvPython = Join-Path $venv 'Scripts/python.exe'
    if (!(Test-Path -LiteralPath $venvPython)) {
        $record.commands += "$Python -B -m venv $venv"
        & $Python -B -m venv $venv
        if ($LASTEXITCODE -ne 0) { throw "venv creation failed: exit $LASTEXITCODE" }
    }
    $env:PIP_CACHE_DIR = Join-Path $root '.cache/pip'
    $env:TEMP = Join-Path $root 'results/tmp'
    $env:TMP = $env:TEMP
    $record.commands += "$venvPython -B -m pip install --disable-pip-version-check -r configs/requirements-reference.txt"
    $pipLog = Join-Path $root "results/bootstrap-$stamp.log"
    & $venvPython -B -m pip install --disable-pip-version-check -r (Join-Path $root 'configs/requirements-reference.txt') 2>&1 | Tee-Object -FilePath $pipLog
    $record.outputs["results/bootstrap-$stamp.log"] = (Get-FileHash -Algorithm SHA256 -LiteralPath $pipLog).Hash.ToLower()
    if ($LASTEXITCODE -ne 0) { throw "pip installation failed: exit $LASTEXITCODE; see $pipLog" }
    $record.status = 'SUCCESS'
} catch {
    $record.status = 'FAILED'
    $record.error = $_.ToString()
    throw
} finally {
    $record.finished_at = [DateTime]::UtcNow.ToString('o')
    $record | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 -LiteralPath $recordPath
}
