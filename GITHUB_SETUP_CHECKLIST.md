# GitHub Repository Setup Checklist

Use this checklist after creating your GitHub repository.

## Repository Settings

### Basic Information
- [ ] Repository name: `gitlab-mr-conflict-resolver`
- [ ] Description: "🔧 GUI tool to automatically resolve GitLab merge request conflicts for Terraform/NDO environments"
- [ ] Website: (Optional) Your documentation URL
- [ ] Topics/Tags:
  - [ ] `gitlab`
  - [ ] `merge-conflicts`
  - [ ] `automation`
  - [ ] `terraform`
  - [ ] `devops`
  - [ ] `python`
  - [ ] `gui`
  - [ ] `conflict-resolution`
  - [ ] `cicd`
  - [ ] `ndo`

### Features to Enable
- [ ] ✅ Issues
- [ ] ✅ Projects
- [ ] ✅ Discussions (recommended for Q&A)
- [ ] ✅ Wiki (optional)
- [ ] ✅ Releases

### Branch Protection (Optional but Recommended)
- [ ] Protect `main` branch
- [ ] Require pull request reviews (at least 1)
- [ ] Require status checks to pass
- [ ] Require conversation resolution before merging
- [ ] Do not allow bypassing the above settings

## GitHub Actions

### Enable Actions
- [ ] Go to "Actions" tab
- [ ] Enable workflows
- [ ] Verify workflows appear:
  - [ ] `build-release.yml` - Builds executables on tag push
  - [ ] `tests.yml` - Runs tests on push/PR

### Secrets (Optional)
If you want to auto-deploy:
- [ ] Add `GITLAB_TOKEN` secret (for testing)
- [ ] Add other secrets as needed

## Issue Templates

Create issue templates for better bug reports:

### Bug Report Template
```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
If applicable, add screenshots.

**Environment:**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.11.5]
- GitLab version: [e.g., 16.0]

**Additional context**
Any other context about the problem.
```

### Feature Request Template
```markdown
**Is your feature request related to a problem?**
A clear description of the problem.

**Describe the solution you'd like**
What you want to happen.

**Describe alternatives you've considered**
Other solutions you've thought about.

**Additional context**
Any other context or screenshots.
```

## Pull Request Template

Create `.github/pull_request_template.md`:

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tested locally
- [ ] Added/updated tests
- [ ] All tests pass

## Checklist
- [ ] Code follows project style
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No console warnings/errors
- [ ] Commit messages follow conventional commits
```

## Security

### Security Policy
Create `SECURITY.md`:

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

**Do not open public issues for security vulnerabilities.**

Email: [your-email@example.com]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will respond within 48 hours.
```

### Code Scanning (Optional)
- [ ] Enable Dependabot alerts
- [ ] Enable code scanning (CodeQL)
- [ ] Enable secret scanning

## Community Files

### Code of Conduct
- [ ] Add CODE_OF_CONDUCT.md (use GitHub's template)

### Support
Create `SUPPORT.md`:

```markdown
# Support

## Getting Help

- 📖 Read the [Documentation](README.md)
- 🚀 Check the [Quick Start Guide](QUICKSTART.md)
- 💬 Ask in [GitHub Discussions](../../discussions)
- 🐛 Report bugs in [Issues](../../issues)

## Before Opening an Issue

1. Search existing issues
2. Check documentation
3. Try latest version
4. Provide complete information

## Community

- Be respectful and constructive
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)
- Help others when possible
```

## Release Process

When creating releases:

1. **Update version** in code
2. **Update CHANGELOG.md** with changes
3. **Create git tag**:
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
4. **GitHub Actions will**:
   - Build executables automatically
   - Create draft release
5. **Edit release notes** on GitHub
6. **Publish release**

## Badges for README

Add these to top of README.md:

```markdown
![Build](https://github.com/YOUR_USERNAME/gitlab-mr-conflict-resolver/actions/workflows/build-release.yml/badge.svg)
![Tests](https://github.com/YOUR_USERNAME/gitlab-mr-conflict-resolver/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/github/license/YOUR_USERNAME/gitlab-mr-conflict-resolver)
![Release](https://img.shields.io/github/v/release/YOUR_USERNAME/gitlab-mr-conflict-resolver)
![Downloads](https://img.shields.io/github/downloads/YOUR_USERNAME/gitlab-mr-conflict-resolver/total)
```

## Social Preview

Create a social preview image (1280x640px) showing:
- Tool name
- Key features
- Screenshot of GUI

Upload in: Settings → Options → Social preview

## README Enhancements

Consider adding:
- [ ] Demo GIF/video
- [ ] Architecture diagram
- [ ] Comparison with alternatives
- [ ] Performance metrics
- [ ] Testimonials/use cases

## Marketing

After publishing:
- [ ] Share on LinkedIn
- [ ] Share on Twitter/X
- [ ] Post on Reddit (r/devops, r/gitlab, r/terraform)
- [ ] Write blog post
- [ ] Submit to awesome lists
- [ ] Add to GitLab integrations

---

**Checklist complete?** Your repository is professional and ready for the community! 🎉
