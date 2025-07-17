// Main JavaScript for Trading System

// Update system time
function updateSystemTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const dateString = now.toLocaleDateString();
    
    if (document.getElementById('systemTime')) {
        document.getElementById('systemTime').textContent = `${dateString} ${timeString}`;
    }
}

// Format currency
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

// Format percentage
function formatPercentage(value) {
    const sign = value >= 0 ? '+' : '';
    return `${sign}${parseFloat(value).toFixed(2)}%`;
}

// Check system status
function checkSystemStatus() {
    fetch('/api/system_status')
        .then(response => response.json())
        .then(data => {
            const statusIndicator = document.getElementById('systemStatusIndicator');
            if (statusIndicator) {
                if (data.status === 'online') {
                    statusIndicator.className = 'bi bi-circle-fill text-success';
                    statusIndicator.title = 'System Online';
                } else {
                    statusIndicator.className = 'bi bi-circle-fill text-danger';
                    statusIndicator.title = 'System Offline';
                }
            }
        })
        .catch(error => console.error('Error checking system status:', error));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Update time every second
    updateSystemTime();
    setInterval(updateSystemTime, 1000);
    
    // Check system status every 30 seconds
    checkSystemStatus();
    setInterval(checkSystemStatus, 30000);
});