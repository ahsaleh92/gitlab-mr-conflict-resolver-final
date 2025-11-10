# Contributing to GitLab MR Conflict Resolver

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/gitlab-mr-conflict-resolver.git
   cd gitlab-mr-conflict-resolver
   ```
3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes**
   - Test GUI functionality
   - Test with real GitLab MRs (if possible)
   - Ensure no regressions

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Open a Pull Request**
   - Describe what your PR does
   - Reference any related issues
   - Include screenshots for UI changes

## Commit Message Guidelines

Use conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Example:
```
feat: Add support for custom merge strategies per file type
```

## Code Style

- **Python**: Follow PEP 8 guidelines
- **Line length**: Max 120 characters
- **Docstrings**: Use for all classes and functions
- **Type hints**: Preferred for function signatures

Example:
```python
def resolve_conflict(file_path: str, strategy: str) -> bool:
    """
    Resolve a single file conflict using the specified strategy.
    
    Args:
        file_path: Path to the conflicting file
        strategy: Resolution strategy ('theirs' or 'ours')
    
    Returns:
        True if resolution successful, False otherwise
    """
    # Implementation
```

## Testing

### Manual Testing
1. Set up a test GitLab project with MRs that have conflicts
2. Test different scenarios:
   - Single file conflicts
   - Multiple file conflicts
   - Multi-round conflicts (multiple commits)
   - Large files
   - Binary files
   - SSL/proxy configurations

### Test Checklist
- [ ] GUI loads correctly
- [ ] Authentication works (env var and embedded)
- [ ] MR detection works
- [ ] Conflict resolution works
- [ ] Force push succeeds
- [ ] Cancel button works
- [ ] Error handling is graceful
- [ ] Logs are clear and helpful

## Areas for Contribution

### High Priority
- [ ] Add unit tests
- [ ] Add integration tests
- [ ] Linux/macOS support and builds
- [ ] Command-line interface
- [ ] Better error messages

### Medium Priority
- [ ] Conflict preview mode (show what will be resolved)
- [ ] Batch MR processing
- [ ] Custom strategies per file type
- [ ] Undo/rollback functionality
- [ ] Configuration GUI

### Low Priority
- [ ] Dark mode theme
- [ ] Internationalization (i18n)
- [ ] Plugin system
- [ ] Web-based interface

## Security

### Reporting Security Issues
**Do not open public issues for security vulnerabilities.**

Email security concerns to: [maintainer email]

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Guidelines
- Never commit tokens or credentials
- Use environment variables for sensitive data
- Sanitize user inputs
- Validate GitLab API responses
- Use HTTPS for all API calls

## Documentation

Update documentation for:
- New features
- Configuration options
- API changes
- Breaking changes

Documentation files:
- `README.md` - Main documentation
- `CHANGELOG.md` - Version history
- Code comments - Inline documentation

## Building Releases

### Building Executable
```bash
python -m PyInstaller build.spec --noconfirm
```

### Pre-release Checklist
- [ ] Update version in code
- [ ] Update CHANGELOG.md
- [ ] Test on Windows/Linux/macOS
- [ ] Build executables
- [ ] Test executables
- [ ] Create git tag
- [ ] Create GitHub release
- [ ] Upload executables

## Questions?

- Open a GitHub Discussion for questions
- Open an Issue for bugs
- Join our community chat (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉
