# DVOACAP-Python Wiki

Welcome to the DVOACAP-Python documentation wiki! This wiki provides comprehensive guides, tutorials, and reference materials for using and developing with DVOACAP-Python.

## What is DVOACAP-Python?

DVOACAP-Python is a modern Python port of the DVOACAP HF propagation prediction engine, originally written in Delphi/Pascal by Alex Shovkoplyas (VE3NEA). This project provides an accessible, well-documented, and maintainable Python implementation of the VOACAP ionospheric propagation model.

**Key Features:**
- Predicts HF radio propagation conditions
- Calculates Maximum Usable Frequency (MUF), signal strength, and reliability
- **NEW:** VOACAP-style propagation maps with Maidenhead grid overlay
- **NEW:** Mode presets for WSPR, FT8, CW, SSB with proper bandwidth parameters
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
- **[Propagation Maps](Propagation-Maps)** - NEW! VOACAP-style coverage maps
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

**🎉 Production Ready - v1.0.1 Released! 🎉**

**All 5 Development Phases Complete - 86.6% Validation Accuracy + 2.3x Performance Boost**

- ✅ Phase 1: Path Geometry
- ✅ Phase 2: Solar & Geomagnetic
- ✅ Phase 3: Ionospheric Profiles
- ✅ Phase 4: Raytracing
- ✅ Phase 5: Signal Predictions (86.6% validation pass rate across 11 diverse test paths)
- ✅ **NEW in v1.0.1:** Performance optimization - 2.3x faster!

DVOACAP-Python has reached production-ready status with comprehensive HF propagation prediction capabilities, validated against VOACAP reference data, optimized for performance (2.3x speedup in v1.0.1), and ready for real-world amateur radio and professional applications.

See the [Architecture](Architecture) page for detailed module status.

## Repository Links

- **Main Repository:** [github.com/skyelaird/dvoacap-python](https://github.com/skyelaird/dvoacap-python)
- **Issues:** [github.com/skyelaird/dvoacap-python/issues](https://github.com/skyelaird/dvoacap-python/issues)
- **Original DVOACAP:** [github.com/VE3NEA/DVOACAP](https://github.com/VE3NEA/DVOACAP)

## License

DVOACAP-Python is released under the MIT License. See the [LICENSE](https://github.com/skyelaird/dvoacap-python/blob/main/LICENSE) file for details.

## Acknowledgments

- **Alex Shovkoplyas (VE3NEA)** - Original DVOACAP implementation
- **Voice of America / ITS** - Original VOACAP development
- Amateur radio and propagation modeling community

---

**Amateur Radio Operators:** This tool is designed for HF propagation prediction to help you make better contacts! 73! 📻
