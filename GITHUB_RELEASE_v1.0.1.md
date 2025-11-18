# 🚀 DVOACAP-Python v1.0.1 - Performance Release

**2.3x faster** predictions through algorithmic optimizations while maintaining 86.6% validation accuracy!

## ⚡ Performance Improvements

| Operation | v1.0.0 | v1.0.1 | Speedup |
|-----------|--------|--------|---------|
| Single prediction | 0.008s | 0.004s | **2.0x** |
| Multi-frequency (9) | 0.111s | 0.048s | **2.3x** |
| 24-hour scan | 0.282s | 0.118s | **2.4x** |
| Area coverage (100) | 0.820s | 0.350s | **2.3x** |

## 🔧 Key Optimizations

- **Binary search** for height-density interpolation (O(n) → O(log n))
- **Vectorized Gaussian integration** using NumPy (eliminated 40-iteration loop)
- **Vectorized oblique frequency computation** (eliminated 1,200 nested iterations)
- **Optimized Fourier series** with NumPy dot products

## 📦 Installation

```bash
# Core library
pip install dvoacap

# With dashboard
pip install dvoacap[dashboard]

# Full installation
pip install dvoacap[all]
```

## 📊 What's Included

- ✅ **86.6% validation accuracy** maintained
- ✅ All 5 implementation phases complete
- ✅ Production-ready HF propagation predictions
- ✅ Interactive web dashboard
- ✅ Real-time space weather integration
- ✅ Python 3.11+ support

## 🔗 Resources

- 📖 [Full Release Notes](RELEASE_NOTES_v1.0.1.md)
- 📖 [Changelog](CHANGELOG.md)
- 🌐 [Documentation](https://skyelaird.github.io/dvoacap-python/)
- 📦 [PyPI Package](https://pypi.org/project/dvoacap/)

## 🙏 Credits

Original DVOACAP by Alex Shovkoplyas (VE3NEA)
Original VOACAP by Voice of America / ITS

---

**73!** 📻
