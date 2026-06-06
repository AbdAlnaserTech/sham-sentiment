# Push project to GitHub (run once)
# Usage: powershell -ExecutionPolicy Bypass -File deploy_push.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "=== Push sentiment project to GitHub ===" -ForegroundColor Cyan
Write-Host ""

$username = Read-Host "GitHub username (example: AbdAlnaserTech)"
$repo = Read-Host "Repository name (example: sham-sentiment)"
$token = Read-Host "GitHub Personal Access Token" -AsSecureString
$plain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($token)
)

if (-not $username -or -not $repo -or -not $plain) {
    Write-Host "Username, repository, and token are required." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Create a PUBLIC repo first: https://github.com/new" -ForegroundColor Yellow
Write-Host "Name: $repo - do NOT add README" -ForegroundColor Yellow
Write-Host "Press Enter after the repo is created on GitHub..."
Read-Host

$remote = "https://github.com/$username/$repo.git"
$pushUrl = "https://${username}:${plain}@github.com/${username}/${repo}.git"

git branch -M main 2>$null

$prevErrorAction = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
$originUrl = git remote get-url origin 2>$null
$ErrorActionPreference = $prevErrorAction

if ($originUrl) {
    git remote set-url origin $remote
} else {
    git remote add origin $remote
}

Write-Host "Uploading..." -ForegroundColor Green
git push -u $pushUrl main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Upload failed. Check token (repo scope) and that repo is Public." -ForegroundColor Red
    exit 1
}

git remote set-url origin $remote
Write-Host ""
Write-Host "Upload successful!" -ForegroundColor Green
Write-Host "Repo: https://github.com/$username/$repo" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next - Streamlit Cloud:" -ForegroundColor Yellow
Write-Host "1) Open https://share.streamlit.io and click Create app"
Write-Host "2) Repository: $username/$repo"
Write-Host "3) Main file: streamlit_app.py"
Write-Host "4) Secrets (Advanced settings):"
Write-Host '   SENTIMENT_CLOUD = "1"'
Write-Host '   SENTIMENT_CLOUD_LIGHT = "1"'
Write-Host '   SENTIMENT_MAX_BATCH = "100"'
Write-Host "5) Deploy - URL: https://$repo.streamlit.app"
Write-Host ""
