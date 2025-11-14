# DVOACAP-Python Wiki

Welcome to the DVOACAP-Python documentation wiki! This wiki provides comprehensive guides, tutorials, and reference materials for using and developing with DVOACAP-Python.

## What is DVOACAP-Python?

DVOACAP-Python is a modern Python port of the DVOACAP HF propagation prediction engine. This project provides an accessible, well-documented, and maintainable Python implementation for amateur radio operators and researchers.

### Project Lineage

This is a **port of a port** with a rich history:

1. **VOACAP** (1970s-1990s) - Voice of America Coverage Analysis Program
   - Original FORTRAN implementation by Voice of America / ITS
   - Professional HF broadcast planning tool
   - Industry standard for propagation prediction

2. **DVOACAP** (2000s-2010s) - Digital VOACAP for Amateur Radio
   - Delphi/Pascal port by **Alex Shovkoplyas (VE3NEA)**
   - Modernized for ham radio operators
   - Added user-friendly GUI and visualizations
   - Made VOACAP accessible to amateur radio community

3. **DVOACAP-Python** (2025) - This Project
   - Python port of VE3NEA's DVOACAP
   - Modern Python implementation
   - Cross-platform, open-source
   - Designed for integration with Python scientific ecosystem

**Key Features:**
- Predicts HF radio propagation conditions
- Calculates Maximum Usable Frequency (MUF), signal strength, and reliability
- Includes interactive web dashboard for visualization
- Integrates with modern Python scientific stack (NumPy, SciPy, Matplotlib)
- Validated against original VOACAP reference data

## Quick Navigation

### Getting Started
- **[Getting Started](Getting-Started)** - Installation, basic usage, and first prediction
- **[Quick Examples](Quick-Examples)** - Common use cases and code snippets

### User Guides
- **[Architecture Overview](Architecture)** - Understanding the 5-phase structure
- **[API Reference](API-Reference)** - Core classes, methods, and data structures
- **[Dashboard Guide](Dashboard-Guide)** - Web interface setup and usage
- **[Integration Guide](Integration-Guide)** - Using DVOACAP in your applications

### Validation & Accuracy
- **[Validation Status](Validation-Status)** - Current testing state and accuracy metrics
- **[Comparison Guide](Comparison-Guide)** - DVOACAP vs VOACAP vs ITU P.533
- **[Known Issues](Known-Issues)** - Current limitations and bugs

### Development
- **[Contributing Guide](Contributing)** - How to contribute to the project
- **[Development Setup](Development-Setup)** - Setting up your development environment
- **[Testing Guide](Testing-Guide)** - Running and writing tests

### Troubleshooting
- **[Common Issues](Troubleshooting)** - Solutions to frequent problems
- **[FAQ](FAQ)** - Frequently asked questions
- **[Performance Tips](Performance-Tips)** - Optimizing prediction speed

## Project Status

**Current Phase: 5 of 5 (85% complete)**

- ✅ Phase 1: Path Geometry
- ✅ Phase 2: Solar & Geomagnetic
- ✅ Phase 3: Ionospheric Profiles
- ✅ Phase 4: Raytracing
- 🚧 Phase 5: Signal Predictions (in progress)

See the [Architecture](Architecture) page for detailed module status.

## Repository Links

- **DVOACAP-Python (This Project):** [github.com/skyelaird/dvoacap-python](https://github.com/skyelaird/dvoacap-python)
- **Issues & Discussions:** [github.com/skyelaird/dvoacap-python/issues](https://github.com/skyelaird/dvoacap-python/issues)
- **DVOACAP (VE3NEA's Pascal):** [github.com/VE3NEA/DVOACAP](https://github.com/VE3NEA/DVOACAP)
- **Original VOACAP:** [voacap.com](https://www.voacap.com/)

## License

DVOACAP-Python is released under the MIT License. See the [LICENSE](https://github.com/skyelaird/dvoacap-python/blob/main/LICENSE) file for details.

**Lineage Licenses:**
- **VOACAP** - Public domain / US Government work
- **DVOACAP** - Mozilla Public License Version 1.1
- **DVOACAP-Python** - MIT License (clean-room reimplementation)

## Acknowledgments

**Standing on the Shoulders of Giants:**

- **Voice of America / ITS** - Original VOACAP development team
  - Decades of ionospheric research and professional HF broadcast planning

- **Alex Shovkoplyas (VE3NEA)** - DVOACAP creator
  - Brought VOACAP to amateur radio operators
  - Modernized the code in Delphi/Pascal
  - Made propagation prediction accessible to hams worldwide

- **Amateur Radio Community**
  - Testing, feedback, and propagation data
  - Keeping HF radio alive and thriving

- **Python Scientific Community**
  - NumPy, SciPy, and the amazing Python ecosystem

---

**Amateur Radio Operators:** This tool is designed for HF propagation prediction to help you make better contacts! 73! 📻
