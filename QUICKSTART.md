# Quick Start Guide

This guide will help you get started with GitLab MR Conflict Resolver in 5 minutes.

## Prerequisites

- GitLab account with API token
- Python 3.11+ (if running from source)
- Git installed and configured

## Step 1: Get a GitLab Token

1. Log into your GitLab instance
2. Go to **User Settings** → **Access Tokens**
3. Create a new token with scopes:
   - `api` (full API access)
   - `read_repository`
   - `write_repository`
4. Copy the token (starts with `glpat-`)

## Step 2: Configure Authentication

### Option A: Environment Variable (Recommended)

**Windows:**
```powershell
$env:GITLAB_TOKEN="glpat-YOUR-TOKEN-HERE"
$env:GITLAB_URL="https://gitlab.example.com"
$env:GITLAB_PROJECT_ID="namespace/project"
```

**Linux/macOS:**
```bash
export GITLAB_TOKEN="glpat-YOUR-TOKEN-HERE"
export GITLAB_URL="https://gitlab.example.com"
export GITLAB_PROJECT_ID="namespace/project"
```

### Option B: Configuration File

1. Copy `config.example.yaml` to `config_ndo.yaml`
2. Edit with your settings:
   ```yaml
   gitlab_token: "glpat-YOUR-TOKEN-HERE"
   gitlab_url: "https://gitlab.example.com"
   gitlab_project_id: "namespace/project"
   ```

## Step 3: Run the Tool

### Using Pre-built Executable (Windows)

```powershell
# Just double-click MR_Conflict_Resolver_GUI.exe
# Or run from command line:
.\MR_Conflict_Resolver_GUI.exe
```

### Running from Source

```bash
# Install dependencies
pip install -r requirements.txt

# Run the GUI
python gui_mr_fixer.py
```

## Step 4: Resolve Your First MR

1. **Open the GUI** - You'll see a simple interface
2. **Enter MR Number** - Type the MR ID (e.g., `449`)
3. **Click "Resolve Conflicts"** - The tool will:
   - Connect to GitLab ✓
   - Analyze the MR ✓
   - Clone the repository ✓
   - Detect conflicts ✓
   - Resolve conflicts ✓
   - Push the resolution ✓
4. **Watch the Logs** - Real-time progress in the text area
5. **Success!** - Your MR is now conflict-free

## Example Output

```
========================================
GITLAB MR CONFLICT AUTO-FIXER - NDO
========================================

Step 1: Authenticating with GitLab...
  → Using token from environment variable
  ✓ Connected: https://gitlab.example.com
  ✓ Project: namespace/project (ID: 42)

Step 2: Analyzing MR #449...
  ✓ Source: feature-branch → Target: main
  ✓ Author: John Doe
  ⚠️  ISSUE: Merge conflicts

Step 3: Cloning repository...
  ✓ Cloned to: C:\Temp\mr_fixer_abc123

Step 4: Multi-round conflict resolution...
Rebase attempt 1/10...
⚠️  Conflict round 1 detected with 1 file(s)
   • data/schema.yaml
Strategy: theirs
  ✓ data/schema.yaml - kept source (MR changes)
  ✓ Staged: data/schema.yaml
✓ Resolved 1 file(s) in round 1

Rebase attempt 2/10...
✓ Rebase completed successfully!

Force pushing to feature-branch...
✓ Force pushed

========================================
✓ SUCCESS - MR conflicts resolved!
========================================
```

## Common Issues

### "Authentication Failed"
- Check your token is valid
- Ensure token has `api` scope
- Verify `GITLAB_URL` is correct

### "Project Not Found"
- Check `GITLAB_PROJECT_ID` format: `namespace/project`
- Ensure token has access to the project

### "SSL Certificate Error"
- Already disabled by default
- Set `ssl_verify: false` in config

### "No Conflicts Detected"
- MR may not have conflicts
- Try a different MR
- Check if conflicts were already resolved

## Next Steps

- Read the full [README.md](README.md) for advanced features
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- See [config.example.yaml](config.example.yaml) for all options

## Getting Help

- **Issues**: GitHub Issues for bugs
- **Questions**: GitHub Discussions
- **Documentation**: Full README.md

---

**Ready to automate conflict resolution!** 🚀
