// Bot Control Panel JavaScript

document.addEventListener('DOMContentLoaded', function() {
    loadBotStatus();
    setInterval(loadBotStatus, 5000);
    initRangeSliders();
});

function controlBot(action) {
    fetch(`/api/bot/${action}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadBotStatus();
                showNotification(`Bot ${action}ed successfully`, 'success');
            } else {
                showNotification(data.error || 'Action failed', 'error');
            }
        })
        .catch(err => showNotification('Connection error', 'error'));
}

function loadBotStatus() {
    fetch('/api/bot/status')
        .then(response => response.json())
        .then(data => updateUI(data))
        .catch(err => console.error('Status load error:', err));
}

function updateUI(data) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    const btnStart = document.getElementById('btn-start');
    const btnPause = document.getElementById('btn-pause');
    const btnStop = document.getElementById('btn-stop');
    
    if (!indicator || !statusText) return;
    
    indicator.className = 'status-indicator ' + (data.status === 'running' ? 'online' : data.status === 'paused' ? 'paused' : '');
    statusText.textContent = data.status ? data.status.charAt(0).toUpperCase() + data.status.slice(1) : 'Stopped';
    
    if (btnStart) btnStart.disabled = data.status === 'running';
    if (btnPause) btnPause.disabled = data.status !== 'running';
    if (btnStop) btnStop.disabled = data.status === 'stopped' || !data.status;
}

function addPair() {
    const select = document.getElementById('pair-select');
    if (!select || !select.value) return;
    
    fetch('/api/trading/pairs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pair: select.value })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadActivePairs();
            select.value = '';
        }
    });
}

function saveRiskParams() {
    const params = {
        maxPosition: document.getElementById('max-position').value,
        stopLoss: document.getElementById('stop-loss').value,
        takeProfit: document.getElementById('take-profit').value
    };
    
    fetch('/api/trading/risk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    })
    .then(response => response.json())
    .then(data => showNotification(data.success ? 'Parameters saved' : 'Save failed', data.success ? 'success' : 'error'));
}

function closeAllPositions() {
    if (!confirm('Close ALL open positions?')) return;
    fetch('/api/positions/close-all', { method: 'POST' })
        .then(response => response.json())
        .then(data => showNotification(data.success ? 'All positions closed' : 'Failed', data.success ? 'success' : 'error'));
}

function cancelAllOrders() {
    if (!confirm('Cancel ALL pending orders?')) return;
    fetch('/api/orders/cancel-all', { method: 'POST' })
        .then(response => response.json())
        .then(data => showNotification(data.success ? 'All orders cancelled' : 'Failed', data.success ? 'success' : 'error'));
}

function emergencyStop() {
    if (!confirm('EMERGENCY STOP: This will close all positions and stop the bot. Continue?')) return;
    fetch('/api/bot/emergency-stop', { method: 'POST' })
        .then(response => response.json())
        .then(data => { loadBotStatus(); showNotification('Emergency stop executed', 'warning'); });
}

function initRangeSliders() {
    const slider = document.getElementById('max-position');
    const display = document.getElementById('max-position-value');
    if (slider && display) {
        slider.addEventListener('input', function() { display.textContent = this.value + '%'; });
    }
}

function showNotification(message, type) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'warning'} position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 250px;';
    toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'exclamation'}-circle me-2"></i>${message}`;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
