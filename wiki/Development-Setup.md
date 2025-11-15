# Development Setup

Complete guide to setting up a development environment for contributing to DVOACAP-Python.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
- [Development Tools](#development-tools)
- [Project Structure](#project-structure)
- [Code Style](#code-style)
- [Testing](#testing)
- [Documentation](#documentation)
- [Git Workflow](#git-workflow)

---

## Prerequisites

### Required Software

**Python 3.8 or higher:**
```bash
# Check your Python version
python3 --version

# Should output: Python 3.8.0 or higher
```

**Git:**
```bash
# Install git (if not already installed)
# Ubuntu/Debian
sudo apt-get install git

# macOS
brew install git

# Windows
# Download from https://git-scm.com/download/win
```

**pip and virtualenv:**
```bash
# Install pip (usually included with Python)
python3 -m ensurepip --upgrade

# Install virtualenv
pip install virtualenv
```

---

## Getting Started

### 1. Fork and Clone Repository

**Fork the repository** on GitHub:
- Visit https://github.com/skyelaird/dvoacap-python
- Click "Fork" button (top-right)

**Clone your fork:**
```bash
git clone https://github.com/YOUR_USERNAME/dvoacap-python.git
cd dvoacap-python
```

**Add upstream remote:**
```bash
git remote add upstream https://github.com/skyelaird/dvoacap-python.git
git fetch upstream
```

---

### 2. Create Virtual Environment

**Create and activate virtual environment:**

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Your prompt should change to show (venv)
```

---

### 3. Install in Development Mode

**Install DVOACAP with all development dependencies:**

```bash
# Install in editable mode with all extras
pip install -e ".[all]"

# This installs:
# - dvoacap library (core)
# - dashboard dependencies (flask, etc.)
# - dev tools (pytest, black, flake8, mypy)
# - documentation tools (sphinx, sphinx-rtd-theme)
```

**Verify installation:**
```bash
# Test import
python3 -c "import dvoacap; print(dvoacap.__version__)"

# Should output: 0.5.0

# Run a quick test
pytest tests/test_path_geometry.py -v
```

---

### 4. Configure Development Tools

**Install pre-commit hooks (optional but recommended):**

```bash
# Install pre-commit
pip install pre-commit

# Set up git hooks
pre-commit install

# Run against all files to test
pre-commit run --all-files
```

---

## Development Tools

### Code Formatting: Black

DVOACAP-Python uses [Black](https://black.readthedocs.io/) for consistent code formatting.

**Configuration** (from `pyproject.toml`):
```toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311', 'py312']
```

**Usage:**
```bash
# Format a single file
black src/dvoacap/path_geometry.py

# Format all Python files
black src/ tests/ examples/

# Check without modifying
black --check src/
```

---

### Linting: Flake8

Use [Flake8](https://flake8.pycqa.org/) for code quality checks.

**Usage:**
```bash
# Lint a file
flake8 src/dvoacap/path_geometry.py

# Lint entire project
flake8 src/ tests/

# Configuration in setup.cfg or pyproject.toml
```

**Common issues:**
- Line too long (E501) - Black should handle this
- Unused imports (F401) - Remove unused imports
- Undefined name (F821) - Check for typos

---

### Type Checking: mypy

Use [mypy](https://mypy.readthedocs.io/) for optional static type checking.

**Configuration** (from `pyproject.toml`):
```toml
[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
```

**Usage:**
```bash
# Check a file
mypy src/dvoacap/path_geometry.py

# Check entire package
mypy src/dvoacap/

# Ignore errors for now (many modules not fully typed)
mypy --ignore-missing-imports src/
```

---

### Testing: pytest

Run tests with [pytest](https://docs.pytest.org/).

**Usage:**
```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_path_geometry.py

# Run specific test function
pytest tests/test_path_geometry.py::test_distance_calculation

# Run with coverage
pytest --cov=dvoacap tests/

# Generate HTML coverage report
pytest --cov=dvoacap --cov-report=html tests/
# Open htmlcov/index.html in browser
```

**Configuration** (from `pyproject.toml`):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

---

## Project Structure

```
dvoacap-python/
├── src/
│   └── dvoacap/                    # Main Python package
│       ├── __init__.py             # Package initialization
│       ├── path_geometry.py        # Phase 1: Path geometry
│       ├── solar.py                # Phase 2: Solar calculations
│       ├── geomagnetic.py          # Phase 2: Geomagnetic field
│       ├── fourier_maps.py         # Phase 3: CCIR/URSI maps
│       ├── ionospheric_profile.py  # Phase 3: Ionosphere modeling
│       ├── layer_parameters.py     # Phase 3: Layer parameters
│       ├── muf_calculator.py       # Phase 4: MUF calculations
│       ├── reflectrix.py           # Phase 4: Raytracing
│       ├── prediction_engine.py    # Phase 5: Prediction engine
│       ├── noise_model.py          # Phase 5: Noise modeling
│       └── antenna_gain.py         # Phase 5: Antenna calculations
│
├── tests/                          # Test suite
│   ├── test_path_geometry.py       # Path geometry tests
│   ├── test_ionospheric.py         # Ionospheric tests
│   └── test_voacap_parser.py       # VOACAP reference tests
│
├── examples/                       # Usage examples
│   ├── complete_prediction_example.py
│   ├── phase4_raytracing_example.py
│   └── integration_example.py
│
├── Dashboard/                      # Web dashboard
│   ├── dashboard.html              # Main UI
│   ├── server.py                   # Flask server
│   ├── generate_predictions.py     # Prediction generator
│   └── README.md                   # Dashboard docs
│
├── DVoaData/                       # CCIR/URSI coefficient data
│   ├── ccir*.asc                   # CCIR coefficients
│   └── ursi*.asc                   # URSI coefficients
│
├── SampleIO/                       # Sample input/output files
│   └── voacap_reference/           # Reference VOACAP output
│
├── docs/                           # Documentation
│   ├── source/                     # Sphinx source
│   ├── build/                      # Built documentation
│   └── *.md, *.pdf                 # Various docs
│
├── wiki/                           # GitHub wiki (this documentation)
│   ├── Home.md
│   ├── Getting-Started.md
│   └── ...
│
├── pyproject.toml                  # Package configuration
├── README.md                       # Main README
├── LICENSE                         # MIT License
└── .gitignore                      # Git ignore rules
```

---

## Code Style

### General Conventions

**Follow PEP 8** with these specifics:
- **Line length:** 100 characters (Black default)
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Grouped (standard library, third-party, local)
- **Naming:**
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

**Example:**
```python
"""Module docstring explaining purpose."""

import math
from typing import List, Tuple

import numpy as np

from dvoacap.path_geometry import GeoPoint


class PredictionEngine:
    """Class docstring explaining the class."""

    MAX_FREQUENCY = 30.0  # Constant

    def __init__(self, location: GeoPoint):
        """Initialize prediction engine."""
        self.location = location
        self._cache = {}  # Private attribute

    def predict(self, frequencies: List[float]) -> np.ndarray:
        """
        Run propagation prediction.

        Args:
            frequencies: List of frequencies in MHz

        Returns:
            Array of predictions
        """
        # Implementation
        pass
```

---

### Docstrings

Use **NumPy/Google style** docstrings:

```python
def calculate_muf(foF2: float, hop_count: int, elevation: float) -> float:
    """
    Calculate Maximum Usable Frequency.

    Args:
        foF2: F2 layer critical frequency in MHz
        hop_count: Number of hops (1-4)
        elevation: Elevation angle in radians

    Returns:
        MUF in MHz

    Raises:
        ValueError: If hop_count < 1

    Example:
        >>> calculate_muf(foF2=8.5, hop_count=2, elevation=0.1)
        15.2
    """
    if hop_count < 1:
        raise ValueError("hop_count must be >= 1")

    # Implementation
    return foF2 * 3.14 / math.sin(elevation)
```

---

### Type Hints

Use type hints for function signatures:

```python
from typing import List, Tuple, Optional
import numpy as np

def process_frequencies(
    frequencies: List[float],
    ssn: float,
    month: int
) -> Tuple[np.ndarray, Optional[str]]:
    """Process frequencies and return results."""
    # Implementation
    pass
```

---

## Testing

### Writing Tests

**Test file structure:**
```python
# tests/test_my_module.py

import pytest
import numpy as np
from dvoacap.my_module import MyClass


class TestMyClass:
    """Tests for MyClass"""

    def test_basic_functionality(self):
        """Test basic usage"""
        obj = MyClass()
        result = obj.method(42)
        assert result == 84

    def test_edge_case(self):
        """Test edge case"""
        obj = MyClass()
        with pytest.raises(ValueError):
            obj.method(-1)

    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
    ])
    def test_multiple_values(self, input, expected):
        """Test multiple input values"""
        obj = MyClass()
        assert obj.method(input) == expected
```

**Run tests:**
```bash
# All tests
pytest

# Specific module tests
pytest tests/test_path_geometry.py

# With coverage
pytest --cov=dvoacap --cov-report=term-missing
```

---

### Validation Tests

**Run VOACAP reference validation:**
```bash
# Full validation suite
python3 test_voacap_reference.py

# Specific phase validation
pytest tests/test_ionospheric.py -v
```

See [Testing Guide](Testing-Guide) for detailed testing instructions.

---

## Documentation

### Building Sphinx Documentation

**Install Sphinx dependencies:**
```bash
pip install -e ".[docs]"
```

**Build HTML documentation:**

**Linux/macOS:**
```bash
cd docs
make html
```

**Windows:**
```powershell
cd docs
.\make.bat html

# Or use PowerShell script
.\make.ps1 html

# Or direct sphinx-build
sphinx-build -M html source build
```

**View documentation:**
```bash
# Open in browser
open docs/build/html/index.html  # macOS
xdg-open docs/build/html/index.html  # Linux
start docs/build/html/index.html  # Windows
```

---

### Contributing to Wiki

Wiki pages are in the `/wiki` directory:

```bash
# Edit a wiki page
vi wiki/Development-Setup.md

# Add new page
vi wiki/New-Page.md

# Commit and push
git add wiki/
git commit -m "Update wiki documentation"
git push origin main
```

---

## Git Workflow

### Branch Strategy

**Main branches:**
- `main` - Stable releases
- Feature branches - Development work

**Create feature branch:**
```bash
# Update main
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature

# Work on your changes
# ...

# Commit regularly
git add .
git commit -m "Add feature description"
```

---

### Making Changes

**1. Make changes:**
```bash
# Edit files
vi src/dvoacap/my_module.py

# Format code
black src/dvoacap/my_module.py

# Run tests
pytest tests/test_my_module.py
```

**2. Commit changes:**
```bash
# Stage changes
git add src/dvoacap/my_module.py tests/test_my_module.py

# Commit with clear message
git commit -m "Add new feature: detailed description"
```

**3. Push to your fork:**
```bash
git push origin feature/my-feature
```

**4. Create Pull Request:**
- Visit your fork on GitHub
- Click "New Pull Request"
- Fill in description
- Submit for review

---

### Keeping Your Fork Updated

```bash
# Fetch upstream changes
git fetch upstream

# Update main
git checkout main
git merge upstream/main

# Rebase feature branch (if needed)
git checkout feature/my-feature
git rebase main

# Resolve any conflicts, then:
git push --force-with-lease origin feature/my-feature
```

---

## Development Workflow Example

**Complete workflow for adding a new feature:**

```bash
# 1. Set up environment
git clone https://github.com/YOUR_USERNAME/dvoacap-python.git
cd dvoacap-python
python3 -m venv venv
source venv/bin/activate
pip install -e ".[all]"

# 2. Create feature branch
git checkout -b feature/add-new-feature

# 3. Make changes
# Edit source files
vi src/dvoacap/new_module.py

# 4. Write tests
vi tests/test_new_module.py

# 5. Format and lint
black src/ tests/
flake8 src/ tests/

# 6. Run tests
pytest tests/test_new_module.py -v

# 7. Update documentation
vi docs/source/api/new_module.rst

# 8. Commit changes
git add src/dvoacap/new_module.py tests/test_new_module.py docs/
git commit -m "Add new module for feature X"

# 9. Push and create PR
git push origin feature/add-new-feature
# Create pull request on GitHub
```

---

## Next Steps

- **[Contributing Guide](Contributing)** - Contribution guidelines
- **[Testing Guide](Testing-Guide)** - Detailed testing instructions
- **[API Reference](API-Reference)** - Code documentation
- **[Architecture](Architecture)** - Project architecture overview

---

## Troubleshooting Development Setup

### "ModuleNotFoundError: No module named 'dvoacap'"

**Solution:**
```bash
# Ensure installed in editable mode
pip install -e .
```

---

### "pytest: command not found"

**Solution:**
```bash
# Install dev dependencies
pip install -e ".[dev]"
```

---

### Black formatting conflicts

**Solution:**
```bash
# Use Black's configuration
black --line-length=100 src/
```

---

### Import errors in tests

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall package
pip install -e .
```

---

**Ready to contribute?** Check out the [Contributing Guide](Contributing) for detailed contribution guidelines!
