# GN55-IN25 Line Comparison Analysis
## Propagation Differences: North vs South of 45°N Latitude

**Analysis Date:** 2025-11-15
**TX Location:** VE1ATM - FN74ui (44.374°N, 64.300°W)
**Conditions:** SSN=100 (mid-cycle), Month=November, TX Power=100W

---

## Executive Summary

This analysis compares HF propagation characteristics between regions **north** and **south** of the 45°N latitude line (defined by the Maidenhead grid line GN55-IN25). The line runs east-west from approximately 50°W to 14°W longitude.

### Geographic Context

**The Line:** GN55-IN25 spans latitude 45°N-46°N across the North Atlantic/European sector
- **GN55:** 45-46°N, 50-48°W (Northwestern Atlantic)
- **IN25:** 45-46°N, 16-14°W (Eastern Atlantic, west of Iberia)

**TX Station (VE1ATM):** Located at 44.37°N — just **SOUTH** of the 45°N line

---

## Key Findings

### Overall Statistics

| Region | Mean Reliability | Mean SNR | Key Characteristic |
|--------|-----------------|----------|-------------------|
| **North of 45°N** | 57.5% | +3.4 dB | Better on 17m/15m |
| **South of 45°N** | 58.6% | +5.1 dB | Better on 12m/10m |
| **Difference (S-N)** | **+1.1%** | **+1.7 dB** | Slight southern advantage |

### Critical Band-by-Band Differences

The most significant differences emerge when examining individual HF bands:

#### Bands Favoring SOUTH of 45°N (Lower Latitudes)

| Band | Reliability Advantage | SNR Advantage | Why This Matters |
|------|---------------------|---------------|------------------|
| **12m (24 MHz)** | **+26.2%** | **+17.9 dB** | Dramatic difference — Southern regions vastly superior |
| **10m (28 MHz)** | **+22.1%** | **+35.9 dB** | Highest band shows strongest latitude effect |
| **40m (7 MHz)** | +6.2% | -8.4 dB | More reliable south, but weaker signals |
| **20m (14 MHz)** | -20.4% | +5.2 dB | Mixed results (less reliable but better SNR when open) |

#### Bands Favoring NORTH of 45°N (Higher Latitudes)

| Band | Reliability Advantage | SNR Advantage | Key Observation |
|------|---------------------|---------------|-----------------|
| **17m (18 MHz)** | +0.7% | +17.7 dB | Stronger signals to northern regions |
| **15m (21 MHz)** | +5.5% | +5.1 dB | Better reliability to north |

#### Neutral Bands

| Band | Note |
|------|------|
| **30m (10 MHz)** | Nearly identical performance north vs south (-2.3% reliability, -0.4 dB SNR) |

---

## Detailed Analysis

### 1. High-Band Propagation (12m/10m)

**Southern regions show dramatic advantages on higher bands:**

- **12m:** 76.1% reliability (south) vs 49.9% (north) — **26% improvement**
- **10m:** 38.4% reliability (south) vs 16.3% (north) — **22% improvement**

**Physical Explanation:**
- Lower latitudes receive higher solar zenith angles (sun more overhead)
- Higher F2-layer critical frequencies (foF2) at lower latitudes
- More consistent ionization levels year-round
- Less impact from auroral/geomagnetic disturbances

**Practical Impact:**
- Contacts to Southern Europe (Spain, Italy, Greece) significantly better on 12m/10m during solar maximum
- Northern Europe (Scandinavia, UK) more challenging on high bands
- Station at 44.37°N is well-positioned for southern high-band paths

### 2. Mid-Band Behavior (17m/15m/20m)

**Complex patterns emerge:**

- **17m shows NORTHERN advantage:** +17.7 dB SNR to northern grids
- **15m slightly favors NORTH:** +5.5% reliability, +5.1 dB SNR
- **20m mixed results:** Lower reliability south (-20.4%) but better SNR when open (+5.2 dB)

**Physical Explanation:**
- Mid-bands transition zone between low-band and high-band physics
- Similar-latitude propagation (VE1ATM at 44°N to regions at 45-60°N) benefits from matched ionospheric conditions
- Grayline enhancement effects stronger at higher latitudes on 17m/15m

**Practical Impact:**
- 17m/15m are "universal" bands with good performance both directions
- 20m behavior depends on time of day and season
- Both regions workable, but slight northern edge on these bands

### 3. Low-Band Characteristics (40m/30m)

**Surprisingly good performance to southern regions:**

- **40m:** +6.2% reliability to south (though -8.4 dB SNR)
- **30m:** Nearly identical (neutral)

**Physical Explanation:**
- Lower bands less dependent on F2-layer MUF
- Atmospheric noise and ground conductivity become dominant factors
- Northern regions experience more D-layer absorption from auroral effects
- Southern paths benefit from reduced geomagnetic interference

**Practical Impact:**
- 40m reliable to both regions, but northern signals slightly stronger
- 30m is the "equalizer" band — works equally well north and south
- Night-time propagation critical for both directions

---

## Sample Grid Results

### Grids NORTH of 45°N

