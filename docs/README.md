# DVOACAP Python Documentation

This directory contains the Sphinx documentation for DVOACAP Python.

## Building the Documentation

### Prerequisites

Install Sphinx and required extensions:

```bash
pip install sphinx sphinx-rtd-theme
```

### Build HTML Documentation

#### On Linux/macOS:

From the `docs/` directory:

```bash
make html
```

#### On Windows:

From the `docs/` directory:

**Option 1 - Using the batch file (PowerShell or CMD):**
```powershell
.\make.bat html
```

**Option 2 - Using the PowerShell script:**
```powershell
.\make.ps1 html
```

**Option 3 - Using sphinx-build directly:**
```powershell
sphinx-build -M html source build
```

**Note:** The `make` command without the `.\` prefix won't work on Windows PowerShell. You must use one of the options above.

The built documentation will be in `docs/build/html/`. Open `docs/build/html/index.html` in your browser.

### Build Other Formats

#### Linux/macOS:
```bash
make latexpdf  # PDF via LaTeX
make epub      # EPUB format
make man       # Man pages
```

#### Windows:
```powershell
.\make.bat latexpdf  # PDF via LaTeX (or .\make.ps1 latexpdf)
.\make.bat epub      # EPUB format (or .\make.ps1 epub)
.\make.bat man       # Man pages (or .\make.ps1 man)
```

### Clean Build

#### Linux/macOS:
```bash
make clean
```

#### Windows:
```powershell
.\make.bat clean  # or .\make.ps1 clean
```

## Documentation Structure

```
docs/
├── source/
│   ├── conf.py           # Sphinx configuration
│   ├── index.rst         # Main documentation page
│   ├── api.rst           # API reference
│   ├── overview.rst      # Project overview
│   ├── installation.rst  # Installation guide
│   ├── quickstart.rst    # Quick start guide
│   ├── examples.rst      # Example code
│   ├── _static/          # Static files (CSS, images)
│   └── _templates/       # Custom templates
├── build/                # Built documentation (generated)
└── Makefile              # Build commands

```

## Writing Documentation

The documentation is written in reStructuredText (RST) format. Key resources:

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [reStructuredText Primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html)
- [Napoleon Extension](https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html) (Google/NumPy style docstrings)

## Docstring Format

Use Google-style docstrings in the source code:

```python
def calculate_something(param1: float, param2: str) -> bool:
    """
    Brief description of the function.

    More detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised

    Example:
        >>> calculate_something(1.5, "test")
        True
    """
    pass
```

## Auto-Documentation

The API reference is automatically generated from docstrings using the `autodoc` extension.
Add new modules to `source/api.rst` to include them in the documentation.
