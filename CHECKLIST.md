# Repository Reorganization Checklist

Quick reference for reorganizing dvoacap-python repository.

## 📥 Files to Download from Claude

- [ ] README.md
- [ ] .gitignore
- [ ] pyproject.toml
- [ ] requirements.txt
- [ ] src_dvoacap_init.py (rename to __init__.py)

## 📂 Files to Copy

- [ ] Copy README.md → repository root
- [ ] Copy .gitignore → repository root
- [ ] Copy pyproject.toml → repository root
- [ ] Copy requirements.txt → repository root
- [ ] Copy src_dvoacap_init.py → src/dvoacap/__init__.py (rename!)

## 🔄 Files to Move

```bash
move Python\solar.py src\dvoacap\solar.py
move Python\geomagnetic.py src\dvoacap\geomagnetic.py
```

## 🗑️ Files to Remove

```bash
rmdir /s /q Python\__pycache__
# Optional: rmdir Python (after moving all files)
```

## 📝 Git Commands

```bash
# Add new files
git add README.md .gitignore pyproject.toml requirements.txt
git add src/dvoacap/__init__.py

# Add moved files
git add src/dvoacap/solar.py src/dvoacap/geomagnetic.py

# Remove old locations
git rm Python/solar.py Python/geomagnetic.py
git rm -r Python/__pycache__

# Commit
git commit -m "Reorganize repository structure and add Python packaging"

# Push
git push origin main
```

## 🌐 GitHub Website Updates

- [ ] Add description: "Python port of DVOACAP HF propagation prediction engine"
- [ ] Add topics: hf-propagation, ionosphere, voacap, amateur-radio, ham-radio, python, radio-propagation

## ✅ Verification

- [ ] Files in correct locations (see REORGANIZATION_GUIDE.md)
- [ ] `pip install -e .` works without errors
- [ ] `from dvoacap import SolarCalculator` works
- [ ] README displays correctly on GitHub
- [ ] No __pycache__ folders visible on GitHub

## 📊 Expected Result

```
src/dvoacap/
├── __init__.py          ✓ NEW
├── path_geometry.py     ✓ Existing
├── solar.py             ✓ MOVED from Python/
└── geomagnetic.py       ✓ MOVED from Python/
```

---

✨ Once complete, your repository will be a professional Python package!
