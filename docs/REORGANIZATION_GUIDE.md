# DVOACAP-Python Repository Reorganization Guide

## 🎯 Goal
Transform the repository into a proper Python package with correct structure and documentation.

---

## 📋 Files to Add/Update

### New Files Created:
1. ✅ `README.md` - Comprehensive project README
2. ✅ `.gitignore` - Python-specific ignore rules
3. ✅ `pyproject.toml` - Modern Python packaging configuration
4. ✅ `requirements.txt` - Dependency list
5. ✅ `src/dvoacap/__init__.py` - Package initialization

---

## 🔧 Step-by-Step Instructions

### Step 1: Backup Current State (Optional but Recommended)
```bash
cd "D:\Python Scripts\dvoacap-python"
git status
git log --oneline -5
```

### Step 2: Add New Files to Repository Root

**Copy these files from Claude's outputs to your repository root:**

1. **README.md** → `D:\Python Scripts\dvoacap-python\README.md`
   - Replace the existing Readme.txt content
   
2. **.gitignore** → `D:\Python Scripts\dvoacap-python\.gitignore`
   - Create new file at root
   
3. **pyproject.toml** → `D:\Python Scripts\dvoacap-python\pyproject.toml`
   - Create new file at root
   
4. **requirements.txt** → `D:\Python Scripts\dvoacap-python\requirements.txt`
   - Create new file at root

5. **src/dvoacap/__init__.py** → `D:\Python Scripts\dvoacap-python\src\dvoacap\__init__.py`
   - Note: File provided as `src_dvoacap_init.py` - rename when copying

### Step 3: Move Python Modules to Correct Location

**Move Phase 2 modules from `Python/` to `src/dvoacap/`:**

```bash
# In your repository directory
cd "D:\Python Scripts\dvoacap-python"

# Move solar.py
move Python\solar.py src\dvoacap\solar.py

# Move geomagnetic.py
move Python\geomagnetic.py src\dvoacap\geomagnetic.py

# Verify they're in the right place
dir src\dvoacap
```

**Expected result in `src/dvoacap/`:**
- `__init__.py` (new)
- `path_geometry.py` (already there ✓)
- `solar.py` (moved)
- `geomagnetic.py` (moved)

### Step 4: Clean Up Old Files

```bash
# Remove __pycache__ directories (they're in .gitignore now)
rmdir /s /q Python\__pycache__

# Optional: Remove empty Python directory after moving files
# (Only if you've moved everything out)
rmdir Python
```

### Step 5: Update Git Repository

```bash
cd "D:\Python Scripts\dvoacap-python"

# Stage new files
git add README.md
git add .gitignore
git add pyproject.toml
git add requirements.txt
git add src/dvoacap/__init__.py

# Stage moved files
git add src/dvoacap/solar.py
git add src/dvoacap/geomagnetic.py

# Remove old locations (Git will track the move)
git rm Python/solar.py
git rm Python/geomagnetic.py
git rm -r Python/__pycache__

# Check status
git status
```

**Expected git status output:**
```
renamed:    Python/solar.py -> src/dvoacap/solar.py
renamed:    Python/geomagnetic.py -> src/dvoacap/geomagnetic.py
deleted:    Python/__pycache__/*
new file:   README.md
new file:   .gitignore
new file:   pyproject.toml
new file:   requirements.txt
new file:   src/dvoacap/__init__.py
```

### Step 6: Commit Changes

```bash
git commit -m "Reorganize repository structure and add Python packaging

Repository Structure:
- Move Python modules to src/dvoacap/ for proper package structure
- Add comprehensive README.md for Python port
- Add .gitignore for Python projects
- Add pyproject.toml for modern Python packaging
- Add requirements.txt for dependencies
- Add src/dvoacap/__init__.py for package initialization

Cleanup:
- Remove __pycache__ directories from tracking
- Organize all Python modules under src/dvoacap/

Package Installation:
- Repository can now be installed with: pip install -e .
- Proper module imports: from dvoacap import SolarCalculator

This completes the transition to a proper Python package structure."
```

