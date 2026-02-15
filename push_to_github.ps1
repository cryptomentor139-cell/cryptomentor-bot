# Push to GitHub with Personal Access Token
# This script will push your code to GitHub using the provided token

$token = "YOUR_GITHUB_TOKEN_HERE"
$username = "cryptomentor139-cell"
$repo = "cryptomentor-bot"

# Create URL with token
$remoteUrl = "https://${username}:${token}@github.com/${username}/${repo}.git"

Write-Host "Pushing to GitHub..." -ForegroundColor Green

# Remove existing remote if any
git remote remove origin 2>$null

# Add remote with token
git remote add origin $remoteUrl

# Push to GitHub
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "Successfully pushed to GitHub!" -ForegroundColor Green
    Write-Host "Repository: https://github.com/${username}/${repo}" -ForegroundColor Cyan
} else {
    Write-Host "Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Please check the error message above" -ForegroundColor Yellow
}

# Remove remote with token for security
git remote remove origin
git remote add origin "https://github.com/${username}/${repo}.git"

Write-Host ""
Write-Host "Done! Remote URL cleaned (token removed)" -ForegroundColor Green
