/**
 * StockMaster Pro - Advanced Charts
 * A collection of chart components for data visualization
 */

class StockmasterCharts {
  constructor() {
    this.charts = {};
    this.colors = {
      primary: getComputedStyle(document.documentElement).getPropertyValue('--primary-500').trim() || '#6366F1',
      secondary: getComputedStyle(document.documentElement).getPropertyValue('--primary-400').trim() || '#818CF8',
      tertiary: getComputedStyle(document.documentElement).getPropertyValue('--primary-300').trim() || '#A5B4FC',
      success: getComputedStyle(document.documentElement).getPropertyValue('--success-500').trim() || '#10B981',
      danger: getComputedStyle(document.documentElement).getPropertyValue('--danger-500').trim() || '#EF4444',
      warning: getComputedStyle(document.documentElement).getPropertyValue('--warning-500').trim() || '#F59E0B',
      info: getComputedStyle(document.documentElement).getPropertyValue('--info-500').trim() || '#3B82F6',
      textPrimary: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#111827',
      textSecondary: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#4B5563',
      textTertiary: getComputedStyle(document.documentElement).getPropertyValue('--text-tertiary').trim() || '#9CA3AF',
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#E5E7EB',
    };

    // Listen for theme changes
    document.addEventListener('themeChanged', this.updateColors.bind(this));
  }

  /**
   * Update chart colors when theme changes
   */
  updateColors() {
    this.colors = {
      primary: getComputedStyle(document.documentElement).getPropertyValue('--primary-500').trim() || '#6366F1',
      secondary: getComputedStyle(document.documentElement).getPropertyValue('--primary-400').trim() || '#818CF8',
      tertiary: getComputedStyle(document.documentElement).getPropertyValue('--primary-300').trim() || '#A5B4FC',
      success: getComputedStyle(document.documentElement).getPropertyValue('--success-500').trim() || '#10B981',
      danger: getComputedStyle(document.documentElement).getPropertyValue('--danger-500').trim() || '#EF4444',
      warning: getComputedStyle(document.documentElement).getPropertyValue('--warning-500').trim() || '#F59E0B',
      info: getComputedStyle(document.documentElement).getPropertyValue('--info-500').trim() || '#3B82F6',
      textPrimary: getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#111827',
      textSecondary: getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#4B5563',
      textTertiary: getComputedStyle(document.documentElement).getPropertyValue('--text-tertiary').trim() || '#9CA3AF',
      borderColor: getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim() || '#E5E7EB',
    };

    // Update all charts
    Object.values(this.charts).forEach(chart => {
      if (chart && typeof chart.update === 'function') {
        this.updateChartColors(chart);
        chart.update();
      }
    });
  }

  /**
   * Update chart colors
   * @param {Object} chart - Chart.js instance
   */
  updateChartColors(chart) {
    if (!chart || !chart.options) return;

    // Update grid lines
    if (chart.options.scales && chart.options.scales.x) {
      chart.options.scales.x.grid = {
        ...chart.options.scales.x.grid,
        color: this.colors.borderColor,
      };
    }

    if (chart.options.scales && chart.options.scales.y) {
      chart.options.scales.y.grid = {
        ...chart.options.scales.y.grid,
        color: this.colors.borderColor,
      };
    }

    // Update text colors
    if (chart.options.plugins && chart.options.plugins.legend) {
      chart.options.plugins.legend.labels = {
        ...chart.options.plugins.legend.labels,
        color: this.colors.textPrimary,
      };
    }

    if (chart.options.scales && chart.options.scales.x) {
      chart.options.scales.x.ticks = {
        ...chart.options.scales.x.ticks,
        color: this.colors.textSecondary,
      };
    }

    if (chart.options.scales && chart.options.scales.y) {
      chart.options.scales.y.ticks = {
        ...chart.options.scales.y.ticks,
        color: this.colors.textSecondary,
      };
    }
  }