### Step 7: Push to GitHub

```bash
git push origin main
```

### Step 8: Update GitHub Repository Settings

**On GitHub website (github.com/skyelaird/dvoacap-python):**

1. Click "About" (⚙️ gear icon in top right)
2. Add description: 
   ```
   Python port of DVOACAP HF propagation prediction engine
   ```
3. Add website (optional):
   ```
   https://github.com/VE3NEA/DVOACAP
   ```
4. Add topics:
   - `hf-propagation`
   - `ionosphere`
   - `voacap`
   - `amateur-radio`
   - `ham-radio`
   - `python`
   - `radio-propagation`

---

## ✅ Verification

After completing all steps, verify:

### 1. File Structure Check
```bash
tree /F src\dvoacap
```

**Expected output:**
```
src\dvoacap
├── __init__.py
├── path_geometry.py
├── solar.py
└── geomagnetic.py
```

### 2. Package Installation Check
```bash
pip install -e .
```

**Should install successfully without errors**

### 3. Import Check
```bash
python -c "from dvoacap import SolarCalculator, GeomagneticCalculator; print('✓ Imports working!')"
```

**Should print:** `✓ Imports working!`

### 4. GitHub Check
- Visit: https://github.com/skyelaird/dvoacap-python
- README.md should display nicely with badges
- About section should have description
- No `__pycache__` folders visible
- Files organized correctly

---

## 🎯 Final Structure

After reorganization, your repository should look like:

```
dvoacap-python/
├── README.md                 ← New comprehensive README
├── LICENSE                   ← Existing
├── .gitignore               ← New Python .gitignore
├── pyproject.toml           ← New packaging config
├── requirements.txt         ← New dependencies
│
├── src/
│   ├── dvoacap/             ← Python package
│   │   ├── __init__.py      ← New package init
│   │   ├── path_geometry.py ← Phase 1 (existing)
│   │   ├── solar.py         ← Phase 2 (moved)
│   │   └── geomagnetic.py   ← Phase 2 (moved)
│   └── original/            ← Reference Pascal code
│       └── *.pas
│
├── tests/                   ← Test files
│   └── test_path_geometry.py
│
├── examples/                ← Usage examples
│   ├── integration_example.py
│   └── phase2_integration_example.py
│
├── docs/                    ← Documentation PDFs
│   └── *.pdf
│
├── DVoaData/                ← CCIR/URSI data
│   └── *.dat
│
└── SampleIO/                ← Sample I/O files
    └── *.json
```

---

## 🚨 Troubleshooting

### Problem: Git won't track file moves
**Solution:** Use `git mv` instead:
```bash
git mv Python/solar.py src/dvoacap/solar.py
git mv Python/geomagnetic.py src/dvoacap/geomagnetic.py
```

### Problem: Import errors after reorganization
**Solution:** Reinstall package:
```bash
pip uninstall dvoacap
pip install -e .
```

### Problem: .gitignore not working for __pycache__
**Solution:** Remove from tracking first:
```bash
git rm -r --cached Python/__pycache__
git commit -m "Remove __pycache__ from tracking"
```

### Problem: Merge conflicts after push
**Solution:** Pull first, then push:
```bash
git pull origin main
git push origin main
```

---

## 📞 Questions?

If you encounter any issues during reorganization, check:
1. Are you in the correct directory? (`dvoacap-python`)
2. Have you committed previous changes?
3. Are file paths correct for Windows? (use `\` not `/`)
4. Did you rename `src_dvoacap_init.py` to `__init__.py`?

---

## ✨ After Completion

Once reorganized, you can:
- Install the package: `pip install -e .`
- Import modules: `from dvoacap import SolarCalculator`
- Run tests: `pytest tests/`
- Share the repository with proper Python structure!

**The repository will be a professional, installable Python package! 🎉**
