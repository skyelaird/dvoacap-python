# Contributing to DVOACAP-Python

Thank you for your interest in contributing to DVOACAP-Python! This project aims to create a modern, well-documented Python implementation of the VOACAP HF propagation prediction engine.

## 🎯 Project Goals

- Maintain numerical accuracy with the original VOACAP/DVOACAP
- Provide clear, well-documented code
- Enable integration with the Python scientific ecosystem
- Make HF propagation modeling accessible to developers and researchers

## 🚀 Getting Started

### Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/skyelaird/dvoacap-python.git
   cd dvoacap-python
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   pip install pytest pytest-cov  # For testing
   ```

4. **Verify installation**:
   ```bash
   python -c "from dvoacap import FourierMaps; print('Success!')"
   pytest tests/ -v
   ```

## 📋 How to Contribute

### Areas Needing Help

We welcome contributions in the following areas:

1. **Phase 5 Completion** (Current Priority)
   - Signal strength calculations
   - Path loss modeling
   - Noise and SNR calculations
   - System performance metrics
   - Full end-to-end integration

2. **Testing**
   - Unit tests for existing modules
   - Integration tests
   - Validation against reference VOACAP data
   - Edge case testing

3. **Documentation**
   - Code comments and docstrings
   - Usage examples
   - Tutorial notebooks
   - API reference documentation

4. **Performance Optimization**
   - Profiling and bottleneck identification
   - NumPy vectorization
   - Caching strategies
   - Memory optimization

5. **Dashboard and Web Interface**
   - Dashboard UI/UX improvements
   - Additional visualization features
   - API endpoint enhancements
   - Mobile app development
   - Multi-user service features (see Dashboard/ISSUE_MULTI_USER_WEB_APP.md)

6. **Features**
   - Data visualization tools
   - Additional antenna models
   - Import/export utilities
   - Integration with external APIs

### Types of Contributions

- **Bug Reports**: Found an issue? Open a GitHub issue with details
- **Bug Fixes**: Submit a pull request with the fix
- **New Features**: Discuss in an issue first, then submit a PR
- **Documentation**: Improvements always welcome
- **Tests**: Help us increase code coverage
- **Examples**: Show others how to use the library

## 🔧 Development Workflow

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/dvoacap-python.git
cd dvoacap-python
git remote add upstream https://github.com/skyelaird/dvoacap-python.git
```

### 2. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes

- Write clear, readable code
- Follow the existing code style
- Add docstrings to new functions/classes
- Include type hints where appropriate
- Update documentation if needed

### 4. Add Tests

```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=dvoacap tests/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "Brief description of changes"
```

**Commit Message Guidelines**:
- Use present tense ("Add feature" not "Added feature")
- Keep first line under 72 characters
- Reference issue numbers when applicable

Examples:
- `Add noise modeling for Phase 5`
- `Fix virtual height calculation bug (#123)`
- `Update documentation for MUF calculator`

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- Clear description of changes
- Reference to related issues
- Test results (if applicable)
- Before/after examples (if applicable)

## 📝 Code Style Guidelines

### Python Style

We generally follow PEP 8 with some flexibility:

```python
# Good: Clear variable names
critical_frequency = 10.5  # MHz
solar_zenith_angle = 0.3   # radians

# Good: Type hints
def compute_muf(frequency: float, layer: LayerInfo) -> float:
    """Compute Maximum Usable Frequency.

    Args:
        frequency: Operating frequency in MHz
        layer: Ionospheric layer parameters

    Returns:
        MUF in MHz
    """
    pass

# Good: Docstrings for classes
class IonosphericProfile:
    """Represents a complete ionospheric electron density profile.

    This class models the electron density as a function of height
    using quasi-parabolic segments for each ionospheric layer.

    Attributes:
        e: E layer parameters
        f1: F1 layer parameters
        f2: F2 layer parameters
    """
    pass
```

### Documentation

- **Modules**: Brief description at top of file
- **Functions**: Docstring with Args, Returns, Raises (if applicable)
- **Classes**: Docstring with overview and attributes
- **Complex algorithms**: Inline comments explaining the approach

### Naming Conventions

- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants
- Descriptive names (avoid single letters except in math formulas)

## 🧪 Testing Guidelines

### Test Structure

