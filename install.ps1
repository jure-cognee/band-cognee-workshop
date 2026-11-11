# The whole of step 0 on Windows, in one line. Paste this into PowerShell:
#
#   irm https://raw.githubusercontent.com/jure-cognee/band-cognee-workshop/main/install.ps1 | iex
#
# It gets the workshop into a folder called band-cognee-workshop (inside the folder you are
# in now), runs the setup, and leaves you inside that folder, ready for step 1.
# You need nothing installed first. Running it again is safe: it updates and re-checks.

& {
    $ErrorActionPreference = "Stop"
    $repo = "https://github.com/jure-cognee/band-cognee-workshop"
    function Say($text) { Write-Host "[install] $text" }

    try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12 } catch {}

    # Where the workshop goes. If you are already inside it, stay there.
    $here = (Get-Location).Path
    if ((Test-Path (Join-Path $here "00_check.py")) -and (Test-Path (Join-Path $here "pyproject.toml"))) {
        $folder = $here
    } else {
        $folder = Join-Path $here "band-cognee-workshop"
    }

    $hasGit = [bool](Get-Command git -ErrorAction SilentlyContinue)

    # 1. Get or update the code with git, when git is there.
    if ($hasGit -and (Test-Path (Join-Path $folder ".git"))) {
        Say "Updating $folder"
        git -C $folder pull --ff-only
    } elseif ($hasGit -and -not (Test-Path $folder)) {
        Say "Downloading the workshop into $folder"
        git clone "$repo.git" $folder
    }

    # 2. No git, or the update did not bring the new files: take the files as a zip.
    #    This never touches your .env.
    if (-not (Test-Path (Join-Path $folder "setup.ps1")) -or -not (Test-Path (Join-Path $folder "node22.py"))) {
        Say "Downloading the workshop files as a zip"
        $tmp = Join-Path ([System.IO.Path]::GetTempPath()) ("band-workshop-" + [System.Guid]::NewGuid().ToString("N"))
        New-Item -ItemType Directory -Path $tmp | Out-Null
        $zip = Join-Path $tmp "workshop.zip"
        Invoke-WebRequest -Uri "$repo/archive/refs/heads/main.zip" -OutFile $zip -UseBasicParsing
        Expand-Archive -Path $zip -DestinationPath $tmp -Force
        if (-not (Test-Path $folder)) { New-Item -ItemType Directory -Path $folder | Out-Null }
        Copy-Item -Path (Join-Path $tmp "band-cognee-workshop-main\*") -Destination $folder -Recurse -Force
        Remove-Item -Recurse -Force $tmp
    }

    if (-not (Test-Path (Join-Path $folder "setup.ps1"))) {
        Write-Host "[install] Could not get the workshop files. Check your internet connection and paste the line again." -ForegroundColor Red
        return
    }

    # 3. Run the setup, then make sure this window can see uv.
    Set-Location $folder
    powershell -ExecutionPolicy Bypass -File (Join-Path $folder "setup.ps1")
    $setupOk = ($LASTEXITCODE -eq 0)

    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
    }

    if ($setupOk) {
        Write-Host ""
        Write-Host "[install] Done. You are now in $folder" -ForegroundColor Green
        Write-Host "[install] Step 1:  uv run python 01_ingest.py" -ForegroundColor Green
    } else {
        Write-Host "[install] The setup did not finish. Read the message above, fix it, and paste the same line again." -ForegroundColor Red
    }
}