| Grid | Location | Best Band (00:00 UTC) | Best Band (12:00 UTC) |
|------|----------|---------------------|---------------------|
| IO55 | British Isles/North Sea | 40m (86%, 27 dB) | 17m (91%, 30 dB) |
| JP50 | Southern Scandinavia | 40m (68%, 19 dB) | 15m (77%, 26 dB) |
| IO72 | Ireland/UK | 40m (83%, 26 dB) | 15m (90%, 31 dB) |
| JN18 | Northern France | 40m (82%, 24 dB) | 15m (90%, 30 dB) |
| JO20 | Belgium/Netherlands | 40m (82%, 24 dB) | 15m (90%, 30 dB) |
| JO60 | Southern Finland | 40m (68%, 18 dB) | 15m (76%, 25 dB) |

### Grids SOUTH of 45°N

| Grid | Location | Best Band (00:00 UTC) | Best Band (12:00 UTC) |
|------|----------|---------------------|---------------------|
| IN62 | Northern Spain/Portugal | 40m (91%, 27 dB) | 15m (94%, 33 dB) |
| JN70 | Southern Italy | 40m (77%, 20 dB) | 15m (79%, 22 dB) |
| KM18 | Greece | 30m (72%, 22 dB) | 15m (77%, 21 dB) |
| IM76 | Southern Spain | 40m (88%, 25 dB) | **12m (95%, 32 dB)** |
| IN80 | Central Spain | 40m (88%, 25 dB) | 15m (93%, 31 dB) |
| KN23 | Southern France/Riviera | 40m (82%, 22 dB) | 15m (91%, 29 dB) |

**Notable:**
- Southern Spain (IM76) achieves **95% reliability and 32 dB SNR on 12m** at midday
- Northern grids show strong 17m preference during evening hours
- Southern grids maintain higher reliability percentages across most times

---

## Geophysical Factors

### North of 45°N (Higher Latitudes)

**Advantages:**
- ✅ Stronger grayline enhancement on mid-bands
- ✅ Better low-band (40m/30m) signal strength
- ✅ Shared similar-latitude ionospheric conditions with TX station

**Challenges:**
- ❌ More geomagnetic storm susceptibility (closer to auroral oval at ~65-70°N)
- ❌ Higher D-layer absorption during disturbed conditions
- ❌ Lower F2-layer critical frequencies (lower MUF)
- ❌ More variable day-to-day conditions
- ❌ Seasonal extremes (very short winter days, very long summer days)

### South of 45°N (Lower Latitudes)

**Advantages:**
- ✅ Higher F2-layer critical frequencies (higher MUF)
- ✅ More stable ionospheric conditions
- ✅ Excellent high-band (12m/10m) performance
- ✅ More consistent year-round propagation
- ✅ Less auroral interference

**Challenges:**
- ❌ Slightly weaker mid-band signals (17m/15m)
- ❌ Cross-latitude propagation from similar-latitude TX
- ❌ Lower reliability on 20m during some time periods

---

## Practical Operating Recommendations

### For VE1ATM (44.37°N) Working Europe

#### Target Northern Europe (UK, Scandinavia, Northern France, BeNeLux)

**Best Bands by Time:**
- **Night (00:00-06:00 UTC):** 40m primary, 30m secondary
- **Day (12:00-18:00 UTC):** 17m/15m primary, 20m secondary
- **Transitions (sunrise/sunset):** 17m (grayline enhancement)

**Band Selection:**
- ✅ **Excellent:** 17m (83.9% avg reliability, 27.7 dB SNR)
- ✅ **Excellent:** 15m (81.4% avg reliability, 27.7 dB SNR)
- ✅ **Good:** 40m (48.3% reliability but strong signals)
- ⚠️ **Challenging:** 12m/10m (lower reliability, especially to Scandinavia)

#### Target Southern Europe (Spain, Italy, Greece, Southern France)

**Best Bands by Time:**
- **Night (00:00-06:00 UTC):** 40m primary, 30m secondary
- **Day (12:00-18:00 UTC):** 15m/12m primary, 17m secondary
- **High solar activity:** 10m becomes viable

**Band Selection:**
- ✅ **Excellent:** 12m (76.1% avg reliability, 24.4 dB SNR)
- ✅ **Excellent:** 15m (75.9% avg reliability, 22.6 dB SNR)
- ✅ **Good:** 40m (54.5% reliability)
- ✅ **Solar Max:** 10m (38.4% reliability — far better than to northern regions)

#### The "Universal" Bands

**30m (10.125 MHz):**
- Nearly identical performance to both regions
- -2.3% reliability difference (negligible)
- Excellent "fallback" band when conditions uncertain
- Works day or night with consistent performance

**17m (18.118 MHz):**
- Good to both regions (83% avg reliability)
- Slightly better SNR to north (+17.7 dB)
- Strong all-around performer for Europe

---

## Time-of-Day Patterns

### Midnight (00:00 UTC)

**North:** 40m dominant (68-86% reliability)
**South:** 40m dominant (72-91% reliability)
**Winner:** South slightly better on 40m reliability

