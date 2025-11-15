/**
 * Propagation Charts Module - DVOACAP Dashboard v1.0
 *
 * Implements interactive REL/SDBW/SNR/MUFday charts for band-by-band analysis
 * Based on VOACAP Online prop charts feature (P0 critical)
 *
 * Features:
 * - 24-hour timeline with hourly granularity
 * - Multiple metrics on same chart (REL, SDBW, SNR, MUFday)
 * - Signal uncertainty zones (SDBW10/SDBW90)
 * - Interactive hover tooltips
 * - Band and region selection
 * - PNG export capability
 */

// Convert signal power (dBW) to S-meter reading
function dbwToSMeter(dbw) {
    // S9 = -73 dBm = -103 dBW (approximately)
    // Each S-unit is 6 dB
    const s9_dbw = -103;
    const db_over_s9 = dbw - s9_dbw;

    if (db_over_s9 >= 0) {
        // S9+ readings
        const plus_db = db_over_s9;
        return `S9+${plus_db.toFixed(0)}dB`;
    } else {
        // S1-S9 readings
        const s_units = Math.max(1, Math.min(9, 9 + (db_over_s9 / 6)));
        return `S${Math.round(s_units)}`;
    }
}

// Generate propagation chart for a specific band and region
function generatePropChart(bandName, regionCode, propData) {
    if (!propData || !propData.predictions) {
        console.error('No propagation data available');
        return;
    }

    // Filter predictions for this region
    const regionPredictions = propData.predictions.filter(p => p.region === regionCode);

    if (regionPredictions.length === 0) {
        console.error(`No predictions found for region ${regionCode}`);
        return;
    }

    // Sort by UTC hour
    regionPredictions.sort((a, b) => a.utc_hour - b.utc_hour);

    // Extract data arrays
    const hours = regionPredictions.map(p => p.utc_hour);
    const reliability = regionPredictions.map(p => p.bands[bandName]?.reliability || 0);
    const snr = regionPredictions.map(p => p.bands[bandName]?.snr || -999);
    const mufDay = regionPredictions.map(p => p.bands[bandName]?.muf_day || 0);
    const signalDbw = regionPredictions.map(p => p.bands[bandName]?.signal_dbw || -999);
    const signal10 = regionPredictions.map(p => p.bands[bandName]?.signal_10 || -999);
    const signal90 = regionPredictions.map(p => p.bands[bandName]?.signal_90 || -999);

    // Create S-meter labels for signal power axis
    const sMeterLabels = signalDbw.map(dbw => dbwToSMeter(dbw));

    // Reliability trace (primary y-axis, left)
    const reliabilityTrace = {
        x: hours,
        y: reliability,
        name: 'Reliability',
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#4a90e2',
            width: 3
        },
        marker: {
            size: 6
        },
        yaxis: 'y1',
        hovertemplate: '<b>%{x}:00 UTC</b><br>' +
                      'Reliability: %{y:.1f}%<br>' +
                      '<extra></extra>'
    };

    // SNR trace (secondary y-axis, right)
    const snrTrace = {
        x: hours,
        y: snr,
        name: 'SNR',
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#f59e0b',
            width: 3
        },
        marker: {
            size: 6
        },
        yaxis: 'y2',
        hovertemplate: '<b>%{x}:00 UTC</b><br>' +
                      'SNR: %{y:.1f} dB<br>' +
                      '<extra></extra>'
    };

    // MUFday trace (primary y-axis, left) - shares with reliability
    const mufDayTrace = {
        x: hours,
        y: mufDay,
        name: 'MUFday',
        type: 'scatter',
        mode: 'lines',
        line: {
            color: '#ef4444',
            width: 2,
            dash: 'dot'
        },
        yaxis: 'y1',
        hovertemplate: '<b>%{x}:00 UTC</b><br>' +
                      'MUFday: %{y:.1f}%<br>' +
                      '<extra></extra>'
    };

    // Signal power trace with S-meter (secondary y-axis2)
    const signalTrace = {
        x: hours,
        y: signalDbw,
        name: 'Signal (dBW)',
        type: 'scatter',
        mode: 'lines+markers',
        line: {
            color: '#10b981',
            width: 2
        },
        marker: {
            size: 5
        },
        yaxis: 'y3',
        hovertemplate: '<b>%{x}:00 UTC</b><br>' +
                      'Signal: %{y:.1f} dBW<br>' +
                      'S-Meter: ' + sMeterLabels.map((s, i) => i === hours.indexOf('%{x}') ? s : '').filter(Boolean)[0] + '<br>' +
                      '<extra></extra>'
    };

    // Uncertainty zone (fill between signal_10 and signal_90)
    const uncertaintyUpper = {
        x: hours,
        y: signal90,
        name: 'Signal 90%',
        type: 'scatter',
        mode: 'lines',
        line: {
            color: 'rgba(16, 185, 129, 0.3)',
            width: 0
        },
        yaxis: 'y3',
        showlegend: false,
        hoverinfo: 'skip'
    };

    const uncertaintyLower = {
        x: hours,
        y: signal10,
        name: 'Signal Range',
        type: 'scatter',
        mode: 'lines',
        fill: 'tonexty',
        fillcolor: 'rgba(16, 185, 129, 0.2)',
        line: {
            color: 'rgba(16, 185, 129, 0.3)',
            width: 0
        },
        yaxis: 'y3',
        hovertemplate: '<b>%{x}:00 UTC</b><br>' +
                      'Signal Range: %{y:.1f} to ' + signal90[hours.indexOf('%{x}')] + ' dBW<br>' +
                      '<extra></extra>'
    };

    const data = [reliabilityTrace, snrTrace, mufDayTrace, uncertaintyUpper, uncertaintyLower, signalTrace];

    const layout = {
        title: {
            text: `Propagation Chart - ${bandName} to ${propData.regions[regionCode]}`,
            font: {
                color: '#e0e0e0',
                size: 18
            }
        },
        plot_bgcolor: '#0a0e1a',
        paper_bgcolor: '#162236',
        font: {
            color: '#e0e0e0'
        },
        xaxis: {
            title: 'UTC Hour',
            gridcolor: '#2a3f5f',
            range: [0, 23],
            dtick: 2,
            tickmode: 'linear'
        },
        yaxis: {
            title: 'Reliability / MUFday (%)',
            titlefont: {color: '#4a90e2'},
            tickfont: {color: '#4a90e2'},
            gridcolor: '#2a3f5f',
            range: [0, 100],
            side: 'left'
        },
        yaxis2: {
            title: 'SNR (dB)',
            titlefont: {color: '#f59e0b'},
            tickfont: {color: '#f59e0b'},
            overlaying: 'y',
            side: 'right',
            showgrid: false
        },
        yaxis3: {
            title: 'Signal Power (dBW)',
            titlefont: {color: '#10b981'},
            tickfont: {color: '#10b981'},
            overlaying: 'y',
            side: 'right',
            position: 0.95,
            showgrid: false
        },
        legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(22, 34, 54, 0.8)',
            bordercolor: '#2a3f5f',
            borderwidth: 1
        },
        hovermode: 'x unified',
        margin: {
            l: 60,
            r: 120,
            t: 60,
            b: 60
        }
    };

    const config = {
        responsive: true,
        displayModeBar: true,
        displaylogo: false,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: `prop_chart_${bandName}_${regionCode}`,
            height: 600,
            width: 1200,
            scale: 2
        }
    };

    Plotly.newPlot('propChartContainer', data, layout, config);
}

