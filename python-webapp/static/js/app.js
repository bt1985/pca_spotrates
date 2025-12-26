/**
 * PCA Spotrates - Yield Curve Stress Testing
 * Main application JavaScript
 */

// Set default end date to today on page load
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('endDate').valueAsDate = new Date();
    checkDemoMode();
});

/**
 * Check if demo mode is active
 */
async function checkDemoMode() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        if (data.demo_mode) {
            showDemoBadge();
            showWarning('🎭 Demo Mode: Using sample data (2022-2023). For production, set DEMO_MODE=false.');
        }
    } catch (error) {
        console.log('Could not check demo mode status');
    }
}

/**
 * Show demo badge in header
 */
function showDemoBadge() {
    const header = document.querySelector('header h1');
    header.innerHTML += '<span class="demo-badge">DEMO MODE</span>';
}

/**
 * Toggle advanced options visibility
 */
function toggleAdvancedOptions() {
    const advOptions = document.getElementById('advancedOptions');
    if (advOptions.style.display === 'none') {
        advOptions.style.display = 'block';
    } else {
        advOptions.style.display = 'none';
    }
}

/**
 * Validate date inputs
 */
function validateDates() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    const startError = document.getElementById('startDateError');
    const endError = document.getElementById('endDateError');
    const analyzeBtn = document.getElementById('analyzeBtn');

    let isValid = true;

    // Clear previous errors
    startError.style.display = 'none';
    endError.style.display = 'none';

    if (!startDate || !endDate) {
        return; // Don't validate if fields are empty
    }

    const start = new Date(startDate);
    const end = new Date(endDate);
    const today = new Date();
    const minDate = new Date('2000-01-01');

    // Check if start date is before end date
    if (start >= end) {
        endError.textContent = '⚠️ End date must be after start date';
        endError.style.display = 'block';
        isValid = false;
    }

    // Check if end date is not in the future
    if (end > today) {
        endError.textContent = '⚠️ End date cannot be in the future';
        endError.style.display = 'block';
        isValid = false;
    }

    // Check if start date is not too old
    if (start < minDate) {
        startError.textContent = '⚠️ Start date should not be before 2000';
        startError.style.display = 'block';
        isValid = false;
    }

    // Check if date range is at least 30 days
    const daysDiff = (end - start) / (1000 * 60 * 60 * 24);
    if (daysDiff < 30) {
        endError.textContent = '⚠️ Date range should be at least 30 days for meaningful analysis';
        endError.style.display = 'block';
        isValid = false;
    }

    // Disable button if validation fails
    analyzeBtn.disabled = !isValid;

    return isValid;
}

/**
 * Perform PCA analysis
 */
async function performAnalysis() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    // Validate inputs
    if (!startDate || !endDate) {
        showError('Please select both start and end dates',
                 'Make sure to choose a date range for the analysis.');
        return;
    }

    if (!validateDates()) {
        return; // Validation errors are already shown
    }

    // Hide previous results and errors
    document.getElementById('results').style.display = 'none';
    document.getElementById('errorBox').style.display = 'none';
    document.getElementById('warningBox').style.display = 'none';
    document.getElementById('loading').style.display = 'block';
    document.getElementById('analyzeBtn').disabled = true;

    // Get advanced parameters
    const nComponents = parseInt(document.getElementById('nComponents').value) || 3;
    const stressQuantile = parseFloat(document.getElementById('stressQuantile').value) || 0.995;
    const rollingWindow = parseInt(document.getElementById('rollingWindow').value) || 24;

    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate,
                n_components: nComponents,
                stress_quantile: stressQuantile,
                rolling_window: rollingWindow
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Analysis failed');
        }

        displayResults(result.data);

    } catch (error) {
        handleError(error, startDate, endDate);
    } finally {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('analyzeBtn').disabled = false;
    }
}

/**
 * Handle error with helpful suggestions
 */
