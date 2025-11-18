# Performance Tips

Optimization strategies for speeding up DVOACAP-Python predictions.

## 🚀 v1.0.1 Performance Improvements

**Released:** November 2025
**Speedup:** 2.3x faster than v1.0.0

DVOACAP-Python v1.0.1 delivers significant performance improvements through algorithmic optimizations and NumPy vectorization:

### Benchmark Results

| Operation | v1.0.0 | v1.0.1 | Speedup |
|-----------|--------|--------|---------|
| Single prediction | 0.008s | 0.004s | **2.0x** |
| Multi-frequency (9 predictions) | 0.111s | 0.048s | **2.3x** |
| 24-hour scan | 0.282s | 0.118s | **2.4x** |
| Area coverage (100 predictions) | 0.82s | 0.35s | **2.3x** |
| Function calls | 100% | 29-32% | **68-71% reduction** |

### Key Optimizations

1. **Binary Search for Height-to-Density** - O(n) → O(log n) complexity
2. **Vectorized Gaussian Integration** - Eliminated 40-iteration loop using NumPy
3. **Vectorized Oblique Frequency** - Eliminated 1,200 nested iterations
4. **Optimized Fourier Series** - Replaced loops with NumPy dot products

See [CHANGELOG.md](https://github.com/skyelaird/dvoacap-python/blob/main/CHANGELOG.md) for full v1.0.1 release notes.

---

## Table of Contents

- [v1.0.1 Performance Improvements](#-v101-performance-improvements)
- [Understanding Performance](#understanding-performance)
- [Quick Wins](#quick-wins)
- [Configuration Optimization](#configuration-optimization)
- [Code-Level Optimization](#code-level-optimization)
- [Caching Strategies](#caching-strategies)
- [Parallel Processing](#parallel-processing)
- [Profiling](#profiling)
- [Future Improvements](#future-improvements)

---

## Understanding Performance

### Where Time Is Spent

**Typical prediction breakdown:**

| Phase | Time % | Operation |
|-------|--------|-----------|
| Phase 3: Ionospheric Profiles | ~35% | CCIR coefficient processing, electron density profiles |
| Phase 4: Raytracing | ~40% | Iterative path finding, MUF calculations |
| Phase 5: Signal Predictions | ~20% | Path loss, SNR, reliability calculations |
| Phase 1-2: Geometry/Solar | ~5% | Path calculations, solar zenith angles |

**Bottleneck:** Raytracing (Phase 4) is the most computationally intensive.

---

### Timing Benchmarks

**Single prediction (1 frequency, 1 path):**
- Fast system (modern CPU): ~4 ms (v1.0.1 optimized - 2.3x faster than v1.0.0)
- Average system: ~10-20 ms
- Slow system (Raspberry Pi): ~50-100 ms

**Full dashboard generation (10 regions × 7 bands × 12 hours):**
- Fast system: ~20-30 seconds (v1.0.1 optimized - 2.3x faster than v1.0.0)
- Average system: ~30-45 seconds
- Slow system: ~1-2 minutes

**Note:** See the [v1.0.1 Performance Improvements](#-v101-performance-improvements) section above for detailed benchmark data and optimization details.

---

## Quick Wins

### 1. Reuse PredictionEngine Instances

**❌ Slow (creates new engine every time):**
```python
for region in regions:
    engine = PredictionEngine()  # DON'T DO THIS
    engine.predict(...)
```

**✅ Fast (reuse engine):**
```python
engine = PredictionEngine()  # Create once
for region in regions:
    engine.predict(...)  # Reuse for all predictions
```

**Speedup:** ~20-30% faster (avoids re-loading CCIR maps)

---

### 2. Batch Frequencies Together

**❌ Slow (separate predictions):**
```python
for freq in [7.0, 14.0, 21.0]:
    engine.predict(rx_location, utc_time, frequencies=[freq])
```

**✅ Fast (batch frequencies):**
```python
engine.predict(rx_location, utc_time, frequencies=[7.0, 14.0, 21.0])
```

**Speedup:** ~3x faster (path geometry computed once)

---

### 3. Reduce Number of Predictions

**Dashboard optimization:**
```python
# Instead of 10 regions
TARGET_REGIONS = {
    'EU': ...,
    'JA': ...,
    'VK': ...,
    # Remove regions you don't work
}

# Instead of 7 bands
BANDS = {
    '40m': 7.150,
    '20m': 14.150,
    '15m': 21.200,
    # Remove bands you don't use
}

# Instead of 12 time points, use 8
utc_hours = [0, 3, 6, 9, 12, 15, 18, 21]  # Every 3 hours instead of 2
```

**Speedup:** Proportional to reduction (50% fewer predictions = 50% faster)

---

### 4. Use Reasonable Solar Conditions

**Avoid extreme values:**
```python
# ✅ Good - typical values
engine.params.ssn = 100.0  # Moderate solar cycle

# ❌ Slow - extreme values take longer to converge
engine.params.ssn = 300.0  # Very high (edge case)
```

---

## Configuration Optimization

### Reduce Path Resolution

**For dashboard/batch processing:**
```python
# Default: High accuracy, slower
engine.params.min_angle = np.deg2rad(3.0)

# Faster: Slightly lower accuracy
engine.params.min_angle = np.deg2rad(5.0)
```

**Speedup:** ~10-15% faster
**Impact:** Minimal difference in results for typical amateur radio use

---

### Adjust Raytracing Parameters

**Tune iteration limits (advanced):**
```python
# In muf_calculator.py (internal settings)
MAX_ITERATIONS = 50  # Default: 100 (faster but less precise)
CONVERGENCE_TOLERANCE = 1e-3  # Default: 1e-4 (looser tolerance)
```

**Speedup:** ~15-20% faster
**Impact:** May affect edge case accuracy

---

### Skip Unnecessary Calculations

**Disable features you don't need:**
```python
# If you only need MUF (not full signal predictions)
# Use muf_calculator directly instead of full PredictionEngine

from dvoacap.muf_calculator import MufCalculator

calc = MufCalculator()
# ... configure and run MUF calculation only
# Much faster than full prediction
```

---

## Code-Level Optimization

### Use NumPy Vectorization

**❌ Slow (Python loops):**
```python
results = []
for i in range(len(frequencies)):
    result = calculate_loss(frequencies[i])
    results.append(result)
```

**✅ Fast (NumPy vectorization):**
```python
import numpy as np
results = calculate_loss(np.array(frequencies))  # Vectorized
```

**Speedup:** 10-100x for large arrays

---

### Avoid Repeated Calculations

**Cache expensive operations:**
```python
class OptimizedEngine:
    def __init__(self):
        self._solar_cache = {}

    def get_solar_params(self, month, ssn, utc_time):
        """Cache solar calculations"""
        cache_key = (month, ssn, utc_time)

        if cache_key not in self._solar_cache:
            self._solar_cache[cache_key] = compute_solar_params(month, ssn, utc_time)

        return self._solar_cache[cache_key]
```

---

### Minimize Object Creation

**❌ Slow:**
```python
for i in range(1000):
    point = GeoPoint.from_degrees(lat, lon)  # Creates new object each time
    # ...
```

**✅ Fast:**
```python
point = GeoPoint.from_degrees(lat, lon)  # Create once
for i in range(1000):
    # Reuse point
    # ...
```

---

## Caching Strategies

### Result Caching

**Cache predictions for identical inputs:**

```python
import hashlib
import json
import pickle
from pathlib import Path

class CachedPredictionEngine:
    """Prediction engine with result caching"""

    def __init__(self, cache_dir='cache'):
        self.engine = PredictionEngine()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _cache_key(self, rx_location, frequencies, month, ssn, utc_time):
        """Generate cache key from parameters"""
        rx_lat, rx_lon = rx_location.to_degrees()
        params = {
            'rx_lat': round(rx_lat, 4),
            'rx_lon': round(rx_lon, 4),
            'frequencies': frequencies,
            'month': month,
            'ssn': round(ssn, 1),
            'utc_time': round(utc_time, 2)
        }
        key_str = json.dumps(params, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    def predict(self, rx_location, frequencies, month, ssn, utc_time):
        """Predict with caching"""
        cache_key = self._cache_key(rx_location, frequencies, month, ssn, utc_time)
        cache_file = self.cache_dir / f"{cache_key}.pkl"

        # Check cache
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                return pickle.load(f)

        # Run prediction
        self.engine.params.month = month
        self.engine.params.ssn = ssn

        self.engine.predict(
            rx_location=rx_location,
            utc_time=utc_time / 24.0,
            frequencies=frequencies
        )

        # Cache results
        result = {
            'muf': self.engine.muf_calculator.muf,
            'predictions': self.engine.predictions
        }

        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)

        return result

# Usage
engine = CachedPredictionEngine(cache_dir='prediction_cache')
result = engine.predict(...)  # First call: runs prediction
result = engine.predict(...)  # Second call: instant (from cache)
```

**Speedup:** ~∞ for cached results (instant retrieval)

---

### CCIR Map Caching

**CCIR maps are automatically cached** after first load. Don't reload unnecessarily:

```python
# ✅ Good - maps loaded once
maps = FourierMaps()
for month in range(1, 13):
    maps.set_conditions(month=month, ssn=100, utc_fraction=0.5)
    # Maps are reused

# ❌ Bad - reloads maps each time
for month in range(1, 13):
    maps = FourierMaps()  # DON'T DO THIS
    maps.set_conditions(month=month, ssn=100, utc_fraction=0.5)
```

---

## Parallel Processing

### Multi-Processing for Multiple Paths

**Process regions in parallel:**

```python
from multiprocessing import Pool
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint

def predict_region(args):
    """Worker function for parallel processing"""
    region_name, region_location, frequencies, month, ssn, utc_time = args

    # Each process gets its own engine
    engine = PredictionEngine()
    engine.params.month = month
    engine.params.ssn = ssn
    engine.params.tx_location = GeoPoint.from_degrees(44.374, -64.300)

    engine.predict(
        rx_location=region_location,
        utc_time=utc_time / 24.0,
        frequencies=frequencies
    )

    return {
        'region': region_name,
        'muf': engine.muf_calculator.muf,
        'predictions': engine.predictions
    }

# Parallel execution
if __name__ == '__main__':
    regions = {
        'EU': GeoPoint.from_degrees(50.0, 10.0),
        'JA': GeoPoint.from_degrees(36.0, 138.0),
        'VK': GeoPoint.from_degrees(-33.87, 151.21),
        # ... more regions
    }

    tasks = [
        (name, location, [7.0, 14.0, 21.0], 6, 100, 12)
        for name, location in regions.items()
    ]

    # Use 4 processes
    with Pool(processes=4) as pool:
        results = pool.map(predict_region, tasks)

    for result in results:
        print(f"{result['region']}: MUF {result['muf']:.2f} MHz")
```

**Speedup:** ~4x with 4 cores (linear scaling up to number of cores)

**Note:** Use `if __name__ == '__main__':` guard on Windows!

---

### Async I/O for Dashboard

**Use asyncio for concurrent operations:**

```python
import asyncio
from dvoacap import PredictionEngine

async def async_predict(region, location, frequencies):
    """Async wrapper for prediction"""
    loop = asyncio.get_event_loop()

    # Run prediction in thread pool
    result = await loop.run_in_executor(
        None,
        run_prediction,
        region, location, frequencies
    )

    return result

def run_prediction(region, location, frequencies):
    """Synchronous prediction function"""
    engine = PredictionEngine()
    # ... configure and run prediction
    return result

# Run predictions concurrently
async def main():
    tasks = [
        async_predict('EU', eu_location, [14.0]),
        async_predict('JA', ja_location, [14.0]),
        async_predict('VK', vk_location, [14.0]),
    ]

    results = await asyncio.gather(*tasks)
    return results

# Execute
results = asyncio.run(main())
```

---

## Profiling

### Identify Bottlenecks

**Use cProfile to find slow code:**

```bash
python3 -m cProfile -o profile.stats generate_predictions.py
```

**Analyze results:**
```python
import pstats

stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 slowest functions
```

---

### Line-by-Line Profiling

**Use line_profiler for detailed analysis:**

```bash
# Install
pip install line_profiler

# Add @profile decorator to function
@profile
def my_slow_function():
    # ...

# Run profiler
kernprof -l -v my_script.py
```

---

### Memory Profiling

**Check memory usage:**

```bash
pip install memory_profiler

# Run
python3 -m memory_profiler generate_predictions.py
```

---

## Future Improvements

### Planned Optimizations

**In Development:**
1. **Numba JIT compilation** - Compile hot paths to native code
2. **Cython modules** - Rewrite critical modules in Cython
3. **Lookup tables** - Pre-computed values for common scenarios
4. **Parallel raytracing** - Parallel ray finding for multiple frequencies

**Expected speedup:** 3-10x for full implementation

---

### Experimental: Numba Acceleration

**Add Numba JIT to hot functions:**

```python
from numba import jit
import numpy as np

@jit(nopython=True)
def fast_path_loss_calculation(frequency, distance, layer_params):
    """JIT-compiled path loss calculation"""
    # ... computation
    return loss

# First call: compilation overhead (~1 second)
result = fast_path_loss_calculation(14.0, 5000, params)

# Subsequent calls: very fast (10-100x speedup)
result = fast_path_loss_calculation(21.0, 5000, params)
```

**Status:** Experimental (not yet integrated into main codebase)

---

## Benchmark Comparison

### Optimization Impact Summary

| Optimization | Speedup | Effort | Notes |
|--------------|---------|--------|-------|
| Reuse engine instances | 1.3x | Easy | Always do this |
| Batch frequencies | 3x | Easy | Always do this |
| Reduce predictions | Variable | Easy | Trade-off with coverage |
| Caching results | ∞ | Medium | Best for repeated queries |
| Multi-processing | 4x | Medium | For batch jobs |
| Numba/Cython | 10x | Hard | Future work |

---

## Practical Examples

### Optimized Dashboard Generation

**Before (slow):**
```python
for region in regions:
    for band in bands:
        for hour in range(24):
            engine = PredictionEngine()  # ❌ Recreates each time
            engine.predict(region, [band], hour)
```

**After (fast):**
```python
engine = PredictionEngine()  # ✅ Create once

# Batch by region
for region in regions:
    # Batch frequencies
    all_bands = list(bands.values())

    # Batch time points
    for hour in [0, 3, 6, 9, 12, 15, 18, 21]:  # Every 3 hours
        engine.predict(region, all_bands, hour)
```

**Speedup:** ~10-15x faster

---

### Optimized Multi-Region Prediction

```python
from concurrent.futures import ProcessPoolExecutor
from functools import partial

def optimized_multi_region_predict(regions, bands, hours, month, ssn):
    """Optimized multi-region prediction"""

    def predict_one(region_name, region_location):
        """Predict for one region (runs in separate process)"""
        engine = PredictionEngine()
        engine.params.month = month
        engine.params.ssn = ssn
        engine.params.tx_location = tx_location

        results = []
        for hour in hours:
            engine.predict(
                rx_location=region_location,
                utc_time=hour / 24.0,
                frequencies=bands
            )
            results.append({
                'hour': hour,
                'muf': engine.muf_calculator.muf,
                'predictions': engine.predictions
            })

        return region_name, results

    # Run in parallel
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(predict_one, name, location): name
            for name, location in regions.items()
        }

        all_results = {}
        for future in futures:
            region_name, results = future.result()
            all_results[region_name] = results

    return all_results

# Usage
results = optimized_multi_region_predict(
    regions=TARGET_REGIONS,
    bands=[7.0, 14.0, 21.0],
    hours=[0, 6, 12, 18],
    month=6,
    ssn=100
)
```

**Speedup:** ~4x with 4 cores + batching optimizations

---

## Monitoring Performance

### Add Timing to Your Code

```python
import time
from functools import wraps

def timing_decorator(func):
    """Decorator to measure function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} took {elapsed:.2f} seconds")
        return result
    return wrapper

@timing_decorator
def generate_predictions():
    # ... prediction code
    pass

# Output: generate_predictions took 45.23 seconds
```

---

## Next Steps

- **[Integration Guide](Integration-Guide)** - Build optimized applications
- **[Dashboard Guide](Dashboard-Guide)** - Optimize dashboard performance
- **[Known Issues](Known-Issues)** - Performance limitations
- **[Development Setup](Development-Setup)** - Set up profiling tools

---

**Tip:** Start with the quick wins (reuse engines, batch frequencies) for immediate 3-5x speedup with minimal effort!