  /**
   * Create a line chart
   * @param {string} elementId - Canvas element ID
   * @param {Object} data - Chart data
   * @param {Object} options - Chart options
   * @returns {Object} - Chart instance
   */
  createLineChart(elementId, data, options = {}) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    // Default options
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 20,
            color: this.colors.textPrimary,
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          titleColor: this.colors.textPrimary,
          bodyColor: this.colors.textSecondary,
          borderColor: this.colors.borderColor,
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          boxWidth: 8,
          boxHeight: 8,
          cornerRadius: 4,
        }
      },
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false,
          },
          ticks: {
            color: this.colors.textSecondary,
            padding: 10,
          }
        },
        y: {
          grid: {
            color: this.colors.borderColor,
            drawBorder: false,
            borderDash: [5, 5],
          },
          ticks: {
            color: this.colors.textSecondary,
            padding: 10,
          },
          beginAtZero: true
        }
      },
      elements: {
        line: {
          tension: 0.4
        },
        point: {
          radius: 4,
          hoverRadius: 6,
          borderWidth: 2,
          backgroundColor: 'white'
        }
      },
      interaction: {
        mode: 'index',
        intersect: false,
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    };

    // Merge options
    const chartOptions = { ...defaultOptions, ...options };

    // Create chart
    const chart = new Chart(ctx, {
      type: 'line',
      data: data,
      options: chartOptions
    });

    // Store chart instance
    this.charts[elementId] = chart;

    return chart;
  }

  /**
   * Create a bar chart
   * @param {string} elementId - Canvas element ID
   * @param {Object} data - Chart data
   * @param {Object} options - Chart options
   * @returns {Object} - Chart instance
   */
  createBarChart(elementId, data, options = {}) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    // Default options
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            usePointStyle: true,
            padding: 20,
            color: this.colors.textPrimary,
          }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          titleColor: this.colors.textPrimary,
          bodyColor: this.colors.textSecondary,
          borderColor: this.colors.borderColor,
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          boxWidth: 8,
          boxHeight: 8,
          cornerRadius: 4,
        }
      },
      scales: {
        x: {
          grid: {
            display: false,
            drawBorder: false,
          },
          ticks: {
            color: this.colors.textSecondary,
            padding: 10,
          }
        },
        y: {
          grid: {
            color: this.colors.borderColor,
            drawBorder: false,
            borderDash: [5, 5],
          },
          ticks: {
            color: this.colors.textSecondary,
            padding: 10,
          },
          beginAtZero: true
        }
      },
      animation: {
        duration: 1000,
        easing: 'easeOutQuart'
      }
    };

    // Merge options
    const chartOptions = { ...defaultOptions, ...options };

    // Create chart
    const chart = new Chart(ctx, {
      type: 'bar',
      data: data,
      options: chartOptions
    });

    // Store chart instance
    this.charts[elementId] = chart;

    return chart;
  }

  /**
   * Create a doughnut chart
   * @param {string} elementId - Canvas element ID
   * @param {Object} data - Chart data
   * @param {Object} options - Chart options
   * @returns {Object} - Chart instance
   */
  createDoughnutChart(elementId, data, options = {}) {
    const canvas = document.getElementById(elementId);
    if (!canvas) return null;

    const ctx = canvas.getContext('2d');
    
    // Default options
    const defaultOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            usePointStyle: true,
            padding: 20,
            color: this.colors.textPrimary,
          }
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          titleColor: this.colors.textPrimary,
          bodyColor: this.colors.textSecondary,
          borderColor: this.colors.borderColor,
          borderWidth: 1,
          padding: 12,
          boxPadding: 6,
          usePointStyle: true,
          boxWidth: 8,
          boxHeight: 8,
          cornerRadius: 4,
        }
      },
      cutout: '70%',
      animation: {
        animateScale: true,
        animateRotate: true,
        duration: 1000,
        easing: 'easeOutQuart'
      }
    };

    // Merge options
    const chartOptions = { ...defaultOptions, ...options };

    // Create chart
    const chart = new Chart(ctx, {
      type: 'doughnut',
      data: data,
      options: chartOptions
    });

    // Store chart instance
    this.charts[elementId] = chart;

    return chart;
  }

  /**
   * Update chart data
   * @param {string} chartId - Chart ID
   * @param {Object} newData - New chart data
   */
  updateChartData(chartId, newData) {
    const chart = this.charts[chartId];
    if (!chart) return;

    chart.data = newData;
    chart.update();
  }

  /**
   * Destroy a chart
   * @param {string} chartId - Chart ID
   */
  destroyChart(chartId) {
    const chart = this.charts[chartId];
    if (!chart) return;

    chart.destroy();
    delete this.charts[chartId];
  }

  /**
   * Destroy all charts
   */
  destroyAllCharts() {
    Object.keys(this.charts).forEach(chartId => {
      this.destroyChart(chartId);
    });
  }
}

// Create global charts instance
window.stockmasterCharts = new StockmasterCharts();