### Dawn (06:00 UTC)

**North:** 40m still strong (67-82%)
**South:** 40m best (55-80%)
**Winner:** North maintains stronger 40m performance

### Noon (12:00 UTC)

**North:** 15m/17m excellent (76-91%, 25-30 dB)
**South:** 15m/12m excellent (77-95%, 22-32 dB)
**Winner:** South shows higher reliability and introduces 12m viability

### Evening (18:00 UTC)

**North:** 17m peak (73-88%, 23-31 dB)
**South:** 17m/20m strong (68-93%, 19-33 dB)
**Winner:** South maintains better peak performance

---

## Statistical Methodology

### Test Configuration

- **TX Location:** VE1ATM at FN74ui (44.374°N, 64.300°W)
- **Test Grids:** 6 grids north of 45°N, 6 grids south of 45°N
- **Test Times:** 00:00, 06:00, 12:00, 18:00 UTC (4 time points)
- **Frequencies:** 7 HF amateur bands (40m, 30m, 20m, 17m, 15m, 12m, 10m)
- **Total Predictions:** 168 individual propagation predictions per region
- **Conditions:** November, SSN=100 (mid solar cycle), 100W TX power
- **Min Takeoff Angle:** 3°

### Grids Tested

**North of 45°N:**
- IO55 (British Isles/North Sea, 55.5°N)
- JP50 (Southern Scandinavia, 60.5°N)
- IO72 (Ireland/UK, 52.5°N)
- JN18 (Northern France, 48.5°N)
- JO20 (Belgium/Netherlands, 50.5°N)
- JO60 (Southern Finland, 60.5°N)

**South of 45°N:**
- IN62 (Northern Spain/Portugal, 42.5°N)
- JN70 (Southern Italy, 40.5°N)
- KM18 (Greece, 38.5°N)
- IM76 (Southern Spain, 36.5°N)
- IN80 (Central Spain, 40.5°N)
- KN23 (Southern France/Riviera, 43.5°N)

---

## Conclusions

### Major Findings

1. **High-Band Latitude Effect is Dramatic**
   - 12m shows **+26% reliability** to southern regions
   - 10m shows **+36 dB SNR improvement** to southern regions
   - This is the most significant propagation difference

2. **Mid-Bands Favor Northern Regions**
   - 17m/15m show +5-18 dB SNR advantage to north
   - Better similar-latitude ionospheric coupling

3. **Low-Bands Are Relatively Neutral**
   - 40m works well to both regions (slight southern reliability edge)
   - 30m is nearly identical performance

4. **Overall Advantage: Slight Southern Edge**
   - +1.1% overall reliability
   - +1.7 dB overall SNR
   - But band-by-band differences are more meaningful than averages

### Operational Strategy

**The 45°N latitude line represents a real propagation boundary:**

- **For high-band DX (12m/10m):** Work southern grids preferentially
- **For mid-band DX (17m/15m):** Northern regions perform well
- **For low-band DX (40m/30m):** Both regions viable, pick based on target
- **For all-around reliability:** 17m and 30m are "universal" bands

### Station Planning Insights

For a station at VE1ATM's latitude (44.37°N):

1. **You're positioned in the "crossover zone"** — just south of the line
2. **Northern Europe:** Excellent on 17m/15m/40m
3. **Southern Europe:** Excellent on 12m/10m during solar max
4. **Mediterranean:** Outstanding high-band target during solar cycle peak
5. **Scandinavia:** Challenging on high bands, use 17m/15m

---

## Data Files

**Full Results:** `gn55_in25_comparison_results.json`
**Analysis Script:** `analysis_gn55_in25_comparison.py`
**Generated:** 2025-11-15 13:45 UTC

---

## Appendix: Geographic Reference

### The GN55-IN25 Line

```
         50°W                    16°W
          |                       |
  46°N ---|------ GN55 ---- IN25 -|--- 46°N
          |                       |
  45°N ---|---------------------|--- 45°N (DIVIDING LINE)
          |                       |
```

**Line characteristics:**
- **Latitude:** 45-46°N
- **Longitude span:** 50°W to 14°W (~2,675 km)
- **Location:** North Atlantic / European Atlantic seaboard
- **Significance:** Separates higher-latitude northern Europe from lower-latitude Mediterranean/Southern Europe

**VE1ATM position:** 44.37°N — 0.63° south of the line (approximately 70 km)

### Why This Line Matters

The 45°N parallel is a meaningful propagation boundary:

1. **Geomagnetic latitude:** Approximately 52°N geomagnetic (northern hemisphere mid-latitudes)
2. **Auroral influence:** Transition zone from low auroral influence (south) to moderate influence (north)
3. **F2-layer behavior:** Critical frequencies begin to decrease significantly north of this line
4. **Solar zenith angles:** Seasonal day/night variations become more extreme north of 45°N
5. **Sporadic-E:** Both regions experience summer sporadic-E, but northern latitudes see more pronounced effects

---

**Report Prepared By:** DVOACAP-Python Prediction Engine
**Analysis Version:** 1.0
**Contact:** VE1ATM
