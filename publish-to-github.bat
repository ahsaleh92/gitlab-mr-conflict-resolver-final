@echo off
REM GitHub Publishing Script
REM Run this script to publish to GitHub

echo ========================================
echo Publishing to GitHub
echo ========================================
echo.

REM Step 1: Initialize git repository
echo [1/6] Initializing git repository...
git init
if %errorlevel% neq 0 (
    echo ERROR: Git initialization failed
    exit /b 1
)

REM Step 2: Add all files
echo.
echo [2/6] Adding all files...
git add .

REM Step 3: Create first commit
echo.
echo [3/6] Creating initial commit...
git commit -m "feat: Initial release v1.0.0 - GitLab MR Conflict Resolver

- GUI-based merge request conflict resolver
- Multi-round conflict resolution
- Corporate network ready (SSL disabled, proxy bypassed)
- Embedded configuration for NDO environment
- Secure authentication with environment variable support
- Non-interactive git operations
- MR author attribution
- Real-time logging and progress tracking
- Working cancel button
- Tested on MR #449 successfully"

if %errorlevel% neq 0 (
    echo ERROR: Commit failed
    exit /b 1
)

REM Step 4: Set main branch
echo.
echo [4/6] Setting main branch...
git branch -M main

REM Step 5: Add remote (REPLACE YOUR_USERNAME)
echo.
echo [5/6] Adding GitHub remote...
echo.
echo ⚠️  IMPORTANT: Enter your GitHub username when prompted
echo.
set /p GITHUB_USERNAME="Enter your GitHub username: "

git remote add origin https://github.com/%GITHUB_USERNAME%/gitlab-mr-conflict-resolver.git

if %errorlevel% neq 0 (
    echo ERROR: Failed to add remote
    exit /b 1
)

REM Step 6: Push to GitHub
echo.
echo [6/6] Pushing to GitHub...
echo.
echo ⚠️  You will be prompted for GitHub authentication
echo    Use your Personal Access Token as password
echo.
pause

git push -u origin main

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo Push failed!
    echo ========================================
    echo.
    echo Make sure:
    echo 1. You created the repository on GitHub first
    echo 2. Repository name is: gitlab-mr-conflict-resolver
    echo 3. You have a GitHub Personal Access Token
    echo.
    echo Create token at: https://github.com/settings/tokens
    echo Scopes needed: repo
    echo.
    exit /b 1
)

REM Step 7: Create and push tag
echo.
echo [7/7] Creating release tag...
git tag -a v1.0.0 -m "Release v1.0.0 - Initial public release"
git push origin v1.0.0

echo.
echo ========================================
echo ✓ SUCCESS - Published to GitHub!
echo ========================================
echo.
echo Repository: https://github.com/%GITHUB_USERNAME%/gitlab-mr-conflict-resolver
echo.
echo Next steps:
echo 1. Go to your GitHub repository
echo 2. Check the Actions tab - executables will build automatically
echo 3. Add repository description and topics
echo 4. Enable Discussions (optional)
echo.
pause
