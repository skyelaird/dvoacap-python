# PyPI Setup Guide - Step by Step

This guide walks you through setting up TestPyPI and PyPI accounts, configuring credentials, and publishing your first release.

## Part 1: Create TestPyPI Account (Test First!)

### Step 1: Register on TestPyPI

1. Go to https://test.pypi.org/account/register/
2. Fill in the registration form:
   - Username: Choose a unique username
   - Email: Your email address
   - Password: Create a strong password
3. Click "Sign up"
4. Check your email for verification link
5. Click the verification link to activate your account

### Step 2: Enable 2FA on TestPyPI (Recommended)

1. Log in to https://test.pypi.org
2. Go to Account Settings: https://test.pypi.org/manage/account/
3. Scroll to "Two Factor Authentication"
4. Click "Add 2FA with authentication application"
5. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
6. Enter the 6-digit code to verify

### Step 3: Generate TestPyPI API Token

1. Go to https://test.pypi.org/manage/account/token/
2. Click "Add API token"
3. Fill in:
   - Token name: `dvoacap-github-actions` (or similar)
   - Scope: "Entire account" (you can limit to project after first upload)
4. Click "Add token"
5. **IMPORTANT:** Copy the token immediately! It starts with `pypi-` and you'll only see it once
6. Save it securely (we'll use it in GitHub Secrets)

## Part 2: Create PyPI Account (Production)

### Step 1: Register on PyPI

1. Go to https://pypi.org/account/register/
2. Fill in the registration form (same as TestPyPI)
3. Verify your email address

### Step 2: Enable 2FA on PyPI (Required for Publishing)

1. Log in to https://pypi.org
2. Go to Account Settings: https://pypi.org/manage/account/
3. Enable 2FA (same process as TestPyPI)
4. **IMPORTANT:** 2FA is required to publish packages on PyPI

### Step 3: Generate PyPI API Token

1. Go to https://pypi.org/manage/account/token/
2. Click "Add API token"
3. Fill in:
   - Token name: `dvoacap-github-actions`
   - Scope: "Entire account" (limit to project after first upload)
4. Click "Add token"
5. **IMPORTANT:** Copy the token immediately!
6. Save it securely

## Part 3: Configure GitHub Secrets

### Step 1: Add TestPyPI Token to GitHub

1. Go to your GitHub repository
2. Click "Settings" tab
3. In left sidebar, click "Secrets and variables" → "Actions"
4. Click "New repository secret"
5. Add:
   - Name: `TESTPYPI_API_TOKEN`
   - Value: Paste your TestPyPI token (starts with `pypi-`)
6. Click "Add secret"

### Step 2: Add PyPI Token to GitHub

1. Click "New repository secret"
2. Add:
   - Name: `PYPI_API_TOKEN`
   - Value: Paste your PyPI token (starts with `pypi-`)
3. Click "Add secret"

## Part 4: Configure GitHub Environments (For Trusted Publishing)

The workflow uses PyPI's Trusted Publishing (no API tokens needed!). Set this up:

### Step 1: Create GitHub Environments

1. Go to repository Settings → Environments
2. Click "New environment"
3. Name it `testpypi`
4. (Optional) Add protection rules - require approval before deployment
5. Click "Save protection rules"
6. Repeat for environment named `pypi`

### Step 2: Configure Trusted Publishing on TestPyPI

1. Go to https://test.pypi.org/manage/account/publishing/
2. Scroll to "Add a new pending publisher"
3. Fill in:
   - PyPI Project Name: `dvoacap`
   - Owner: `skyelaird` (your GitHub username/org)
   - Repository name: `dvoacap-python`
   - Workflow name: `publish.yml`
   - Environment name: `testpypi`
4. Click "Add"

### Step 3: Configure Trusted Publishing on PyPI

1. After your first manual upload OR:
2. Go to https://pypi.org/manage/account/publishing/
3. Follow same steps as TestPyPI but use environment name `pypi`

## Part 5: Test with TestPyPI (Manual First Upload)

### Step 1: Install Upload Tools Locally

```bash
pip install --upgrade build twine
```

### Step 2: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ src/dvoacap.egg-info/

# Build fresh distribution
python -m build
```

You should see:
```
Successfully built dvoacap-0.9.0.tar.gz and dvoacap-0.9.0-py3-none-any.whl
```

### Step 3: Upload to TestPyPI

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: Your TestPyPI token (starts with `pypi-`)

### Step 4: Test Installation from TestPyPI

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI (with dependencies from PyPI)
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    dvoacap

# Test it works
python -c "from dvoacap import FourierMaps; print('Success!')"

# Deactivate and cleanup
deactivate
rm -rf test_env
```

## Part 6: Upload to Production PyPI

### Option A: Manual Upload

```bash
# Clean and rebuild
rm -rf dist/ build/ src/dvoacap.egg-info/
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI token

### Option B: Automated via GitHub Actions (Recommended)

#### For TestPyPI:
```bash
# Go to GitHub Actions tab
# Click "Publish to PyPI" workflow
# Click "Run workflow"
# Select: "testpypi"
# Click "Run workflow"
```

#### For PyPI (via GitHub Release):
```bash
# Tag and push
git tag -a v0.9.0 -m "Release v0.9.0"
git push origin v0.9.0

# Create GitHub release (triggers automatic PyPI upload)
gh release create v0.9.0 \
    --title "DVOACAP-Python v0.9.0" \
    --notes "See CHANGELOG.md for details"
```

The workflow will automatically:
1. Build the package
2. Upload to PyPI
3. Attach distribution files to GitHub release

## Part 7: Create GitHub Release

### Using GitHub Web Interface:

1. Go to https://github.com/skyelaird/dvoacap-python/releases/new
2. Click "Choose a tag" → Type `v0.9.0` → "Create new tag"
3. Fill in:
   - Release title: `DVOACAP-Python v0.9.0`
   - Description: Copy from CHANGELOG.md or write summary
4. Click "Publish release"

### Using GitHub CLI:

```bash
# Make sure you're on the right branch and committed
git tag -a v0.9.0 -m "Release v0.9.0: Phase 5 complete, 86.6% validation"
git push origin v0.9.0

# Create release
gh release create v0.9.0 \
    --title "DVOACAP-Python v0.9.0 - Beta Release" \
    --notes-file RELEASE_NOTES.md
```

Sample RELEASE_NOTES.md:
```markdown
# DVOACAP-Python v0.9.0 - Beta Release

## What's New

DVOACAP-Python is now feature-complete with **86.6% validation accuracy**!

### Installation

```bash
pip install dvoacap
```

### Features
- Complete propagation engine (Phases 1-5)
- 86.6% validation accuracy (226/261 tests passing)
- All CCIR/URSI ionospheric data included
- Dashboard with space weather integration

See full documentation at https://github.com/skyelaird/dvoacap-python
```

## Troubleshooting

### "Invalid credentials" when uploading

- Make sure you're using `__token__` as username (not your account username)
- Verify token starts with `pypi-`
- Check token hasn't expired
- Ensure 2FA is enabled on your PyPI account

### "File already exists"

- You cannot re-upload the same version
- Increment version in `pyproject.toml` and `src/dvoacap/__init__.py`
- Rebuild and upload new version

### "Trusted publishing not configured"

- Make sure GitHub environment names match exactly (`testpypi` and `pypi`)
- Verify repository name, owner, and workflow name in PyPI settings
- Do manual upload first, then configure trusted publishing for that project

### Package installs but data files missing

```bash
# Verify data files in wheel
unzip -l dist/dvoacap-0.9.0-py3-none-any.whl | grep "\.dat"
```

Should show 24 .dat files in `dvoacap/DVoaData/`.

## Local PyPI Configuration (Optional)

If you want to use `twine` without entering credentials each time:

```bash
# Create ~/.pypirc
cat > ~/.pypirc <<EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_TOKEN_HERE

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
EOF

chmod 600 ~/.pypirc
```

**WARNING:** Keep this file secure! Contains sensitive API tokens.

## Next Steps

1. ✅ Created TestPyPI account
2. ✅ Created PyPI account
3. ✅ Generated API tokens
4. ✅ Added secrets to GitHub
5. ✅ Tested upload to TestPyPI
6. ✅ Uploaded to production PyPI
7. ✅ Created GitHub release
8. 🎉 Package is live!

Your package is now available:
- PyPI: https://pypi.org/project/dvoacap/
- Install: `pip install dvoacap`
- GitHub: https://github.com/skyelaird/dvoacap-python

## Resources

- PyPI Help: https://pypi.org/help/
- Python Packaging Guide: https://packaging.python.org/
- Twine Docs: https://twine.readthedocs.io/
- GitHub Actions for PyPI: https://github.com/pypa/gh-action-pypi-publish
- Trusted Publishers: https://docs.pypi.org/trusted-publishers/
