# CI Version Automation

This document describes the automated version management system for PCILeech Firmware Generator.

## Overview

The project now includes automated version updates that:
- Automatically bump version numbers based on commit messages
- Update build metadata (commit hash, build date)
- Integrate with the existing version checker
- Maintain compatibility with manual releases

## Components

### 1. Version Update Script (`scripts/update_version.py`)

The core automation script that:
- Analyzes git commit messages to determine version bump type
- Updates [`src/__version__.py`](../src/__version__.py) with new version and build metadata
- Supports manual override of bump type
- Includes dry-run mode for testing

**Usage:**
```bash
# Auto-detect version bump from commits
python scripts/update_version.py

# Force specific bump type
python scripts/update_version.py --bump-type minor

# Test without making changes
python scripts/update_version.py --dry-run
```

### 2. Auto Version Update Workflow (`.github/workflows/auto-version-update.yml`)

GitHub Actions workflow that:
- Triggers on pushes to main branch (excluding version file changes)
- Automatically updates version based on commit messages
- Commits version changes back to the repository
- Creates release preparation PRs for significant versions

**Trigger Conditions:**
- Push to `main` branch
- Not triggered by version file changes (prevents loops)
- Can be skipped with `[skip version]` in commit message

### 3. Enhanced Version Checker

The existing [`src/cli/version_checker.py`](../src/cli/version_checker.py) now includes:
- Build metadata awareness (commit hash, build date)
- Enhanced update prompts with build information
- Better integration with automated updates

## Commit Message Conventions

The system uses conventional commit messages to determine version bumps:

### Major Version (Breaking Changes)
- `feat!: description` - Feature with breaking change
- Any commit with `BREAKING CHANGE:` in the body

### Minor Version (New Features)
- `feat: description` - New feature
- `feature: description` - Alternative format

### Patch Version (Bug Fixes)
- `fix: description` - Bug fix
- `bugfix: description` - Alternative format
- Any other commit type defaults to patch

### Examples
```bash
# Will trigger minor version bump
git commit -m "feat: add new device support"

# Will trigger patch version bump  
git commit -m "fix: resolve memory leak in parser"

# Will trigger major version bump
git commit -m "feat!: redesign configuration API"

# Will trigger major version bump
git commit -m "feat: add new API

BREAKING CHANGE: removes deprecated methods"
```

## Version File Structure

The [`src/__version__.py`](../src/__version__.py) file contains:

```python
__version__ = "0.9.13"           # Semantic version
__version_info__ = (0, 9, 12)    # Version tuple
__build_date__ = "2025-01-01T12:00:00.000000"  # ISO format
__commit_hash__ = "abc123"       # Short git hash
```

## Workflow Integration

### Automatic Updates
1. Developer pushes commits to `main`
2. Auto-version workflow analyzes commits
3. Version is bumped and committed automatically
4. For significant versions, release PR is created

### Manual Override
Developers can skip automatic updates by:
- Including `[skip version]` in commit message
- Using the manual release script: `scripts/release.py`

### Release Process
1. Automatic version updates handle day-to-day changes
2. Significant versions trigger release preparation PRs
3. Manual releases still supported for full control
4. PyPI publishing remains manual for security

## Testing

### Test Script
Run the test suite to validate version automation:
```bash
python scripts/test_version_update.py
```

### Manual Testing
```bash
# Test version parsing
python -c "
import sys; sys.path.append('scripts')
from update_version import parse_version, bump_version
print(bump_version('1.0.0', 'minor'))  # Should print 1.1.0
"

# Test dry run
python scripts/update_version.py --dry-run --force
```

## Configuration

### Environment Variables
- `PCILEECH_DISABLE_UPDATE_CHECK`: Disable version checking (set in CI)
- `CI`: Automatically detected, disables update checks

### Workflow Configuration
Edit `.github/workflows/auto-version-update.yml` to:
- Change trigger conditions
- Modify version bump logic
- Adjust release preparation behavior

## Troubleshooting

### Version Not Updating
1. Check if commit messages follow conventions
2. Verify workflow isn't skipped with `[skip version]`
3. Ensure push is to `main` branch
4. Check GitHub Actions logs

### Build Metadata Issues
1. Verify git repository is available
2. Check file permissions on `src/__version__.py`
3. Ensure GitPython is installed for local testing

### Workflow Failures
1. Check GitHub Actions permissions
2. Verify GITHUB_TOKEN has write access
3. Review workflow logs for specific errors

## Migration from Manual Process

The automated system is designed to coexist with manual processes:

1. **Existing releases**: Continue to work normally
2. **Manual bumps**: Override automatic updates when needed
3. **Release script**: Still available for complex releases
4. **Version checker**: Enhanced but backward compatible

## Best Practices

1. **Use conventional commits** for predictable version bumps
2. **Review auto-generated versions** before major releases
3. **Test locally** with dry-run mode before pushing
4. **Skip automation** for complex release scenarios
5. **Monitor CI logs** for automation issues

## Future Enhancements

Potential improvements:
- Automatic changelog generation
- Integration with GitHub releases
- Semantic release compatibility
- Custom version schemes
- Release notes automation