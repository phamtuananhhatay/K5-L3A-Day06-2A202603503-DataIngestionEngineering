$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$config = Get-Content -Raw -Encoding UTF8 (Join-Path $repoRoot 'artifacts/embedding_config.json') | ConvertFrom-Json
$destination = Join-Path $repoRoot $config.local_directory
New-Item -ItemType Directory -Force $destination | Out-Null
foreach ($entry in $config.files) {
    $target = Join-Path $destination $entry.local_name
    if ((Test-Path -LiteralPath $target) -and ((Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant() -eq $entry.sha256)) {
        Write-Output "Verified existing $($entry.local_name)"
        continue
    }
    $url = "https://huggingface.co/$($config.model_name)/resolve/$($config.revision)/$($entry.remote_path)?download=true"
    $partial = "$target.part"
    Write-Output "Downloading $($entry.remote_path)"
    & curl.exe --location --fail --silent --show-error --retry 2 --connect-timeout 30 --max-time 1800 --output $partial $url
    if ($LASTEXITCODE -ne 0) { throw "Download failed for $($entry.remote_path)" }
    if ((Get-FileHash -LiteralPath $partial -Algorithm SHA256).Hash.ToLowerInvariant() -ne $entry.sha256) {
        throw "SHA-256 mismatch for $($entry.remote_path); partial file retained for diagnosis"
    }
    Move-Item -LiteralPath $partial -Destination $target -Force
    Write-Output "Verified $($entry.local_name)"
}
Write-Output 'Model download and SHA-256 checks complete.'
