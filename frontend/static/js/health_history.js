/**
 * Health History Charts
 * Displays patient vital signs history with Chart.js
 */

let currentPatientId = null;
let tempChart = null;
let hrChart = null;
let oxygenChart = null;

/**
 * Show health history modal for a patient
 */
async function showHealthHistory(patientId, patientName) {
    currentPatientId = patientId;
    
    document.getElementById('healthHistoryTitle').textContent = `Health History - ${patientName}`;
    document.getElementById('healthHistoryModal').style.display = 'flex';
    document.getElementById('timeRangeSelect').value = '24';
    
    await loadHealthHistory(patientId, 24);
}

/**
 * Close health history modal
 */
function closeHealthHistory() {
    document.getElementById('healthHistoryModal').style.display = 'none';
    
    // Destroy charts
    if (tempChart) {
        tempChart.destroy();
        tempChart = null;
    }
    if (hrChart) {
        hrChart.destroy();
        hrChart = null;
    }
    if (oxygenChart) {
        oxygenChart.destroy();
        oxygenChart = null;
    }
}

/**
 * Update health history when time range changes
 */
async function updateHealthHistory() {
    const hours = parseInt(document.getElementById('timeRangeSelect').value);
    await loadHealthHistory(currentPatientId, hours);
}

/**
 * Load health history data from API
 */
async function loadHealthHistory(patientId, hours) {
    try {
        const response = await fetch(`/api/health-history/${patientId}?hours=${hours}`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success && data.records.length > 0) {
            renderCharts(data.records);
        } else {
            // Show message if no data
            alert('No health history data available yet. Data is collected hourly.');
        }
    } catch (error) {
        console.error('Error loading health history:', error);
        alert('Failed to load health history');
    }
}

/**
 * Render all three charts
 */
function renderCharts(records) {
    // Extract data
    const labels = records.map(r => {
        const date = new Date(r.timestamp);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    });
    
    const temperatures = records.map(r => ((r.temperature - 32) * 5/9).toFixed(1));
    const heartRates = records.map(r => r.heart_rate);
    const oxygenLevels = records.map(r => r.spo2);
    
    // Chart common configuration
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 2,
        plugins: {
            legend: {
                display: false
            },
            tooltip: {
                backgroundColor: 'rgba(30, 41, 59, 0.95)',
                titleFont: {
                    size: 14,
                    weight: 'bold'
                },
                bodyFont: {
                    size: 13
                },
                padding: 12,
                borderColor: 'rgba(14, 165, 233, 0.3)',
                borderWidth: 1
            }
        },
        scales: {
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    font: {
                        size: 11
                    },
                    maxRotation: 45,
                    minRotation: 45
                }
            },
            y: {
                grid: {
                    color: 'rgba(0, 0, 0, 0.05)'
                },
                ticks: {
                    font: {
                        size: 12
                    }
                }
            }
        }
    };
    
    // Temperature Chart
    if (tempChart) tempChart.destroy();
    const tempCtx = document.getElementById('temperatureChart').getContext('2d');
    tempChart = new Chart(tempCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: temperatures,
                borderColor: '#EF4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#EF4444',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    suggestedMin: 36,
                    suggestedMax: 39
                }
            }
        }
    });
    
    // Heart Rate Chart
    if (hrChart) hrChart.destroy();
    const hrCtx = document.getElementById('heartRateChart').getContext('2d');
    hrChart = new Chart(hrCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Heart Rate (BPM)',
                data: heartRates,
                borderColor: '#EC4899',
                backgroundColor: 'rgba(236, 72, 153, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#EC4899',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    suggestedMin: 50,
                    suggestedMax: 110
                }
            }
        }
    });
    
    // Oxygen Level Chart
    if (oxygenChart) oxygenChart.destroy();
    const oxygenCtx = document.getElementById('oxygenChart').getContext('2d');
    oxygenChart = new Chart(oxygenCtx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Oxygen Level (%)',
                data: oxygenLevels,
                borderColor: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: '#10B981',
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: {
            ...commonOptions,
            scales: {
                ...commonOptions.scales,
                y: {
                    ...commonOptions.scales.y,
                    suggestedMin: 90,
                    suggestedMax: 100
                }
            }
        }
    });
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById('healthHistoryModal');
    if (modal) {
        modal.addEventListener('click', function(event) {
            if (event.target === modal) {
                closeHealthHistory();
            }
        });
    }
});

// Make functions globally available
window.showHealthHistory = showHealthHistory;
window.closeHealthHistory = closeHealthHistory;
window.updateHealthHistory = updateHealthHistory;
