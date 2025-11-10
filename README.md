# GitLab MR Conflict Resolver

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

A GUI-based tool to automatically resolve GitLab merge request conflicts, specifically designed for Terraform/NDO environments with multiple workspaces.

## Features

✅ **GUI Interface** - User-friendly graphical interface with real-time logging  
✅ **Multi-Round Resolution** - Handles MRs with multiple commits, each having conflicts  
✅ **Smart Conflict Detection** - Automatically detects and resolves conflicts  
✅ **Configurable Strategy** - Choose between 'theirs' (keep MR changes) or 'ours' (keep target)  
✅ **Cancel Support** - Working cancel button to stop operations  
✅ **Corporate Network Ready** - SSL verification disabled, proxy bypass enabled by default  
✅ **Secure Authentication** - Environment variable priority, embedded token fallback  
✅ **Non-Interactive Git** - Prevents hanging on git operations  
✅ **MR Author Attribution** - Commits show actual MR author, not token user  

## Quick Start

### Option 1: Use Pre-built Executable (Windows)

1. Download `MR_Conflict_Resolver_GUI.exe` from releases
2. Double-click to run
3. Enter MR number and click "Resolve Conflicts"

### Option 2: Run from Source

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/gitlab-mr-conflict-resolver.git
cd gitlab-mr-conflict-resolver

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python gui_mr_fixer.py
```

## Configuration

### Environment Variables (Recommended)

```bash
# GitLab Authentication
export GITLAB_TOKEN="glpat-your-token-here"
export GITLAB_URL="https://gitlab.example.com"
export GITLAB_PROJECT_ID="namespace/project"

# Optional: Corporate network settings
export CORP_NETWORK="true"  # Disables SSL verification
```

### Embedded Configuration

The tool has embedded defaults that work for most environments:
- **SSL Verification**: Disabled (for self-signed certificates)
- **Proxy Bypass**: Enabled (for corporate networks)
- **Strategy**: `theirs` (keeps MR changes during rebase)
- **Auto Push**: Enabled

### External Configuration File (Optional)

Create `config_ndo.yaml` to override defaults:

```yaml
gitlab_token: "glpat-your-token"  # Or use environment variable
gitlab_url: "https://gitlab.example.com"
gitlab_api_url: "https://gitlab.example.com/api/v4"
gitlab_project_id: "namespace/project"

conflict_resolution:
  strategy: theirs  # 'theirs' keeps MR changes, 'ours' keeps target
  auto_push: true

# Corporate network settings
ssl_verify: false      # Disable for self-signed certs
bypass_proxy: true     # Bypass proxy for git operations
```

## How It Works

1. **Authenticate** - Connects to GitLab using token (env var or embedded)
2. **Analyze MR** - Fetches MR details, source/target branches
3. **Clone Repository** - Clones project locally (60s timeout)
4. **Detect Conflicts** - Checks for merge conflicts
5. **Multi-Round Resolution**:
   - Attempt rebase onto target branch
   - If conflicts detected, resolve using strategy
   - Stage resolved files with verification
   - Continue rebase for next commit
   - Repeat until all commits processed (max 10 rounds)
6. **Force Push** - Pushes resolved branch to GitLab
7. **Success** - MR is now conflict-free and ready to merge

## Conflict Resolution Strategy

During `git rebase origin/target`:
- **`theirs`** = Source branch (MR changes) ✅ **Recommended for MRs**
- **`ours`** = Target branch (base/main) ⚠️ Use only if you want to discard MR changes

The default strategy is `theirs` which keeps the MR changes.

## Building from Source

### Requirements
- Python 3.11+
- PyInstaller 6.16.0+
- GitPython 3.1.0+
- python-gitlab 6.0.0+

### Build Executable

```bash
# Install build dependencies
pip install pyinstaller

# Build single executable
python -m PyInstaller build.spec --noconfirm

# Output: dist/MR_Conflict_Resolver_GUI.exe (~16 MB)
```

## Security Considerations

### Token Security
- ✅ **Best Practice**: Use environment variables (`GITLAB_TOKEN`)
- ✅ **CI/CD**: Token auto-detected from `CI_JOB_TOKEN`
- ⚠️ **Embedded Token**: Fallback only, change default before building
- ❌ **Never commit tokens** to version control

### SSL and Proxy
- SSL verification disabled by default (corporate self-signed certs)
- Proxy bypass enabled by default (corporate networks)
- Configure `ssl_verify: true` if needed

### Git Operations
- Non-interactive mode enabled (prevents hanging)
- Timeout protection on clone operations (60s)
- MR author attribution (commits show actual author)

## Troubleshooting

### "SSL Certificate Verify Failed"
- Already disabled by default
- Ensure `ssl_verify: false` in config
- Or set `CORP_NETWORK=true`

### "Git Clone Timeout"
- Large repos may timeout (60s default)
- Check network connectivity
- Verify proxy settings

### "Git Rebase Hanging"
- Non-interactive mode already enabled
- Check git version (2.0+ required)

### "HTTP 500 from GitLab API"
- Not a tool issue - GitLab backend problem
- Check GitLab system health
- Retry pipeline or contact GitLab admin

### "Author shows as 'ndo-token'"
- Tool automatically uses MR author information
- Ensure GitLab token has API access
- Check MR author details in GitLab

## Use Cases

### Terraform/NDO Environments
- Multiple workspace directories (60+)
- Schema YAML conflicts
- Automated drift fix pipelines

### CI/CD Integration
```yaml
# .gitlab-ci.yml
resolve_conflicts:
  stage: pre-merge
  script:
    - ./MR_Conflict_Resolver_GUI.exe --mr $CI_MERGE_REQUEST_IID
  only:
    - merge_requests
  when: manual
```

### Manual Resolution
- Open GUI
- Enter MR number
- Click "Resolve Conflicts"
- Monitor real-time logs

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

- **Issues**: Report bugs on GitHub Issues
- **Questions**: Open a discussion on GitHub
- **Enterprise Support**: Contact repository owner

## Credits

Developed for NDO/Terraform environments with 60+ workspaces and complex merge conflict scenarios.

---

**⚠️ Important**: Always review resolved conflicts before merging to production. This tool uses automated strategies that may not be appropriate for all scenarios.
