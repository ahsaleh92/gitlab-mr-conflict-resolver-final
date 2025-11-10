# ⚠️ BEFORE BUILDING YOUR OWN EXECUTABLE

**IMPORTANT**: The source code in this repository has placeholder values. Before building your own executable, you MUST customize these settings.

## 🔧 Required Changes

### 1. Update GitLab Configuration

Edit `gui_mr_fixer.py` around **line 111**:

```python
# BEFORE (placeholder - won't work):
token = 'YOUR-GITLAB-TOKEN-HERE'
...
'gitlab_url': os.getenv('GITLAB_URL', 'https://gitlab.example.com'),
'gitlab_project_id': os.getenv('GITLAB_PROJECT_ID', 'namespace/project'),
```

```python
# AFTER (your actual values):
token = 'glpat-your-actual-token-here'  # Your real GitLab token
...
'gitlab_url': os.getenv('GITLAB_URL', 'https://gitlab.yourcompany.com'),
'gitlab_project_id': os.getenv('GITLAB_PROJECT_ID', 'your-team/your-project'),
```

### 2. Alternative: Use Environment Variables (RECOMMENDED)

Instead of hardcoding values, use environment variables:

**Windows:**
```powershell
$env:GITLAB_TOKEN="glpat-your-token"
$env:GITLAB_URL="https://gitlab.yourcompany.com"
$env:GITLAB_PROJECT_ID="your-team/your-project"
```

**Linux/macOS:**
```bash
export GITLAB_TOKEN="glpat-your-token"
export GITLAB_URL="https://gitlab.yourcompany.com"
export GITLAB_PROJECT_ID="your-team/your-project"
```

This way you don't need to modify the source code at all!

## 🏗️ Building the Executable

### Option 1: Quick Build

**Windows:**
```powershell
.\build.bat
```

**Linux/macOS:**
```bash
chmod +x build.sh
./build.sh
```

### Option 2: Manual Build

```powershell
# Install dependencies
pip install -r requirements.txt
pip install pyinstaller

# Clean previous build
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

# Build executable
python -m PyInstaller build.spec --noconfirm

# Output: dist/MR_Conflict_Resolver_GUI.exe
```

## 📝 Build Checklist

Before building:
- [ ] Updated `gitlab_url` in `gui_mr_fixer.py` (or using env var)
- [ ] Updated `gitlab_project_id` in `gui_mr_fixer.py` (or using env var)
- [ ] Have GitLab token ready (via env var is best)
- [ ] Installed all dependencies (`pip install -r requirements.txt`)
- [ ] Installed PyInstaller (`pip install pyinstaller`)

After building:
- [ ] Test the executable with a real MR
- [ ] Verify authentication works
- [ ] Check conflict resolution works
- [ ] Test cancel button
- [ ] Verify logs are readable

## 🔒 Security Best Practices

### ✅ DO:
- Use environment variables for sensitive data
- Keep tokens in secure storage
- Use different tokens for different environments
- Rotate tokens regularly
- Use tokens with minimal required permissions

### ❌ DON'T:
- Commit tokens to git
- Share executables with embedded tokens
- Use production tokens in development
- Give tokens excessive permissions
- Share tokens in chat/email

## 🎯 Distribution Options

### For Your Team (Private Use)
1. Build with your company's GitLab URL embedded
2. Distribute executable via internal channels
3. Users still need to set `GITLAB_TOKEN` environment variable

### For Public (GitHub Release)
1. Keep placeholders in source code
2. Build executable with placeholders
3. Users configure via environment variables or config file
4. Document in README how to configure

## 📦 Example: Corporate Build Script

Create `build-corporate.bat`:

```batch
@echo off
REM Build script for corporate use - customized for your environment

REM Set corporate defaults (not in source code)
set CORPORATE_GITLAB_URL=https://gitlab.yourcompany.com
set CORPORATE_PROJECT_ID=your-team/your-project

REM Update gui_mr_fixer.py temporarily (don't commit!)
echo Customizing for corporate environment...
REM (Use sed or similar to replace placeholders)

REM Build
python -m PyInstaller build.spec --noconfirm

REM Revert changes
git checkout gui_mr_fixer.py

echo.
echo ========================================
echo Corporate build complete!
echo Executable: dist\MR_Conflict_Resolver_GUI.exe
echo Users still need to set GITLAB_TOKEN
echo ========================================
```

## 🧪 Testing Your Build

```powershell
# Test with environment variable
$env:GITLAB_TOKEN="glpat-test-token"
.\dist\MR_Conflict_Resolver_GUI.exe

# Try resolving a test MR
# Verify all features work
# Check logs for errors
```

## ❓ Common Issues

### "Authentication Failed"
- Check `GITLAB_TOKEN` environment variable is set
- Verify token has `api` scope
- Confirm token hasn't expired

### "Project Not Found"
- Verify `gitlab_project_id` format: `namespace/project`
- Check token has access to project
- Confirm `gitlab_url` is correct

### "Import Error" when running executable
- Ensure all dependencies in `requirements.txt`
- Check `hiddenimports` in `build.spec`
- Rebuild with `--clean` flag

## 📞 Need Help?

- Check the [README.md](README.md) for full documentation
- Review [QUICKSTART.md](QUICKSTART.md) for setup guide
- Open an issue on GitHub for bugs
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

---

**Remember**: Source code is public-safe (placeholders only). Your built executable is private (contains your settings).
