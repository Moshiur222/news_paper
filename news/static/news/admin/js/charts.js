/**
 * AdminDek - Modern Admin Dashboard
 * Charts JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    initChartResize();
});

/**
 * Initialize Charts
 */
function initCharts() {
    initRevenueChart();
    initSalesChart();
    initOrderChart();
    initUserChart();
}

/**
 * Revenue Chart
 */
function initRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [
                {
                    label: 'Revenue',
                    data: [12000, 19000, 15000, 25000, 22000, 30000, 35000],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                },
                {
                    label: 'Expenses',
                    data: [8000, 12000, 10000, 18000, 15000, 20000, 22000],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: '#f59e0b',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 5,
                    pointHoverRadius: 7
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20,
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: {
                        family: "'Nunito', sans-serif",
                        size: 14,
                        weight: '700'
                    },
                    bodyFont: {
                        family: "'Nunito', sans-serif",
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    displayColors: true,
                    callbacks: {
                        label: function(context) {
                            let label = context.dataset.label || '';
                            if (label) {
                                label += ': ';
                            }
                            if (context.parsed.y !== null) {
                                label += '$' + context.parsed.y.toLocaleString();
                            }
                            return label;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12
                        },
                        color: '#64748b'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(226, 232, 240, 0.8)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12
                        },
                        color: '#64748b',
                        callback: function(value) {
                            return '$' + value / 1000 + 'k';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Sales Chart
 */
function initSalesChart() {
    const ctx = document.getElementById('salesChart');
    
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            datasets: [
                {
                    label: 'Online Sales',
                    data: [4500, 5200, 4800, 6100, 5500, 6700, 7200, 8100, 7800, 9200, 8900, 10500],
                    backgroundColor: 'rgba(99, 102, 241, 0.8)',
                    borderColor: '#6366f1',
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false,
                },
                {
                    label: 'Offline Sales',
                    data: [3200, 3800, 3400, 4200, 3900, 4800, 5100, 5600, 5300, 6400, 6100, 7200],
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: '#10b981',
                    borderWidth: 1,
                    borderRadius: 6,
                    borderSkipped: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    align: 'end',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'rect',
                        padding: 20,
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: {
                        family: "'Nunito', sans-serif",
                        size: 14,
                        weight: '700'
                    },
                    bodyFont: {
                        family: "'Nunito', sans-serif",
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12
                        },
                        color: '#64748b'
                    }
                },
                y: {
                    grid: {
                        color: 'rgba(226, 232, 240, 0.8)',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12
                        },
                        color: '#64748b',
                        callback: function(value) {
                            return '$' + value / 1000 + 'k';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Order Statistics Chart (Doughnut)
 */
function initOrderChart() {
    const ctx = document.getElementById('orderChart');
    
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Completed', 'Pending', 'Cancelled', 'Processing'],
            datasets: [{
                data: [65, 20, 10, 5],
                backgroundColor: [
                    '#10b981',
                    '#f59e0b',
                    '#ef4444',
                    '#6366f1'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '70%',
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20,
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: {
                        family: "'Nunito', sans-serif",
                        size: 14,
                        weight: '700'
                    },
                    bodyFont: {
                        family: "'Nunito', sans-serif",
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * User Registration Chart (Pie)
 */
function initUserChart() {
    const ctx = document.getElementById('userChart');
    
    if (!ctx) return;
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Direct', 'Social', 'Referral', 'Organic'],
            datasets: [{
                data: [35, 25, 20, 20],
                backgroundColor: [
                    '#6366f1',
                    '#0ea5e9',
                    '#10b981',
                    '#f59e0b'
                ],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'circle',
                        padding: 20,
                        font: {
                            family: "'Nunito', sans-serif",
                            size: 12,
                            weight: '600'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: '#1e293b',
                    titleFont: {
                        family: "'Nunito', sans-serif",
                        size: 14,
                        weight: '700'
                    },
                    bodyFont: {
                        family: "'Nunito', sans-serif",
                        size: 13
                    },
                    padding: 12,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return context.label + ': ' + context.parsed + '%';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Handle Chart Resize
 */
function initChartResize() {
    window.addEventListener('chartResize', function() {
        // Trigger resize for all charts
        Chart.instances.forEach(chart => {
            chart.resize();
        });
    });
}

/**
 * Update Chart Data (Example)
 */
function updateChartData(chartId, newData) {
    const chart = Chart.instances.find(instance => instance.canvas.id === chartId);
    
    if (chart) {
        chart.data.datasets[0].data = newData;
        chart.update();
    }
}

/**
 * Destroy Chart
 */
function destroyChart(chartId) {
    const chart = Chart.instances.find(instance => instance.canvas.id === chartId);
    
    if (chart) {
        chart.destroy();
    }
}

// Export for global use
window.AdminCharts = {
    updateChartData,
    destroyChart
};