```python
# tests/test_your_module.py
import pytest
from dvoacap import YourModule

def test_basic_functionality():
    """Test basic functionality of YourModule."""
    result = YourModule.compute(input_value)
    assert result == expected_value

def test_edge_case():
    """Test edge case handling."""
    with pytest.raises(ValueError):
        YourModule.compute(invalid_input)
```

### Test Coverage

- Aim for >80% code coverage
- Test normal cases
- Test edge cases
- Test error handling
- Test integration points

## 🔬 Validation Against Reference Data

When porting modules from the original VOACAP/DVOACAP:

1. **Generate reference data** from original code
2. **Run your Python implementation** with same inputs
3. **Compare results** and document tolerances
4. **Add validation tests** to test suite

Example:
```python
def test_against_voacap_reference():
    """Validate against VOACAP reference data."""
    # Load reference data from original VOACAP
    ref_data = load_reference_data("test_cases/muf_reference.csv")

    # Run our implementation
    for case in ref_data:
        result = compute_muf(case.inputs)
        assert abs(result - case.expected) < 0.1  # Within 0.1 MHz
```

## 📚 Documentation Standards

### Docstring Format

We use Google-style docstrings:

```python
def compute_critical_frequency(zenith_angle: float, ssn: int) -> float:
    """Compute E layer critical frequency.

    Uses the empirical formula from Davies (1990) to compute foE
    based on solar zenith angle and solar activity level.

    Args:
        zenith_angle: Solar zenith angle in radians (0 = overhead)
        ssn: Smoothed sunspot number (0-200)

    Returns:
        Critical frequency in MHz (typically 1-4 MHz)

    Raises:
        ValueError: If zenith_angle > π/2 (sun below horizon)

    Example:
        >>> compute_critical_frequency(0.3, 100)
        3.15

    References:
        Davies, K. (1990). Ionospheric Radio. Chapter 3.
    """
    pass
```

## 🤝 Code Review Process

All contributions go through code review:

1. **Automated checks**: Tests and linting must pass
2. **Peer review**: At least one maintainer reviews the code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, code is merged

### What Reviewers Look For

- Code correctness and accuracy
- Test coverage
- Documentation quality
- Code style consistency
- Performance considerations
- Integration with existing code

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to Reproduce**: Minimal example demonstrating the bug
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Environment**: Python version, OS, package versions
6. **Error Messages**: Full error traceback if applicable

Example:
```markdown
### Bug Description
MUF calculator returns NaN for high latitude paths

### Steps to Reproduce
```python
from dvoacap import MufCalculator, PathGeometry
path = PathGeometry()
path.set_tx_rx_degrees(80, 0, 85, 10)  # Arctic path
muf = MufCalculator(path, ...)
result = muf.compute_circuit_muf()  # Returns NaN
```

### Expected: Valid MUF value (e.g., 15.2 MHz)
### Actual: NaN

### Environment
- Python 3.9.7
- dvoacap-python 0.4.0
- Linux Ubuntu 20.04
```

## 💬 Communication

- **GitHub Issues**: Bug reports, feature requests, questions
- **Pull Requests**: Code contributions and discussions
- **Discussions**: General questions and ideas

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License, consistent with the project's license.

The original DVOACAP code is licensed under Mozilla Public License Version 1.1. Our Python implementation is a clean-room reimplementation released under MIT License.

## 🙏 Acknowledgments

When contributing, please:

- Acknowledge original VOACAP/DVOACAP authors in relevant comments
- Credit external libraries and algorithms used
- Reference scientific papers for complex algorithms

## 📧 Questions?

If you have questions about contributing:

- Open a GitHub issue with the "question" label
- Check existing issues and documentation first
- Be patient - maintainers are volunteers

## 🎓 Resources for New Contributors

### Understanding VOACAP

- [VOACAP Documentation](https://www.voacap.com/)
- [ITU-R P.533 HF Propagation](https://www.itu.int/rec/R-REC-P.533/)
- Davies, K. (1990). "Ionospheric Radio" - Classic reference book

### Understanding the Ionosphere

- [NOAA Space Weather Prediction Center](https://www.swpc.noaa.gov/)
- [IPS Radio and Space Services](https://www.sws.bom.gov.au/)

### Python Scientific Computing

- [NumPy Documentation](https://numpy.org/doc/)
- [SciPy Documentation](https://docs.scipy.org/)
- [pytest Documentation](https://docs.pytest.org/)

---

Thank you for contributing to DVOACAP-Python! Your efforts help make HF propagation modeling accessible to everyone. 📻 73!
