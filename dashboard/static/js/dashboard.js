// Dashboard JavaScript - Charts and Data Updates

let performanceChart = null;
let allocationChart = null;

document.addEventListener('DOMContentLoaded', function() {
    initCharts();
    loadDashboardData();
    setInterval(loadDashboardData, 30000);
});

function initCharts() {
    const perfCtx = document.getElementById('performance-chart');
    if (perfCtx) {
        performanceChart = new Chart(perfCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Portfolio Value',
                    data: [],
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#a0a0a0' } },
                    y: { grid: { color: 'rgba(255,255,255,0.1)' }, ticks: { color: '#a0a0a0' } }
                }
            }
        });
    }
    
    const allocCtx = document.getElementById('allocation-chart');
    if (allocCtx) {
        allocationChart = new Chart(allocCtx, {
            type: 'doughnut',
            data: {
                labels: ['BTC', 'ETH', 'USDT', 'Other'],
                datasets: [{
                    data: [40, 30, 20, 10],
                    backgroundColor: ['#f7931a', '#627eea', '#26a17b', '#4e73df']
                }]
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { color: '#a0a0a0' } } } }
        });
    }
}

function loadDashboardData() {
    fetch('/api/dashboard')
        .then(response => response.json())
        .then(data => {
            updateStats(data.stats);
            updateChart(data.performance);
            updatePositions(data.positions);
            updateTrades(data.trades);
        })
        .catch(err => console.error('Dashboard load error:', err));
}

function updateStats(stats) {
    if (!stats) return;
    const elements = {
        'total-balance': `$${(stats.balance || 0).toLocaleString()}`,
        'balance-change': `${stats.balanceChange >= 0 ? '+' : ''}${stats.balanceChange || 0}%`,
        'daily-pnl': `$${(stats.dailyPnl || 0).toLocaleString()}`,
        'daily-trades': `${stats.dailyTrades || 0} trades`,
        'win-rate': `${stats.winRate || 0}%`,
        'total-trades': `${stats.totalTrades || 0} total trades`,
        'bot-status': stats.botStatus || 'Offline',
        'bot-uptime': stats.uptime || '--'
    };
    Object.entries(elements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    });
}

function updateChart(performance) {
    if (!performanceChart || !performance) return;
    performanceChart.data.labels = performance.labels;
    performanceChart.data.datasets[0].data = performance.values;
    performanceChart.update();
}

function updatePositions(positions) {
    const tbody = document.getElementById('positions-body');
    if (!tbody) return;
    if (!positions || positions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No open positions</td></tr>';
        return;
    }
    tbody.innerHTML = positions.map(p => `
        <tr>
            <td><strong>${p.symbol}</strong></td>
            <td class="${p.side === 'long' ? 'text-success' : 'text-danger'}">${p.side.toUpperCase()}</td>
            <td>${p.size}</td>
            <td>$${p.entry.toLocaleString()}</td>
            <td class="${p.pnl >= 0 ? 'text-success' : 'text-danger'}">${p.pnl >= 0 ? '+' : ''}$${p.pnl.toLocaleString()}</td>
            <td><button class="btn btn-sm btn-outline-danger" onclick="closePosition('${p.id}')">Close</button></td>
        </tr>
    `).join('');
    document.getElementById('position-count').textContent = positions.length;
}

function updateTrades(trades) {
    const tbody = document.getElementById('trades-body');
    if (!tbody) return;
    if (!trades || trades.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted">No recent trades</td></tr>';
        return;
    }
    tbody.innerHTML = trades.slice(0, 10).map(t => `
        <tr>
            <td>${new Date(t.time).toLocaleTimeString()}</td>
            <td>${t.symbol}</td>
            <td>${t.type}</td>
            <td class="${t.pnl >= 0 ? 'text-success' : 'text-danger'}">${t.pnl >= 0 ? '+' : ''}$${t.pnl.toFixed(2)}</td>
        </tr>
    `).join('');
}

function closePosition(positionId) {
    if (!confirm('Close this position?')) return;
    fetch(`/api/positions/${positionId}/close`, { method: 'POST' })
        .then(response => response.json())
        .then(data => { if (data.success) loadDashboardData(); })
        .catch(err => console.error('Close position error:', err));
}

document.querySelectorAll('[data-period]').forEach(btn => {
    btn.addEventListener('click', function() {
        document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        loadDashboardData();
    });
});
