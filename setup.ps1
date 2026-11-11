# Step 0 on Windows, in one command. Run this in PowerShell, in the workshop folder:
#
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#
# It installs uv if you don't have it, creates .env, asks for your OpenAI key,
# installs everything, and checks the result. You can run it again at any time.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

function Say($text) { Write-Host "[setup] $text" }
function Fail($text) { Write-Host "[setup] $text" -ForegroundColor Red; exit 1 }

if (-not (Test-Path "pyproject.toml")) {
    Fail "Run this from the band-cognee-workshop folder."
}

# 1. uv
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Say "Installing uv..."
    powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Fail "uv was installed, but this window can't see it yet. Close PowerShell, open it again, and run this script again."
    }
}
Say "uv: $(uv --version)"

# 2. .env
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Say "Created .env"
}

# 3. OpenAI key
$envFile = Join-Path $PSScriptRoot ".env"
$lines = @([System.IO.File]::ReadAllLines($envFile))
$current = ($lines | Where-Object { $_ -like "LLM_API_KEY=*" } | Select-Object -First 1)
if (-not $current -or $current -eq "LLM_API_KEY=") {
    $key = (Read-Host "[setup] Paste your OpenAI API key (starts with sk-)").Trim()
    if (-not $key.StartsWith("sk-")) { Fail "That doesn't look like an OpenAI key. Run the script again." }
    $lines = @($lines | ForEach-Object { if ($_ -like "LLM_API_KEY=*") { "LLM_API_KEY=$key" } else { $_ } })
    # UTF-8 without BOM, so Python reads the file cleanly.
    [System.IO.File]::WriteAllLines($envFile, [string[]]$lines, (New-Object System.Text.UTF8Encoding $false))
    Say "Saved your key in .env"
} else {
    Say "LLM_API_KEY is already in .env"
}

# 4. Install and check
Say "Installing Python and Cognee. The first time takes a few minutes..."
uv sync
if ($LASTEXITCODE -ne 0) { Fail "uv sync failed. Send the error above to the presenter." }

# 5. Node.js 22 for step 2 (the graph UI). Downloaded into .node if you don't have it.
uv run python node22.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[setup] Step 2 (the graph UI) will not work until this is fixed. All other steps work." -ForegroundColor Yellow
}

uv run python 00_check.py
if ($LASTEXITCODE -ne 0) { Fail "The check failed. See the message above." }