// Initialize propagation charts tab
function initPropCharts(propData) {
    if (!window.Plotly) {
        console.error('Plotly.js not loaded. Unable to render propagation charts.');
        return;
    }

    // Default to first band and first region
    const defaultBand = Object.keys(propData.bands || {})[0] || '20m';
    const defaultRegion = Object.keys(propData.regions || {})[0] || 'EU';

    // Populate band selector
    const bandSelector = document.getElementById('propChartBandSelect');
    if (bandSelector) {
        bandSelector.innerHTML = '';
        Object.keys(propData.bands || {}).forEach(band => {
            const option = document.createElement('option');
            option.value = band;
            option.textContent = band;
            if (band === defaultBand) option.selected = true;
            bandSelector.appendChild(option);
        });
    }

    // Populate region selector
    const regionSelector = document.getElementById('propChartRegionSelect');
    if (regionSelector) {
        regionSelector.innerHTML = '';
        Object.entries(propData.regions || {}).forEach(([code, name]) => {
            const option = document.createElement('option');
            option.value = code;
            option.textContent = name;
            if (code === defaultRegion) option.selected = true;
            regionSelector.appendChild(option);
        });
    }

    // Add event listeners for selectors
    if (bandSelector) {
        bandSelector.addEventListener('change', () => {
            const band = bandSelector.value;
            const region = regionSelector?.value || defaultRegion;
            generatePropChart(band, region, propData);
        });
    }

    if (regionSelector) {
        regionSelector.addEventListener('change', () => {
            const band = bandSelector?.value || defaultBand;
            const region = regionSelector.value;
            generatePropChart(band, region, propData);
        });
    }

    // Generate initial chart
    generatePropChart(defaultBand, defaultRegion, propData);
}

// Export functions for use in dashboard.html
window.initPropCharts = initPropCharts;
window.generatePropChart = generatePropChart;
