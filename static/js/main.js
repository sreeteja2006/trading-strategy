/**
 * Main JavaScript file for TradePro Trading System
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.classList.add('animate__animated', 'animate__fadeIn');
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Add hover effect to table rows
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', () => {
            row.classList.add('highlight-row');
        });
        row.addEventListener('mouseleave', () => {
            row.classList.remove('highlight-row');
        });
    });

    // Refresh data periodically if on system status page
    if (window.location.pathname === '/system') {
        setInterval(refreshSystemData, 30000); // Refresh every 30 seconds
    }

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add notification counter
    const notificationBadge = document.createElement('span');
    notificationBadge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
    notificationBadge.textContent = '3';
    notificationBadge.style.fontSize = '0.6rem';
    
    const notificationIcon = document.querySelector('.dropdown-toggle i.bi-person-circle');
    if (notificationIcon) {
        notificationIcon.parentElement.style.position = 'relative';
        notificationIcon.parentElement.appendChild(notificationBadge);
    }

    // Add dark mode functionality
    setupDarkMode();
});

/**
 * Refresh system status data
 */
function refreshSystemData() {
    fetch('/api/system_status')
        .then(response => response.json())
        .then(data => {
            // Update CPU usage
            const cpuElement = document.querySelector('#cpu-usage');
            if (cpuElement) {
                cpuElement.textContent = `${data.cpu_usage}%`;
                const cpuProgress = document.querySelector('#cpu-progress');
                if (cpuProgress) {
                    cpuProgress.style.width = `${data.cpu_usage}%`;
                    cpuProgress.setAttribute('aria-valuenow', data.cpu_usage);
                }
            }

            // Update memory usage
            const memoryElement = document.querySelector('#memory-usage');
            if (memoryElement) {
                memoryElement.textContent = `${data.memory_usage}%`;
                const memoryProgress = document.querySelector('#memory-progress');
                if (memoryProgress) {
                    memoryProgress.style.width = `${data.memory_usage}%`;
                    memoryProgress.setAttribute('aria-valuenow', data.memory_usage);
                }
            }

            // Update last updated time
            const lastUpdatedElement = document.querySelector('#last-updated');
            if (lastUpdatedElement) {
                const now = new Date();
                lastUpdatedElement.textContent = `Last updated: ${now.toLocaleTimeString()}`;
            }
        })
        .catch(error => console.error('Error fetching system data:', error));
}

/**
 * Setup dark mode functionality
 */
function setupDarkMode() {
    // Check for saved theme preference or use device preference
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
        document.body.classList.add('dark-mode');
        const icon = document.querySelector('#darkModeToggle i');
        if (icon) {
            icon.classList.remove('bi-moon-fill');
            icon.classList.add('bi-sun-fill');
        }
    }

    // Toggle dark mode
    document.querySelector('#darkModeToggle')?.addEventListener('click', () => {
        document.body.classList.toggle('dark-mode');
        const isDarkMode = document.body.classList.contains('dark-mode');
        localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        
        // Update charts if they exist
        updateChartsTheme(isDarkMode);
    });
}

/**
 * Update charts theme based on dark mode
 */
function updateChartsTheme(isDarkMode) {
    const charts = Plotly.d3.selectAll('.js-plotly-plot');
    if (!charts.size()) return;

    charts.each(function() {
        const chart = this._fullLayout;
        if (!chart) return;

        const update = {
            paper_bgcolor: isDarkMode ? '#2c3e50' : '#ffffff',
            plot_bgcolor: isDarkMode ? '#2c3e50' : '#ffffff',
            font: {
                color: isDarkMode ? '#ffffff' : '#333333'
            },
            xaxis: {
                gridcolor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                zerolinecolor: isDarkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'
            },
            yaxis: {
                gridcolor: isDarkMode ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.1)',
                zerolinecolor: isDarkMode ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.2)'
            }
        };
        
        Plotly.relayout(this, update);
    });
}

/**
 * Format currency values
 */
function formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
    }).format(value);
}

/**
 * Format percentage values
 */
function formatPercentage(value) {
    return `${value > 0 ? '+' : ''}${value.toFixed(2)}%`;
}

/**
 * Show notification toast
 */
function showNotification(title, message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    const toastId = `toast-${Date.now()}`;
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <small>Just now</small>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}