function handleError(error, startDate, endDate) {
    let message = error.message;
    let suggestion = '';

    // Provide helpful suggestions based on error type
    if (message.includes('proxy') || message.includes('Proxy')) {
        suggestion = 'Network connectivity issue. If running locally, try enabling DEMO_MODE=true.';
    } else if (message.includes('No data') || message.includes('empty')) {
        suggestion = `No data available for the period ${startDate} to ${endDate}. Try a different date range (e.g., 2020-2024).`;
    } else if (message.includes('index') || message.includes('bounds')) {
        suggestion = 'Insufficient data for analysis. Try selecting a longer date range (at least 90 days recommended).';
    } else if (message.includes('timeout') || message.includes('Timeout')) {
        suggestion = 'Request timed out. The ECB API might be slow. Please try again.';
    } else {
        suggestion = 'Please check your date range and try again.';
    }

    showError(message, suggestion);
}

/**
 * Display analysis results
 */
function displayResults(data) {
    // Display statistics
    const stats = data.statistics;
    const variancePC1to3 = (stats.variance_explained[0] +
                           stats.variance_explained[1] +
                           stats.variance_explained[2]) * 100;

    document.getElementById('stats').innerHTML = `
        <div class="stat-card">
            <div class="stat-label">Observations</div>
            <div class="stat-value">${stats.n_observations}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">PC1 Variance</div>
            <div class="stat-value">${(stats.variance_explained[0] * 100).toFixed(1)}%</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">PC1-3 Variance</div>
            <div class="stat-value">${variancePC1to3.toFixed(1)}%</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Date Range</div>
            <div class="stat-value" style="font-size: 1em;">${stats.date_range.start} to ${stats.date_range.end}</div>
        </div>
    `;

    // Display plots
    const yieldCurveData = JSON.parse(data.yield_curve);
    const yieldCurveLayout = yieldCurveData.layout;
    // Force full width
    yieldCurveLayout.autosize = true;
    Plotly.newPlot('yieldCurvePlot', yieldCurveData.data,
                  yieldCurveLayout, {responsive: true, displayModeBar: true});

    Plotly.newPlot('pcPlot', JSON.parse(data.principal_components).data,
                  JSON.parse(data.principal_components).layout, {responsive: true});

    Plotly.newPlot('variancePlot', JSON.parse(data.explained_variance).data,
                  JSON.parse(data.explained_variance).layout, {responsive: true});

    Plotly.newPlot('stressedScoresPlot', JSON.parse(data.stressed_scores).data,
                  JSON.parse(data.stressed_scores).layout, {responsive: true});

    Plotly.newPlot('scenariosPlot', JSON.parse(data.stress_scenarios).data,
                  JSON.parse(data.stress_scenarios).layout, {responsive: true});

    document.getElementById('results').style.display = 'block';

    // Scroll to results
    document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Show error message
 */
function showError(message, suggestion = '') {
    const errorBox = document.getElementById('errorBox');
    errorBox.innerHTML = `
        <strong>⚠️ Error</strong>
        <div>${message}</div>
        ${suggestion ? `<div class="error-details">💡 Suggestion: ${suggestion}</div>` : ''}
    `;
    errorBox.style.display = 'block';

    // Scroll to error
    errorBox.scrollIntoView({ behavior: 'smooth' });
}

/**
 * Show warning message
 */
function showWarning(message) {
    const warningBox = document.getElementById('warningBox');
    warningBox.innerHTML = message;
    warningBox.style.display = 'block';
}

/**
 * Export data in specified format
 */
async function exportData(format) {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;

    if (!startDate || !endDate) {
        showError('Please perform an analysis first before exporting');
        return;
    }

    try {
        const endpoint = format === 'csv' ? '/api/export/csv' : '/api/export/excel';

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                start_date: startDate,
                end_date: endDate
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Export failed');
        }

        // Create a blob from the response
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;

        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = `export_${startDate}_${endDate}.${format === 'csv' ? 'csv' : 'xlsx'}`;
        if (contentDisposition) {
            const filenameMatch = contentDisposition.match(/filename="?(.+)"?/i);
            if (filenameMatch) {
                filename = filenameMatch[1].replace(/"/g, '');
            }
        }

        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        console.log(`${format.toUpperCase()} export successful`);

    } catch (error) {
        showError(`Export failed: ${error.message}`);
    }
}
