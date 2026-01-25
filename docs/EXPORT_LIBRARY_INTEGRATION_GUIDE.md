# 📥 ExportLibrary Integration Guide - Dashboard v7.4

**Complete guide for integrating professional export capabilities (Excel & PDF) into BotV2 Dashboard**

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Excel Export with SheetJS](#excel-export-with-sheetjs)
5. [PDF Export with jsPDF](#pdf-export-with-jspdf)
6. [Integration with Dashboard v7.4](#integration-with-dashboard-v74)
7. [Advanced Features](#advanced-features)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Complete Examples](#complete-examples)

---

## 🎯 Overview

### Current State (Dashboard v7.4)

El Dashboard v7.4 incluye un sistema de export básico que soporta:
- ✅ **CSV Export**: Completamente funcional
- ⚠️ **Excel Export**: Placeholder (requiere SheetJS)
- ⚠️ **PDF Export**: Placeholder (requiere jsPDF)

### Goal

Integrar bibliotecas profesionales para exports de Excel y PDF con:
- Multi-sheet Excel workbooks
- Styled cells (colores, fuentes, bordes)
- PDF con tablas, gráficos y formato profesional
- Progress indicators
- Error handling robusto

---

## ✅ Prerequisites

### Required Knowledge
- JavaScript ES6+
- DOM manipulation
- Async/await patterns
- Dashboard v7.4 architecture

### System Requirements
- Node.js 18+ (para instalar dependencias)
- NPM o Yarn
- Dashboard v7.4 ya instalado

---

## 📦 Installation

### Option 1: CDN (Recommended for Quick Start)

#### SheetJS via CDN
```html
<!-- Add to dashboard.html before closing </body> -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
```

#### jsPDF via CDN
```html
<!-- Add to dashboard.html before closing </body> -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
```

**Complete Addition to `dashboard.html`:**
```html
<!-- Right before closing </body> tag -->

<!-- Export Libraries -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>

<!-- Dashboard Scripts -->
<script src="{{ url_for('static', filename='js/performance-optimizer.js') }}"></script>
<script src="{{ url_for('static', filename='js/dashboard-optimized.js') }}"></script>
</body>
```

### Option 2: NPM Install (For Production)

```bash
cd src/dashboard/static/js

# Initialize package.json if not exists
npm init -y

# Install dependencies
npm install xlsx jspdf jspdf-autotable

# Build bundle (requires webpack/rollup)
npm run build
```

**Verification:**
```javascript
// Open browser console after loading dashboard
console.log('SheetJS:', typeof XLSX !== 'undefined' ? '✅ Loaded' : '❌ Not loaded');
console.log('jsPDF:', typeof jspdf !== 'undefined' ? '✅ Loaded' : '❌ Not loaded');
```

---

## 📊 Excel Export with SheetJS

### Basic Implementation

#### 1. Replace Placeholder in `dashboard-optimized.js`

**Find this section:**
```javascript
toExcel() {
    Logger.export('Excel export - requires SheetJS library');
    // Placeholder - would use SheetJS
}
```

**Replace with:**
```javascript
toExcel() {
    Logger.export('Exporting to Excel...');
    
    try {
        // Check if SheetJS is loaded
        if (typeof XLSX === 'undefined') {
            throw new Error('SheetJS library not loaded. Add CDN script to dashboard.html');
        }
        
        const data = this.gatherExportData();
        
        // Create workbook
        const wb = XLSX.utils.book_new();
        
        // Sheet 1: Summary
        const summaryData = [
            ['BotV2 Dashboard Export'],
            ['Generated:', new Date().toISOString()],
            [''],
            ['Metric', 'Value'],
            ...data.map(item => [item.metric, item.value])
        ];
        const ws1 = XLSX.utils.aoa_to_sheet(summaryData);
        XLSX.utils.book_append_sheet(wb, ws1, 'Summary');
        
        // Sheet 2: Performance Metrics
        const perfData = this.getPerformanceMetrics();
        const ws2 = XLSX.utils.json_to_sheet(perfData);
        XLSX.utils.book_append_sheet(wb, ws2, 'Performance');
        
        // Sheet 3: Trades (if available)
        const tradesData = this.getTradesData();
        if (tradesData.length > 0) {
            const ws3 = XLSX.utils.json_to_sheet(tradesData);
            XLSX.utils.book_append_sheet(wb, ws3, 'Trades');
        }
        
        // Generate Excel file
        const filename = `BotV2_Dashboard_${new Date().toISOString().split('T')[0]}.xlsx`;
        XLSX.writeFile(wb, filename);
        
        Logger.export(`Excel export complete: ${filename}`);
        this.showExportSuccess('Excel', filename);
        
    } catch (error) {
        Logger.error('Excel export failed', error);
        this.showExportError('Excel', error.message);
    }
}
```

#### 2. Add Helper Methods

```javascript
// Add to ExportSystem object

getPerformanceMetrics() {
    return [
        { Date: '2026-01-25', Return: '2.5%', Sharpe: '1.8', MaxDD: '-5.2%' },
        { Date: '2026-01-24', Return: '1.8%', Sharpe: '1.7', MaxDD: '-5.5%' },
        { Date: '2026-01-23', Return: '3.2%', Sharpe: '1.9', MaxDD: '-4.8%' }
        // Fetch from actual data source
    ];
},

getTradesData() {
    return [
        { 
            Date: '2026-01-25', 
            Symbol: 'BTC', 
            Action: 'BUY', 
            Size: 0.5, 
            Price: 45000, 
            PnL: 1200 
        },
        { 
            Date: '2026-01-25', 
            Symbol: 'ETH', 
            Action: 'SELL', 
            Size: 2, 
            Price: 2500, 
            PnL: -300 
        }
        // Fetch from actual data source
    ];
},

showExportSuccess(format, filename) {
    // Show success notification
    if (typeof AnalyticsManager !== 'undefined') {
        AnalyticsManager.track('export_success', { format, filename });
    }
    
    // Optional: Show toast notification
    this.showToast(`✅ ${format} export successful: ${filename}`, 'success');
},

showExportError(format, message) {
    // Show error notification
    if (typeof ErrorTracker !== 'undefined') {
        ErrorTracker.track(`${format} export failed`, message);
    }
    
    this.showToast(`❌ ${format} export failed: ${message}`, 'error');
},

showToast(message, type) {
    // Simple toast notification (you can use a library like Toastify)
    console.log(`[${type.toUpperCase()}] ${message}`);
    
    // Optional: Create visual toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 16px 24px;
        background: ${type === 'success' ? '#3fb950' : '#f85149'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
```

### Advanced Excel Features

#### Styled Cells

```javascript
toExcelAdvanced() {
    const wb = XLSX.utils.book_new();
    
    // Create worksheet with data
    const ws = XLSX.utils.aoa_to_sheet([
        ['BotV2 Dashboard Report'],
        ['Generated:', new Date().toLocaleString()],
        [],
        ['Metric', 'Value', 'Status']
    ]);
    
    // Apply styles (requires xlsx-style or custom implementation)
    // Note: Basic XLSX doesn't support styling, need xlsx-style
    
    // Set column widths
    ws['!cols'] = [
        { wch: 30 },  // Column A width
        { wch: 20 },  // Column B width
        { wch: 15 }   // Column C width
    ];
    
    // Merge cells for title
    ws['!merges'] = [
        { s: { r: 0, c: 0 }, e: { r: 0, c: 2 } }  // Merge A1:C1
    ];
    
    XLSX.utils.book_append_sheet(wb, ws, 'Report');
    XLSX.writeFile(wb, 'BotV2_Advanced_Report.xlsx');
}
```

#### Multi-Sheet with Real Data

```javascript
async toExcelComplete() {
    try {
        // Show progress
        this.showProgress('Generating Excel report...');
        
        const wb = XLSX.utils.book_new();
        
        // Sheet 1: Dashboard Overview
        const overviewData = await this.fetchDashboardOverview();
        const ws1 = XLSX.utils.json_to_sheet(overviewData);
        XLSX.utils.book_append_sheet(wb, ws1, 'Overview');
        
        // Sheet 2: Performance Metrics
        const perfData = await this.fetchPerformanceData();
        const ws2 = XLSX.utils.json_to_sheet(perfData);
        XLSX.utils.book_append_sheet(wb, ws2, 'Performance');
        
        // Sheet 3: All Trades
        const tradesData = await this.fetchAllTrades();
        const ws3 = XLSX.utils.json_to_sheet(tradesData);
        XLSX.utils.book_append_sheet(wb, ws3, 'Trades');
        
        // Sheet 4: Risk Metrics
        const riskData = await this.fetchRiskMetrics();
        const ws4 = XLSX.utils.json_to_sheet(riskData);
        XLSX.utils.book_append_sheet(wb, ws4, 'Risk Analysis');
        
        // Generate and download
        const filename = `BotV2_Complete_Report_${Date.now()}.xlsx`;
        XLSX.writeFile(wb, filename);
        
        this.hideProgress();
        this.showExportSuccess('Excel', filename);
        
    } catch (error) {
        this.hideProgress();
        this.showExportError('Excel', error.message);
    }
}
```

---

## 📄 PDF Export with jsPDF

### Basic Implementation

#### 1. Replace Placeholder in `dashboard-optimized.js`

**Find this section:**
```javascript
toPDF() {
    Logger.export('PDF export - requires jsPDF library');
    // Placeholder - would use jsPDF
}
```

**Replace with:**
```javascript
toPDF() {
    Logger.export('Exporting to PDF...');
    
    try {
        // Check if jsPDF is loaded
        if (typeof jspdf === 'undefined') {
            throw new Error('jsPDF library not loaded. Add CDN script to dashboard.html');
        }
        
        const { jsPDF } = jspdf;
        const doc = new jsPDF();
        
        // Title
        doc.setFontSize(20);
        doc.setTextColor(47, 129, 247); // Primary color
        doc.text('BotV2 Dashboard Report', 20, 20);
        
        // Subtitle
        doc.setFontSize(12);
        doc.setTextColor(100);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);
        
        // Line separator
        doc.setDrawColor(48, 54, 61);
        doc.line(20, 35, 190, 35);
        
        // Summary metrics
        doc.setFontSize(14);
        doc.setTextColor(0);
        doc.text('Summary Metrics', 20, 45);
        
        const data = this.gatherExportData();
        const tableData = data.map(item => [item.metric, item.value]);
        
        doc.autoTable({
            startY: 50,
            head: [['Metric', 'Value']],
            body: tableData,
            theme: 'grid',
            headStyles: { 
                fillColor: [47, 129, 247],
                textColor: 255,
                fontStyle: 'bold'
            },
            styles: {
                fontSize: 10,
                cellPadding: 5
            },
            alternateRowStyles: {
                fillColor: [246, 248, 250]
            }
        });
        
        // Footer
        const pageCount = doc.internal.getNumberOfPages();
        for (let i = 1; i <= pageCount; i++) {
            doc.setPage(i);
            doc.setFontSize(8);
            doc.setTextColor(150);
            doc.text(
                `Page ${i} of ${pageCount}`,
                doc.internal.pageSize.width / 2,
                doc.internal.pageSize.height - 10,
                { align: 'center' }
            );
        }
        
        // Save
        const filename = `BotV2_Dashboard_${new Date().toISOString().split('T')[0]}.pdf`;
        doc.save(filename);
        
        Logger.export(`PDF export complete: ${filename}`);
        this.showExportSuccess('PDF', filename);
        
    } catch (error) {
        Logger.error('PDF export failed', error);
        this.showExportError('PDF', error.message);
    }
}
```

### Advanced PDF Features

#### Multi-Page Report with Charts

```javascript
async toPDFAdvanced() {
    try {
        this.showProgress('Generating PDF report...');
        
        const { jsPDF } = jspdf;
        const doc = new jsPDF();
        
        let currentY = 20;
        
        // ===== PAGE 1: OVERVIEW =====
        this.addPDFHeader(doc, 'Dashboard Overview', currentY);
        currentY += 20;
        
        // KPI Cards as table
        const kpiData = await this.fetchKPIData();
        doc.autoTable({
            startY: currentY,
            head: [['KPI', 'Current Value', 'Change', 'Status']],
            body: kpiData.map(kpi => [
                kpi.name,
                kpi.value,
                kpi.change,
                kpi.status
            ]),
            theme: 'striped',
            headStyles: { fillColor: [47, 129, 247] }
        });
        
        currentY = doc.lastAutoTable.finalY + 20;
        
        // ===== PAGE 2: PERFORMANCE =====
        doc.addPage();
        currentY = 20;
        this.addPDFHeader(doc, 'Performance Metrics', currentY);
        currentY += 20;
        
        const perfData = await this.fetchPerformanceData();
        doc.autoTable({
            startY: currentY,
            head: [['Date', 'Return (%)', 'Sharpe Ratio', 'Max Drawdown (%)']],
            body: perfData.map(p => [p.date, p.return, p.sharpe, p.maxDD]),
            theme: 'grid'
        });
        
        // Add chart as image (if available)
        const chartImage = await this.captureChartAsImage('equity-chart');
        if (chartImage) {
            currentY = doc.lastAutoTable.finalY + 10;
            doc.addImage(chartImage, 'PNG', 20, currentY, 170, 80);
        }
        
        // ===== PAGE 3: TRADES =====
        doc.addPage();
        currentY = 20;
        this.addPDFHeader(doc, 'Recent Trades', currentY);
        currentY += 20;
        
        const tradesData = await this.fetchRecentTrades();
        doc.autoTable({
            startY: currentY,
            head: [['Date', 'Symbol', 'Action', 'Size', 'Price', 'P&L']],
            body: tradesData.map(t => [
                t.date,
                t.symbol,
                t.action,
                t.size,
                `€${t.price}`,
                `€${t.pnl}`
            ]),
            theme: 'grid',
            columnStyles: {
                5: { 
                    cellPadding: { right: 5 },
                    halign: 'right',
                    fontStyle: 'bold'
                }
            },
            didParseCell: (data) => {
                // Color P&L based on value
                if (data.column.index === 5 && data.section === 'body') {
                    const value = parseFloat(data.cell.text[0].replace('€', ''));
                    if (value >= 0) {
                        data.cell.styles.textColor = [63, 185, 80]; // Green
                    } else {
                        data.cell.styles.textColor = [248, 81, 73]; // Red
                    }
                }
            }
        });
        
        // Add page numbers
        this.addPDFPageNumbers(doc);
        
        // Save
        const filename = `BotV2_Advanced_Report_${Date.now()}.pdf`;
        doc.save(filename);
        
        this.hideProgress();
        this.showExportSuccess('PDF', filename);
        
    } catch (error) {
        this.hideProgress();
        this.showExportError('PDF', error.message);
    }
}

addPDFHeader(doc, title, y) {
    doc.setFontSize(18);
    doc.setTextColor(47, 129, 247);
    doc.text(title, 20, y);
    doc.setDrawColor(48, 54, 61);
    doc.line(20, y + 5, 190, y + 5);
}

addPDFPageNumbers(doc) {
    const pageCount = doc.internal.getNumberOfPages();
    for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(150);
        doc.text(
            `BotV2 Dashboard | Page ${i} of ${pageCount} | Generated: ${new Date().toLocaleDateString()}`,
            doc.internal.pageSize.width / 2,
            doc.internal.pageSize.height - 10,
            { align: 'center' }
        );
    }
}

async captureChartAsImage(chartId) {
    try {
        const chartElement = document.getElementById(chartId);
        if (!chartElement) return null;
        
        // Using html2canvas (needs to be loaded)
        if (typeof html2canvas === 'undefined') {
            Logger.warn('html2canvas not loaded, skipping chart capture');
            return null;
        }
        
        const canvas = await html2canvas(chartElement);
        return canvas.toDataURL('image/png');
    } catch (error) {
        Logger.error('Failed to capture chart', error);
        return null;
    }
}
```

---

## 🔗 Integration with Dashboard v7.4

### Complete Integration Steps

#### Step 1: Update `dashboard.html`

```html
<!-- Add before closing </body> tag -->

<!-- Export Libraries -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>

<!-- Optional: For chart screenshots in PDF -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

<!-- Dashboard Scripts (existing) -->
<script src="{{ url_for('static', filename='js/performance-optimizer.js') }}"></script>
<script src="{{ url_for('static', filename='js/dashboard-optimized.js') }}"></script>
```

#### Step 2: Update `dashboard-optimized.js`

Replace the `ExportSystem` object completely:

```javascript
// ==================== EXPORT SYSTEM (COMPLETE) ====================
const ExportSystem = {
    execute() {
        const format = document.querySelector('input[name="exportFormat"]:checked')?.value || 'csv';
        Logger.export(`Exporting as ${format.toUpperCase()}`);
        
        switch(format) {
            case 'csv':
                this.toCSV();
                break;
            case 'excel':
                this.toExcel();
                break;
            case 'pdf':
                this.toPDF();
                break;
        }
        
        AppState.exportHistory.push({
            format,
            timestamp: new Date().toISOString()
        });
        StatePersistence.save();
        
        AnalyticsManager.track('data_exported', { format });
    },
    
    toCSV() {
        // ... (existing CSV implementation)
    },
    
    toExcel() {
        // ... (new Excel implementation from above)
    },
    
    toPDF() {
        // ... (new PDF implementation from above)
    },
    
    // Helper methods
    gatherExportData() {
        // ... (existing implementation)
    },
    
    getPerformanceMetrics() {
        // Fetch from API or AppState
        return [
            { Date: '2026-01-25', Return: '2.5%', Sharpe: '1.8', MaxDD: '-5.2%' },
            { Date: '2026-01-24', Return: '1.8%', Sharpe: '1.7', MaxDD: '-5.5%' }
        ];
    },
    
    getTradesData() {
        // Fetch from API or AppState
        return [
            { 
                Date: '2026-01-25', 
                Symbol: 'BTC', 
                Action: 'BUY', 
                Size: 0.5, 
                Price: 45000, 
                PnL: 1200 
            }
        ];
    },
    
    showExportSuccess(format, filename) {
        Logger.export(`${format} export successful: ${filename}`);
        AnalyticsManager.track('export_success', { format, filename });
        this.showToast(`✅ ${format} export successful`, 'success');
    },
    
    showExportError(format, message) {
        Logger.error(`${format} export failed`, message);
        ErrorTracker.track(`${format} export failed`, message);
        this.showToast(`❌ ${format} export failed`, 'error');
    },
    
    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `export-toast export-toast-${type}`;
        toast.innerHTML = `
            <div class="export-toast-icon">${type === 'success' ? '✅' : '❌'}</div>
            <div class="export-toast-message">${message}</div>
        `;
        toast.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#3fb950' : '#f85149'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            z-index: 10000;
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            animation: slideInRight 0.3s ease-out;
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },
    
    showProgress(message) {
        const progress = document.createElement('div');
        progress.id = 'export-progress';
        progress.innerHTML = `
            <div class="export-progress-spinner"></div>
            <div class="export-progress-message">${message}</div>
        `;
        progress.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: var(--bg-secondary);
            border: 1px solid var(--border-default);
            border-radius: 12px;
            padding: 32px 48px;
            box-shadow: var(--shadow-xl);
            z-index: 10001;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 16px;
        `;
        document.body.appendChild(progress);
    },
    
    hideProgress() {
        const progress = document.getElementById('export-progress');
        if (progress) progress.remove();
    },
    
    download(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    }
};
```

#### Step 3: Add CSS for Export UI

Add to `dashboard.html` `<style>` section:

```css
/* Export Toast Animations */
@keyframes slideInRight {
    from {
        transform: translateX(400px);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

@keyframes slideOutRight {
    from {
        transform: translateX(0);
        opacity: 1;
    }
    to {
        transform: translateX(400px);
        opacity: 0;
    }
}

.export-toast {
    font-family: var(--font-family);
}

.export-toast-icon {
    font-size: 24px;
}

.export-progress-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid var(--border-default);
    border-top-color: var(--accent-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.export-progress-message {
    color: var(--text-primary);
    font-weight: 600;
    font-size: 14px;
}
```

---

## 🚀 Advanced Features

### 1. Real-Time Data Fetching

```javascript
async fetchDashboardData() {
    try {
        const response = await fetch('/api/dashboard/export-data');
        if (!response.ok) throw new Error('Failed to fetch data');
        return await response.json();
    } catch (error) {
        Logger.error('Failed to fetch dashboard data', error);
        throw error;
    }
}
```

### 2. Custom Export Options

```javascript
showExportOptionsModal() {
    const options = `
        <div class="export-options">
            <h4>Export Options</h4>
            
            <div class="option-group">
                <label>Format:</label>
                <select id="exportFormat">
                    <option value="csv">CSV</option>
                    <option value="excel">Excel (.xlsx)</option>
                    <option value="pdf">PDF</option>
                </select>
            </div>
            
            <div class="option-group">
                <label>Date Range:</label>
                <input type="date" id="exportDateFrom">
                <span>to</span>
                <input type="date" id="exportDateTo">
            </div>
            
            <div class="option-group">
                <label>Include:</label>
                <label><input type="checkbox" checked> Summary</label>
                <label><input type="checkbox" checked> Performance</label>
                <label><input type="checkbox" checked> Trades</label>
                <label><input type="checkbox"> Risk Analysis</label>
                <label><input type="checkbox"> Charts (PDF only)</label>
            </div>
            
            <button onclick="DashboardApp.executeCustomExport()">Export</button>
        </div>
    `;
    
    DashboardApp.showModal('export-options', { content: options });
}
```

### 3. Scheduled Exports

```javascript
const ScheduledExports = {
    schedules: [],
    
    add(schedule) {
        this.schedules.push({
            id: Date.now(),
            format: schedule.format,
            frequency: schedule.frequency, // 'daily', 'weekly', 'monthly'
            time: schedule.time,
            enabled: true
        });
        this.save();
    },
    
    async execute(scheduleId) {
        const schedule = this.schedules.find(s => s.id === scheduleId);
        if (!schedule || !schedule.enabled) return;
        
        try {
            await ExportSystem[`to${schedule.format.toUpperCase()}`]();
            Logger.success(`Scheduled export executed: ${schedule.format}`);
        } catch (error) {
            Logger.error('Scheduled export failed', error);
        }
    },
    
    save() {
        localStorage.setItem('scheduled_exports', JSON.stringify(this.schedules));
    },
    
    load() {
        const saved = localStorage.getItem('scheduled_exports');
        if (saved) this.schedules = JSON.parse(saved);
    }
};
```

---

## ✨ Best Practices

### Performance

1. **Lazy Loading**: Load export libraries only when needed
```javascript
async loadExportLibraries() {
    if (!window.XLSX) {
        await this.loadScript('https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js');
    }
    if (!window.jspdf) {
        await this.loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js');
    }
}

loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = resolve;
        script.onerror = reject;
        document.head.appendChild(script);
    });
}
```

2. **Batch Processing**: Handle large datasets in chunks
```javascript
exportLargeDataset(data) {
    const chunkSize = 1000;
    const chunks = [];
    
    for (let i = 0; i < data.length; i += chunkSize) {
        chunks.push(data.slice(i, i + chunkSize));
    }
    
    // Process chunks with progress
    chunks.forEach((chunk, index) => {
        this.processChunk(chunk);
        this.updateProgress((index + 1) / chunks.length * 100);
    });
}
```

3. **Memory Management**: Clear large objects after export
```javascript
toExcel() {
    let workbook = XLSX.utils.book_new();
    // ... create sheets
    XLSX.writeFile(workbook, 'export.xlsx');
    workbook = null; // Help GC
}
```

### Error Handling

```javascript
async safeExport(exportFn, format) {
    const startTime = performance.now();
    
    try {
        await exportFn();
        
        const duration = performance.now() - startTime;
        Logger.perf.end('export', `${format} export completed in ${duration.toFixed(2)}ms`);
        
        AnalyticsManager.trackPerformance('export_success', {
            format,
            duration
        });
        
    } catch (error) {
        Logger.error(`${format} export failed`, error);
        
        ErrorTracker.track(`${format}_export_failed`, {
            error: error.message,
            stack: error.stack
        });
        
        // User-friendly error message
        this.showExportError(format, this.getUserFriendlyError(error));
    }
}

getUserFriendlyError(error) {
    if (error.message.includes('library not loaded')) {
        return 'Export library not available. Please refresh the page.';
    }
    if (error.message.includes('fetch')) {
        return 'Failed to fetch data. Check your connection.';
    }
    return 'An unexpected error occurred. Please try again.';
}
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Libraries Not Loading

**Problem**: `XLSX is not defined` or `jspdf is not defined`

**Solution**:
```javascript
// Check loading order in dashboard.html
// Must be BEFORE dashboard-optimized.js

// Verify in console:
console.log('XLSX:', typeof XLSX);
console.log('jspdf:', typeof jspdf);
```

#### 2. CORS Issues

**Problem**: Can't load external scripts

**Solution**: Use CDN or host locally
```bash
# Download and host locally
cd src/dashboard/static/js/vendor
wget https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js
wget https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js
```

#### 3. Large File Performance

**Problem**: Browser freezes on large exports

**Solution**: Use Web Workers
```javascript
// export-worker.js
self.onmessage = function(e) {
    const { data, format } = e.data;
    
    // Process export in background
    const result = processExport(data, format);
    
    self.postMessage({ result });
};

// In dashboard-optimized.js
const worker = new Worker('export-worker.js');
worker.postMessage({ data: exportData, format: 'excel' });
worker.onmessage = (e) => {
    downloadFile(e.data.result);
};
```

---

## 📚 Complete Examples

### Example 1: Full Dashboard Export

```javascript
async exportFullDashboard() {
    try {
        this.showProgress('Generating complete dashboard report...');
        
        // Fetch all data
        const [overview, performance, trades, risk] = await Promise.all([
            fetch('/api/dashboard/overview').then(r => r.json()),
            fetch('/api/dashboard/performance').then(r => r.json()),
            fetch('/api/dashboard/trades').then(r => r.json()),
            fetch('/api/dashboard/risk').then(r => r.json())
        ]);
        
        // Create Excel workbook
        const wb = XLSX.utils.book_new();
        
        // Add all sheets
        XLSX.utils.book_append_sheet(wb, 
            XLSX.utils.json_to_sheet(overview), 
            'Overview'
        );
        XLSX.utils.book_append_sheet(wb, 
            XLSX.utils.json_to_sheet(performance), 
            'Performance'
        );
        XLSX.utils.book_append_sheet(wb, 
            XLSX.utils.json_to_sheet(trades), 
            'Trades'
        );
        XLSX.utils.book_append_sheet(wb, 
            XLSX.utils.json_to_sheet(risk), 
            'Risk'
        );
        
        // Download
        XLSX.writeFile(wb, `BotV2_Full_Report_${Date.now()}.xlsx`);
        
        this.hideProgress();
        this.showExportSuccess('Excel', 'Full Dashboard Report');
        
    } catch (error) {
        this.hideProgress();
        this.showExportError('Excel', error.message);
    }
}
```

### Example 2: PDF with Custom Branding

```javascript
createBrandedPDF() {
    const { jsPDF } = jspdf;
    const doc = new jsPDF();
    
    // Add logo (base64 encoded)
    const logo = 'data:image/png;base64,...'; // Your logo
    doc.addImage(logo, 'PNG', 20, 10, 30, 30);
    
    // Company info
    doc.setFontSize(24);
    doc.setTextColor(47, 129, 247);
    doc.text('BotV2 Trading Platform', 60, 25);
    
    doc.setFontSize(12);
    doc.setTextColor(100);
    doc.text('Professional Algorithmic Trading Dashboard', 60, 33);
    
    // Report date
    doc.text(`Report Date: ${new Date().toLocaleDateString()}`, 20, 50);
    
    // Content...
    
    // Footer with branding
    doc.setFontSize(8);
    doc.text('BotV2 © 2026 | Confidential', 20, 285);
    
    doc.save('BotV2_Branded_Report.pdf');
}
```

---

## 🎯 Next Steps

1. **Implement backend endpoints** for real data:
   - `/api/dashboard/export-data`
   - `/api/dashboard/trades`
   - `/api/dashboard/performance`

2. **Add export scheduling** in dashboard UI

3. **Create export templates** for different report types

4. **Add email delivery** option for scheduled exports

5. **Implement export history** view in dashboard

---

## 📖 References

- [SheetJS Documentation](https://docs.sheetjs.com/)
- [jsPDF Documentation](https://artskydj.github.io/jsPDF/docs/)
- [jsPDF-AutoTable](https://github.com/simonbengtsson/jsPDF-AutoTable)
- [Dashboard v7.4 Architecture](./DASHBOARD_AUDIT_V7.3.md)

---

**Document Version**: 1.0.0  
**Last Updated**: January 25, 2026  
**Author**: Juan Carlos Garcia  
**Status**: ✅ Complete Integration Guide
