# Manual wiki sync script
# Syncs markdown files from wiki/ directory to GitHub Wiki repository

$ErrorActionPreference = "Stop"

$REPO_NAME = "skyelaird/dvoacap-python"
$WIKI_URL = "https://github.com/$REPO_NAME.wiki.git"
$WIKI_DIR = "wiki-repo-temp"

Write-Host "🔄 Starting wiki sync..." -ForegroundColor Cyan

# Check if wiki directory exists
if (-not (Test-Path "wiki")) {
    Write-Host "❌ Error: wiki/ directory not found" -ForegroundColor Red
    exit 1
}

# Clone wiki repository
Write-Host "📥 Cloning wiki repository..." -ForegroundColor Cyan
if (Test-Path $WIKI_DIR) {
    Remove-Item -Recurse -Force $WIKI_DIR
}

try {
    $cloneOutput = git clone $WIKI_URL $WIKI_DIR 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Could not clone wiki repository" -ForegroundColor Red
        Write-Host "Git output: $cloneOutput" -ForegroundColor Yellow
        Write-Host "Make sure the Wiki is enabled in repository settings and at least one page exists" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Error: Could not clone wiki repository" -ForegroundColor Red
    Write-Host "Exception: $_" -ForegroundColor Yellow
    Write-Host "Make sure the Wiki is enabled in repository settings and at least one page exists" -ForegroundColor Yellow
    exit 1
}

# Copy markdown files
Write-Host "📋 Copying markdown files..." -ForegroundColor Cyan
Copy-Item "wiki\*.md" "$WIKI_DIR\" -Force

# Commit and push
Push-Location $WIKI_DIR

$userName = git config --global user.name
$userEmail = git config --global user.email
git config user.name $userName
git config user.email $userEmail

# Check for changes
$addOutput = git add *.md 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to add markdown files" -ForegroundColor Red
    Write-Host "Git output: $addOutput" -ForegroundColor Yellow
    Pop-Location
    exit 1
}
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "✅ No changes to sync" -ForegroundColor Green
    Pop-Location
    Remove-Item -Recurse -Force $WIKI_DIR
    exit 0
}

Write-Host "💾 Committing changes..." -ForegroundColor Cyan
Push-Location ..
$COMMIT_HASH = git rev-parse --short HEAD
Pop-Location
$commitOutput = git commit -m "Manual wiki sync from repository (commit: $COMMIT_HASH)" 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to commit changes" -ForegroundColor Red
    Write-Host "Git output: $commitOutput" -ForegroundColor Yellow
    Pop-Location
    exit 1
}

Write-Host "⬆️  Pushing to GitHub Wiki..." -ForegroundColor Cyan
$pushOutput = git push origin master 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to push to wiki repository" -ForegroundColor Red
    Write-Host "Git output: $pushOutput" -ForegroundColor Yellow
    Pop-Location
    exit 1
}

Pop-Location
Remove-Item -Recurse -Force $WIKI_DIR

Write-Host "✅ Wiki synced successfully!" -ForegroundColor Green
