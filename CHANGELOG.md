# Changelog

All notable changes to GitLab MR Conflict Resolver will be documented in this file.

## [1.0.0] - 2025-11-10

### Added
- 🎉 Initial release
- GUI-based interface with real-time logging
- Multi-round conflict resolution (handles MRs with multiple commits)
- Configurable conflict resolution strategy ('theirs' or 'ours')
- Environment variable authentication with embedded fallback
- SSL verification disabled by default (corporate networks)
- Proxy bypass enabled by default
- Non-interactive git mode (prevents hanging)
- MR author attribution (commits show actual author)
- Working cancel button
- Git add verification with retry
- 60-second timeout on git clone
- Detailed authentication logging
- Large file warnings (>1MB)
- Progress callback error logging
- Single executable build (Windows)

### Security Enhancements
- Token never in source code (env var priority, embedded at build time)
- SSL verification configurable
- Proxy bypass configurable
- No external dependencies at runtime

### Fixed
- Git timeout parameter bug (removed invalid --timeout flag)
- Git rebase hanging (GIT_EDITOR=true, GIT_TERMINAL_PROMPT=0)
- has_conflicts flag detection
- Cancel button actually stops operations
- Git staging verification

### Tested
- MR #449: Successfully resolved 1 conflict in 2 rounds
- Force push working correctly
- Proper author attribution verified

## [Unreleased]

### Planned Features
- Linux/macOS executable builds
- Command-line interface option
- Conflict resolution preview mode
- Batch MR processing
- Custom merge strategies per file type
- Integration with GitLab webhooks
