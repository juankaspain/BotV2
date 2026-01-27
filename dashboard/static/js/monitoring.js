// Real-time Monitoring JavaScript with WebSocket

let ws = null;
let liveChart = null;
let tradeCount = 0;

document.addEventListener('DOMContentLoaded', function() {
    initChart();
    connectWebSocket();
    setInterval(updateMetrics, 5000);
});

function connectWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws/monitor`;
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function() {
        updateConnectionStatus('connected');
        addLog('WebSocket connected', 'success');
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };
    
    ws.onclose = function() {
        updateConnectionStatus('disconnected');
        addLog('WebSocket disconnected', 'warning');
        setTimeout(connectWebSocket, 5000);
    };
    
    ws.onerror = function(error) {
        updateConnectionStatus('error');
        addLog('WebSocket error', 'error');
    };
}

function updateConnectionStatus(status) {
    const indicator = document.getElementById('ws-indicator');
    const statusText = document.getElementById('ws-status');
    const alertDiv = document.getElementById('connection-status');
    
    if (!indicator || !statusText) return;
    
    const states = {
        connected: { color: '#1cc88a', text: 'Connected to real-time feed', class: 'alert-success' },
        disconnected: { color: '#f6c23e', text: 'Disconnected - Reconnecting...', class: 'alert-warning' },
        error: { color: '#e74a3b', text: 'Connection error', class: 'alert-danger' }
    };
    
    const state = states[status];
    indicator.style.color = state.color;
    statusText.textContent = state.text;
    if (alertDiv) alertDiv.className = `alert ${state.class} d-flex align-items-center mb-4`;
}

function handleMessage(data) {
    switch(data.type) {
        case 'price': updateChart(data); break;
        case 'trade': addTrade(data); break;
        case 'orderbook': updateOrderbook(data); break;
        case 'metrics': updateMetricsDisplay(data); break;
    }
}

function initChart() {
    const ctx = document.getElementById('live-chart');
    if (!ctx) return;
    
    liveChart = new Chart(ctx, {
        type: 'line',
        data: { labels: [], datasets: [{ label: 'Price', data: [], borderColor: '#4e73df', borderWidth: 2, fill: false, pointRadius: 0 }] },
        options: {
            responsive: true, maintainAspectRatio: false, animation: { duration: 0 },
            scales: { x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#a0a0a0', maxTicksLimit: 10 } }, y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#a0a0a0' } } },
            plugins: { legend: { display: false } }
        }
    });
}

function updateChart(data) {
    if (!liveChart) return;
    const maxPoints = 100;
    liveChart.data.labels.push(new Date(data.time).toLocaleTimeString());
    liveChart.data.datasets[0].data.push(data.price);
    if (liveChart.data.labels.length > maxPoints) { liveChart.data.labels.shift(); liveChart.data.datasets[0].data.shift(); }
    liveChart.update('none');
}

function addTrade(data) {
    const tbody = document.getElementById('trades-body');
    if (!tbody) return;
    tradeCount++;
    const row = document.createElement('tr');
    row.innerHTML = `<td>${new Date(data.time).toLocaleTimeString()}</td><td>${data.price}</td><td>${data.amount}</td><td class="${data.side === 'buy' ? 'text-success' : 'text-danger'}">${data.side.toUpperCase()}</td>`;
    tbody.insertBefore(row, tbody.firstChild);
    if (tbody.children.length > 50) tbody.removeChild(tbody.lastChild);
    document.getElementById('trade-count').textContent = tradeCount;
}

function updateMetrics() {
    fetch('/api/metrics').then(r => r.json()).then(data => updateMetricsDisplay(data)).catch(err => console.error(err));
}

function updateMetricsDisplay(data) {
    const els = { 'latency': `${data.latency || '--'}ms`, 'msg-rate': data.msgRate || '--', 'cpu-usage': `${data.cpu || '--'}%`, 'memory-usage': `${data.memory || '--'}MB`, 'order-rate': data.orderRate || '--', 'uptime': data.uptime || '--' };
    Object.entries(els).forEach(([id, val]) => { const el = document.getElementById(id); if (el) el.textContent = val; });
}

function addLog(message, type = 'info') {
    const container = document.getElementById('logs-container');
    if (!container) return;
    const entry = document.createElement('div');
    entry.className = `log-entry log-${type}`;
    entry.innerHTML = `[${new Date().toLocaleTimeString()}] ${message}`;
    container.insertBefore(entry, container.firstChild);
    if (container.children.length > 100) container.removeChild(container.lastChild);
}

function clearLogs() { const c = document.getElementById('logs-container'); if (c) c.innerHTML = ''; }
function downloadLogs() { const c = document.getElementById('logs-container'); if (!c) return; const blob = new Blob([c.innerText], {type: 'text/plain'}); const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = 'trading_logs.txt'; a.click(); }
