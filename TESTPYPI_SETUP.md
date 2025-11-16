# TestPyPI Setup and Publishing Guide

This document outlines the complete process for publishing the `dvoacap` package to TestPyPI and PyPI using GitHub Actions with Trusted Publishing (OIDC).

## Table of Contents

- [Overview](#overview)
- [TestPyPI Setup](#testpypi-setup)
- [GitHub Configuration](#github-configuration)
- [Testing the Publication](#testing-the-publication)
- [PyPI Production Setup](#pypi-production-setup)
- [Troubleshooting](#troubleshooting)

## Overview

The `dvoacap` package uses **Trusted Publishing** (OpenID Connect) for secure, token-free publishing to PyPI and TestPyPI. This is the recommended modern approach that eliminates the need for long-lived API tokens.

### What is Trusted Publishing?

Trusted Publishing uses OpenID Connect (OIDC) to establish trust between GitHub Actions and PyPI. Benefits:
- No API tokens to manage or secure
- Automatic authentication through GitHub Actions
- More secure than traditional token-based authentication
- Recommended by PyPI for all new projects

## TestPyPI Setup

### Step 1: Create TestPyPI Account

✅ **COMPLETED** - TestPyPI account has been created.

### Step 2: Configure Trusted Publisher on TestPyPI

1. **Log in to TestPyPI**: https://test.pypi.org/

2. **Navigate to Publishing Settings**:
   - Go to: https://test.pypi.org/manage/account/publishing/
   - Or: Account Settings → Publishing

3. **Add a New Pending Publisher**:
   - Scroll to "Add a new pending publisher"
   - Fill in the form with these **exact values**:

   ```
   PyPI Project Name:     dvoacap
   Owner:                 skyelaird
   Repository name:       dvoacap-python
   Workflow name:         publish.yml
   Environment name:      testpypi
   ```

4. **Click "Add"**

5. **Verify**:
   - You should see the pending publisher listed
   - Once you publish for the first time, the project will be created automatically

### Step 3: Configure GitHub Environment

1. **Navigate to Repository Environments**:
   - Go to: https://github.com/skyelaird/dvoacap-python/settings/environments

2. **Create/Verify "testpypi" Environment**:
   - If "testpypi" environment doesn't exist, click "New environment"
   - Name it exactly: `testpypi`
   - (Optional) Add protection rules:
     - Required reviewers
     - Deployment branches (e.g., only main branch)

3. **No Secrets Needed**:
   - With Trusted Publishing, no API tokens or secrets are required
   - The workflow uses `id-token: write` permission instead

## Testing the Publication

### Option 1: Manual Workflow Dispatch (Recommended for Testing)

1. **Navigate to Actions**:
   - Go to: https://github.com/skyelaird/dvoacap-python/actions/workflows/publish.yml

2. **Run Workflow**:
   - Click "Run workflow" button
   - Select branch: `claude/testpypi-account-setup-01RnVjrx8TjyqvtbP9HcEXrX` (or `main`)
   - Choose upload destination: `testpypi`
   - Click "Run workflow"

3. **Monitor Progress**:
   - Watch the workflow execution in the Actions tab
   - Check for any errors in the build or publish steps

4. **Verify Publication**:
   - Once successful, visit: https://test.pypi.org/project/dvoacap/
   - You should see version `0.9.0` published

### Option 2: Test Installation from TestPyPI

After successful publication, test installing the package:

```bash
# Create a test virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ dvoacap

# Test the installation
python -c "import dvoacap; print(dvoacap.__version__)"
```

**Note**: The `--extra-index-url` flag allows pip to install dependencies (like `numpy`) from the real PyPI.

## PyPI Production Setup

Once you've successfully tested with TestPyPI, set up the real PyPI:

### Step 1: Create PyPI Account

1. Go to: https://pypi.org/account/register/
2. Create your account
3. Verify your email address

### Step 2: Configure Trusted Publisher on PyPI

1. **Log in to PyPI**: https://pypi.org/

2. **Navigate to Publishing Settings**:
   - Go to: https://pypi.org/manage/account/publishing/

3. **Add a New Pending Publisher**:
   ```
   PyPI Project Name:     dvoacap
   Owner:                 skyelaird
   Repository name:       dvoacap-python
   Workflow name:         publish.yml
   Environment name:      pypi
   ```

4. **Click "Add"**

### Step 3: Configure GitHub "pypi" Environment

1. Go to: https://github.com/skyelaird/dvoacap-python/settings/environments
2. Create environment named: `pypi`
3. **Recommended Protection Rules**:
   - Require reviewer approval before deployment
   - Limit to specific branches (e.g., `main` only)

### Step 4: Publish via GitHub Release

The workflow is configured to automatically publish to PyPI when you create a GitHub release:

1. **Create a Git Tag**:
   ```bash
   git tag v0.9.0
   git push origin v0.9.0
   ```

2. **Create GitHub Release**:
   - Go to: https://github.com/skyelaird/dvoacap-python/releases/new
   - Choose tag: `v0.9.0`
   - Release title: `v0.9.0`
   - Description: Use content from `RELEASE_NOTES_v0.9.0.md`
   - Click "Publish release"

3. **Automatic Publication**:
   - The workflow automatically triggers on release creation
   - Builds the package
   - Publishes to PyPI
   - Uploads distribution files to the GitHub release

## Workflow Details

The `.github/workflows/publish.yml` workflow has three jobs:

### 1. Build Job
- Runs on all triggers
- Checks out code
- Builds source distribution and wheel
- Validates the package with twine
- Uploads artifacts for publishing jobs

### 2. TestPyPI Publishing Job
- Triggers on: Manual workflow dispatch with `testpypi` option
- Downloads build artifacts
- Publishes to TestPyPI using Trusted Publishing
- URL: https://test.pypi.org/legacy/

### 3. PyPI Publishing Job
- Triggers on: GitHub release publication OR manual dispatch with `pypi` option
- Downloads build artifacts
- Publishes to PyPI using Trusted Publishing
- URL: https://pypi.org/p/dvoacap

### 4. GitHub Release Job
- Triggers on: GitHub release publication
- Downloads build artifacts
- Uploads distribution files to the GitHub release

## Troubleshooting

### "Trusted publisher mismatch" Error

**Cause**: The OIDC claim from GitHub doesn't match the trusted publisher configuration.

**Solution**:
- Verify all fields match exactly:
  - Repository owner and name
  - Workflow filename (`publish.yml`)
  - Environment name (`testpypi` or `pypi`)

### "Project does not exist" Error

**Cause**: For TestPyPI/PyPI, the project is created on first publish when using a pending publisher.

**Solution**:
- Ensure you added a **pending publisher** (not trying to add to an existing project)
- The project name in pyproject.toml must match exactly: `dvoacap`

### Build Fails with "Module not found" Errors

**Cause**: Build dependencies not installed.

**Solution**: The workflow already handles this with:
```yaml
python -m pip install build twine
```

### Package Installation Fails from TestPyPI

**Cause**: Dependencies (like `numpy`) don't exist on TestPyPI.

**Solution**: Use both indexes:
```bash
pip install --index-url https://test.pypi.org/simple/ \
           --extra-index-url https://pypi.org/simple/ \
           dvoacap
```

### Permission Denied During Publish

**Cause**: Missing `id-token: write` permission.

**Solution**: Already configured in workflow:
```yaml
permissions:
  id-token: write
```

## Package Information

- **Package Name**: `dvoacap`
- **Current Version**: `0.9.0`
- **Python Support**: 3.11, 3.12, 3.13
- **License**: MIT
- **Homepage**: https://github.com/skyelaird/dvoacap-python

## Next Steps After Setup

1. ✅ Test publish to TestPyPI
2. ✅ Verify installation from TestPyPI
3. ✅ Set up PyPI trusted publisher
4. ✅ Create v0.9.0 release
5. ✅ Verify publication to PyPI
6. 📢 Announce the release!

## Resources

- [PyPI Trusted Publishers Documentation](https://docs.pypi.org/trusted-publishers/)
- [GitHub Actions PyPI Publish Action](https://github.com/pypa/gh-action-pypi-publish)
- [Python Packaging Guide](https://packaging.python.org/)
- [TestPyPI](https://test.pypi.org/)
- [PyPI](https://pypi.org/)

## Support

For issues with this package:
- **Bug Reports**: https://github.com/skyelaird/dvoacap-python/issues
- **Discussions**: https://github.com/skyelaird/dvoacap-python/discussions

For issues with PyPI/TestPyPI:
- **PyPI Help**: https://pypi.org/help/
- **PyPI Support**: https://github.com/pypi/support
