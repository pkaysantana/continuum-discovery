# One-time user-authorized preregistration anchor. No detector commands.
$ErrorActionPreference = 'Stop'
$experimentRoot = Split-Path $PSScriptRoot -Parent
$repositoryRoot = Split-Path (Split-Path $experimentRoot -Parent) -Parent
$scope = 'experiments/cryptic_pockets_bclxl'
$tagName = 'cryptic-pocket-bclxl-preregistered-v1'
$commands = [System.Collections.Generic.List[string]]::new()
$started = [DateTime]::UtcNow.ToString('o')
$anchorSha = $null
$receiptCommit = $null
function Invoke-CheckedGit {
    param([string[]]$Arguments)
    $commands.Add('git ' + ($Arguments -join ' '))
    $value = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "git failed ($LASTEXITCODE): $($Arguments -join ' '): $value" }
    return $value
}
Push-Location $repositoryRoot
try {
    $staged = Invoke-CheckedGit @('diff', '--cached', '--name-only')
    if ($staged) { throw 'Existing staged changes: refusing to include unrelated work.' }
    $existingTag = Invoke-CheckedGit @('tag', '--list', $tagName)
    if ($existingTag) { throw 'Preregistration tag already exists; never move it.' }
    $preflight = Get-ChildItem -LiteralPath (Join-Path $experimentRoot 'manifests') -Filter 'preflight-*.json' |
        Sort-Object Name | Select-Object -Last 1
    if (!$preflight) { throw 'Missing preflight receipt.' }
    $check = Get-Content -LiteralPath $preflight.FullName -Raw | ConvertFrom-Json
    if ($check.status -ne 'SUCCESS' -or $check.test_counts.failures -ne 0 -or $check.test_counts.errors -ne 0) {
        throw 'Preflight/test gate did not pass.'
    }
    $preregPath = Join-Path $experimentRoot 'PREREGISTRATION.md'
    $prereg = [IO.File]::ReadAllText($preregPath)
    if (!$prereg.Contains('ANCHOR_SHA_PENDING')) { throw 'Unexpected preregistration anchor state.' }
    Invoke-CheckedGit @('add', '--', $scope) | Out-Null
    $paths = @(Invoke-CheckedGit @('diff', '--cached', '--name-only'))
    if (!$paths.Count -or @($paths | Where-Object { !$_.StartsWith($scope + '/') }).Count) {
        throw 'Staged file scope is not exactly the requested experiment.'
    }
    if (@($paths | Where-Object { $_ -match '/\.venv/|/\.cache/|/__pycache__/|/results/tmp/' }).Count) {
        throw 'Runtime cache unexpectedly staged.'
    }
    Invoke-CheckedGit @('commit', '-m', 'preregister BCL-XL cryptic-pocket reproduction benchmark') | Select-Object -First 2
    $anchorSha = (Invoke-CheckedGit @('rev-parse', 'HEAD')).ToString().Trim()
    Invoke-CheckedGit @('tag', '-a', $tagName, '-m', 'BCL-XL reproduction/pipeline validation preregistration before any detector execution', $anchorSha) | Out-Null
    $resolvedTag = (Invoke-CheckedGit @('rev-parse', "$tagName^{commit}")).ToString().Trim()
    if ($resolvedTag -ne $anchorSha) { throw 'Tag does not resolve to anchor commit.' }
    [IO.File]::WriteAllText($preregPath, $prereg.Replace('ANCHOR_SHA_PENDING', $anchorSha), [Text.UTF8Encoding]::new($false))
    $receipt = [ordered]@{
        schema_version = 1
        status = 'SUCCESS'
        started_at = $started
        recorded_at = [DateTime]::UtcNow.ToString('o')
        anchor_commit_sha = $anchorSha
        tag = $tagName
        tag_commit_sha = $resolvedTag
        no_detector_executed = $true
        commands_completed = @($commands)
        preflight_file = $preflight.Name
        preflight_sha256 = (Get-FileHash -LiteralPath $preflight.FullName -Algorithm SHA256).Hash.ToLower()
        preregistration_receipt_sha256 = (Get-FileHash -LiteralPath $preregPath -Algorithm SHA256).Hash.ToLower()
        script_sha256 = (Get-FileHash -LiteralPath $PSCommandPath -Algorithm SHA256).Hash.ToLower()
        staged_anchor_paths = $paths
        receipt_commit_note = 'This receipt and literal SHA in PREREGISTRATION.md are committed separately without amending the anchor. Find the receipt commit via git log -- manifests/git_anchor_receipt.json.'
        receipt_commands = @('git add -- experiments/cryptic_pockets_bclxl/PREREGISTRATION.md experiments/cryptic_pockets_bclxl/manifests/git_anchor_receipt.json', 'git commit -m record BCL-XL preregistration anchor SHA')
    }
    $receiptPath = Join-Path $experimentRoot 'manifests/git_anchor_receipt.json'
    [IO.File]::WriteAllText($receiptPath, ($receipt | ConvertTo-Json -Depth 8) + "`n", [Text.UTF8Encoding]::new($false))
    Invoke-CheckedGit @('add', '--', "$scope/PREREGISTRATION.md", "$scope/manifests/git_anchor_receipt.json") | Out-Null
    Invoke-CheckedGit @('commit', '-m', 'record BCL-XL preregistration anchor SHA') | Select-Object -First 2
    $receiptCommit = (Invoke-CheckedGit @('rev-parse', 'HEAD')).ToString().Trim()
    Write-Output "ANCHOR_SHA=$anchorSha"
    Write-Output "TAG=$tagName"
    Write-Output "RECEIPT_COMMIT_SHA=$receiptCommit"
    Invoke-CheckedGit @('status', '--short')
} catch {
    $failure = [ordered]@{status='FAILED'; started_at=$started; failed_at=[DateTime]::UtcNow.ToString('o'); error=$_.ToString(); anchor_sha=$anchorSha; receipt_commit=$receiptCommit; commands=@($commands)}
    $stamp = [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffffffZ')
    $failure | ConvertTo-Json -Depth 8 | Set-Content -Encoding UTF8 -LiteralPath (Join-Path $experimentRoot "results/freeze-failed-$stamp.json")
    throw
} finally {
    Pop-Location
}
