# PyPI Release Guide for DVOACAP-Python

## Two-Product Architecture

### Product 1: `dvoacap` Library (PyPI Package)
**Target:** Developers, researchers, programmers
**Purpose:** Programmatic HF propagation prediction engine

### Product 2: DVOACAP Dashboard (Web Application)
**Target:** Ham radio operators, end-users
**Purpose:** Visual propagation analysis and planning

---

## Pre-Release Checklist

### ✅ Completed

- [x] Version consistency (`pyproject.toml` == `__init__.py` == 0.9.0)
- [x] MANIFEST.in created for source distribution
- [x] Package data configuration (DVoaData/*.dat files)
- [x] DVoaData moved into package directory
- [x] FourierMaps updated to find data files in package
- [x] Test build successful (wheels include .dat files)
- [x] Dockerfile created for dashboard deployment
- [x] docker-compose.yml for easy container orchestration

### 📋 Before Release

- [ ] Run full test suite: `pytest tests/`
- [ ] Verify validation still passes: `python validate_predictions.py`
- [ ] Update CHANGELOG.md with release notes
- [ ] Review README.md for accuracy
- [ ] Test installation from wheel in clean environment
- [ ] Create git tag: `git tag -a v0.9.0 -m "Release v0.9.0"`

---

## Release Process

### Step 1: Create PyPI Account

1. Register at https://pypi.org/account/register/
2. Verify email address
3. Enable 2FA (recommended)
4. Generate API token: https://pypi.org/manage/account/token/
   - Scope: "Entire account" (or project-specific after first release)
   - Copy token (starts with `pypi-`)

### Step 2: Configure PyPI Credentials

```bash
# Create/edit ~/.pypirc
cat > ~/.pypirc <<EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_TOKEN_HERE

[testpypi]
username = __token__
password = pypi-YOUR_TESTPYPI_TOKEN_HERE
repository = https://test.pypi.org/legacy/
EOF

chmod 600 ~/.pypirc
```

### Step 3: Test on TestPyPI (Recommended)

```bash
# Build the package
python -m build

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Test installation from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    dvoacap
```

### Step 4: Upload to PyPI

```bash
# Clean previous builds
rm -rf dist/ build/ src/dvoacap.egg-info/

# Build fresh distribution
python -m build

# Check package quality
python -m twine check dist/*

# Upload to PyPI
python -m twine upload dist/*
```

### Step 5: Create GitHub Release

```bash
# Tag the release
git tag -a v0.9.0 -m "Release v0.9.0: Phase 5 complete, 86.6% validation"

# Push tag to GitHub
git push origin v0.9.0

# Create GitHub release (via web UI or gh CLI)
gh release create v0.9.0 \
    --title "DVOACAP-Python v0.9.0" \
    --notes "$(cat CHANGELOG.md | sed -n '/## \[0.9.0\]/,/## \[0.8.0\]/p')" \
    dist/dvoacap-0.9.0.tar.gz \
    dist/dvoacap-0.9.0-py3-none-any.whl
```

---

## Post-Release

### Update Documentation

```bash
# Update badges in README.md
[![PyPI version](https://badge.fury.io/py/dvoacap.svg)](https://badge.fury.io/py/dvoacap)
[![Downloads](https://pepy.tech/badge/dvoacap)](https://pepy.tech/project/dvoacap)
```

### Test User Installation

```bash
# Fresh virtual environment
python -m venv test_env
source test_env/bin/activate

# Install from PyPI
pip install dvoacap

# Verify installation
python -c "from dvoacap import FourierMaps, ControlPoint; print('Success!')"

# Test data files are accessible
python -c "
from dvoacap import FourierMaps
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
print('Data files loaded successfully!')
"
```

### Announce Release

- [ ] GitHub Discussions announcement
- [ ] Twitter/X post with #hamradio #VOACAP hashtags
- [ ] Reddit: r/amateurradio, r/Python
- [ ] QRZ forums
- [ ] eHam.net

---

## Version Strategy

### Current: v0.9.0 (Beta Release)
**Status:** Feature-complete core library, 86.6% validation
**Audience:** Early adopters, developers, testers

**Includes:**
- Complete propagation engine (Phases 1-5)
- CCIR/URSI ionospheric models
- MUF/FOT/reliability calculations
- Noise and antenna modeling
- All required data files

**Missing for v1.0:**
- Dashboard v1.0 features (prop charts, wheel, mini planner)
- Performance optimizations
- Complete API documentation

### Future Releases

**v1.0.0 (Stable Release) - Target: Dec 13, 2025**
- Dashboard enhancements complete
- Production-ready
- Full documentation
- Comprehensive examples

**v1.1.0 - Target: Jan 2026**
- Coverage area maps
- All-year propagation matrix
- Contest planner

**v2.0.0 - Target: Mid 2026**
- Multi-user web service
- Database backend
- Public API
- Mobile app integration

---

## Dashboard Deployment Options

### Option 1: Install with Library

```bash
# Users install library + dashboard together
pip install dvoacap[dashboard]

# Navigate to dashboard directory
cd $(python -c "import dvoacap, os; print(os.path.dirname(dvoacap.__file__))")/../Dashboard

# Run server
python server.py
```

**Pros:** Single install command
**Cons:** Not ideal for non-developers

### Option 2: Docker Container (Recommended for End-Users)

```bash
# Pull from Docker Hub (after you push it)
docker pull skyelaird/dvoacap-dashboard:latest

# Run with environment variables
docker run -d \
    -p 8000:8000 \
    -e CALLSIGN=VE1ATM \
    -e LAT=44.374 \
    -e LON=-64.300 \
    -e GRID=FN74ui \
    --name dvoacap \
    skyelaird/dvoacap-dashboard:latest

# Visit http://localhost:8000
```

**Build and push Docker image:**

```bash
cd Dashboard
docker build -t skyelaird/dvoacap-dashboard:0.9.0 -f Dockerfile ..
docker tag skyelaird/dvoacap-dashboard:0.9.0 skyelaird/dvoacap-dashboard:latest
docker push skyelaird/dvoacap-dashboard:0.9.0
docker push skyelaird/dvoacap-dashboard:latest
```

### Option 3: Docker Compose (Easiest Local Deployment)

```bash
cd Dashboard
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Troubleshooting Release Issues

### Issue: "File already exists on PyPI"

**Solution:** You cannot re-upload the same version. Increment version number:
- Patch: `0.9.0` → `0.9.1` (bug fixes)
- Minor: `0.9.0` → `0.10.0` (new features)
- Major: `0.9.0` → `1.0.0` (breaking changes)

### Issue: "Invalid distribution"

**Solution:** Check with `twine check`:

```bash
python -m twine check dist/*
```

Fix any errors, rebuild, and retry.

### Issue: "Data files not found after install"

**Solution:** Verify package_data in wheel:

```bash
unzip -l dist/dvoacap-0.9.0-py3-none-any.whl | grep "\.dat"
```

Should show 24 .dat files in `dvoacap/DVoaData/`.

### Issue: "Module not found" after install

**Solution:** Check package structure:

```bash
tar -tzf dist/dvoacap-0.9.0.tar.gz | grep "__init__"
```

Should show `src/dvoacap/__init__.py`.

---

## Quality Checklist Before Release

### Code Quality

```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=dvoacap tests/

# Run validation
python validate_predictions.py

# Check type hints (if using mypy)
mypy src/dvoacap/
```

### Documentation

- [ ] README.md is accurate and up-to-date
- [ ] CHANGELOG.md has release notes
- [ ] LICENSE file is present
- [ ] examples/ directory has working code samples
- [ ] API docstrings are complete

### Package Metadata

- [ ] Version number is correct and consistent
- [ ] Author and maintainer info is accurate
- [ ] Keywords are relevant for PyPI search
- [ ] Classifiers are appropriate
- [ ] URLs point to correct locations
- [ ] License is specified correctly

---

## Release Announcement Template

### GitHub Release Notes

```markdown
# DVOACAP-Python v0.9.0 - Beta Release

## 🎉 What's New

DVOACAP-Python is now feature-complete with **86.6% validation accuracy** against reference VOACAP data!

### Core Features

✅ **Complete propagation engine** (Phases 1-5)
- Path geometry calculations
- Solar & geomagnetic modeling
- CCIR/URSI ionospheric profiles
- Raytracing and MUF calculations
- Signal predictions with noise and antenna models

✅ **Production-ready library**
- Available on PyPI: `pip install dvoacap`
- Includes all required CCIR/URSI data files
- Clean Python API for developers

✅ **Interactive dashboard**
- Flask web server with real-time predictions
- Space weather integration (NOAA SWPC)
- DXCC tracking
- Docker support for easy deployment

## 📦 Installation

**For developers:**
```bash
pip install dvoacap
```

**For dashboard users:**
```bash
pip install dvoacap[dashboard]
```

**Using Docker:**
```bash
docker pull skyelaird/dvoacap-dashboard:0.9.0
docker run -p 8000:8000 skyelaird/dvoacap-dashboard:0.9.0
```

## 📊 Validation

- **226 of 261 tests passing** (86.6%)
- Validated against reference VOACAP outputs
- Real-world validation with PSKReporter data
- Comprehensive test coverage across 11 diverse scenarios

## 📚 Documentation

- [README](README.md) - Project overview
- [Usage Guide](docs/USAGE.md) - API examples
- [Integration Guide](docs/INTEGRATION.md) - Web app integration
- [Dashboard Guide](Dashboard/README.md) - Dashboard setup

## 🔮 What's Next (v1.0)

Coming December 2025:
- Enhanced propagation charts (REL/SDBW/SNR)
- Propagation wheel visualization
- Mini planner for DXCC targeting
- Best frequency recommendations

See [V1_RELEASE_PLAN.md](V1_RELEASE_PLAN.md) for full roadmap.

## 🙏 Acknowledgments

- **Alex Shovkoplyas (VE3NEA)** - Original DVOACAP implementation
- **NOAA SWPC** - Space weather data
- Amateur radio community for testing and feedback

---

**73 de VE1ATM** 📻
```

---

## Support and Maintenance

### Issue Tracking

Monitor GitHub issues for:
- Bug reports
- Feature requests
- Installation problems
- Documentation improvements

### Quick Response Template

```markdown
Thanks for reporting this!

To help diagnose the issue, could you provide:
1. Python version: `python --version`
2. Package version: `pip show dvoacap`
3. Installation method: PyPI, editable, Docker?
4. Full error traceback

Meanwhile, you can try:
- Update to latest version: `pip install --upgrade dvoacap`
- Reinstall: `pip uninstall dvoacap && pip install dvoacap`
- Check data files: `python -c "from dvoacap import FourierMaps; FourierMaps()"`
```

---

## Additional Resources

- **PyPI Best Practices:** https://packaging.python.org/
- **Twine Documentation:** https://twine.readthedocs.io/
- **Semantic Versioning:** https://semver.org/
- **Docker Hub:** https://hub.docker.com/

---

**Last Updated:** 2025-11-16
**Next Release Target:** v1.0.0 (December 13, 2025)
