# 📥 Export Library Integration Guide

> **Complete guide for integrating professional export capabilities (CSV, Excel, PDF) into Dashboard v7.4**

---

## 📋 Table of Contents

- [Overview](#-overview)
- [CSV Export (Current)](#-csv-export-current)
- [Excel Export (SheetJS)](#-excel-export-sheetjs)
- [PDF Export (jsPDF)](#-pdf-export-jspdf)
- [Custom Export Templates](#-custom-export-templates)
- [Security Considerations](#-security-considerations)
- [Performance Optimization](#-performance-optimization)
- [Testing Exports](#-testing-exports)

---

## 🎯 Overview

Dashboard v7.4 includes a professional export system with support for:

| Format | Status | Library | Size | Use Case |
|--------|--------|---------|------|----------|
| **CSV** | ✅ Complete | Native JS | 0KB | Simple data exports |
| **Excel** | ⚠️ Ready for integration | SheetJS | ~400KB | Multi-sheet, formatted exports |
| **PDF** | ⚠️ Ready for integration | jsPDF + autoTable | ~200KB | Reports, presentations |

---

## 📝 CSV Export (Current)

### Implementation

CSV export is **already fully implemented** in Dashboard v7.4:

```javascript
// src/dashboard/static/js/dashboard-optimized.js (line 680-710)

toCSV() {
  const data = this.gatherExportData();
  let csv = '# BotV2 Dashboard Export\n';
  csv += `# Generated: ${new Date().toISOString()}\n\n`;
  
  // Convert data to CSV format
  if (Array.isArray(data)) {
    const headers = Object.keys(data[0]);
    csv += headers.join(',') + '\n';
    data.forEach(row => {
      csv += headers.map(h => row[h]).join(',') + '\n';
    });
  }
  
  this.download(csv, 'dashboard_export.csv', 'text/csv');
  Logger.export('CSV export complete');
}
```

### Usage

```javascript
// Open export modal
DashboardApp.showModal('export-options', {});

// User selects CSV format
// Click "Export" button
DashboardApp.executeExport();
// Downloads: dashboard_export.csv
```

### CSV Format Example

```csv
# BotV2 Dashboard Export
# Generated: 2025-01-25T20:30:00.000Z

metric,value
Total Return,45.2%
Sharpe Ratio,1.8
Max Drawdown,-12.3%
Win Rate,67.5%
Total Trades,234
```

### Advanced CSV Features

#### Custom Delimiter

```javascript
toCSV(delimiter = ',') {
  const data = this.gatherExportData();
  let csv = '# BotV2 Dashboard Export\n';
  csv += `# Generated: ${new Date().toISOString()}\n\n`;
  
  if (Array.isArray(data)) {
    const headers = Object.keys(data[0]);
    csv += headers.join(delimiter) + '\n';
    data.forEach(row => {
      csv += headers.map(h => this.escapeCSV(row[h], delimiter)).join(delimiter) + '\n';
    });
  }
  
  this.download(csv, 'dashboard_export.csv', 'text/csv');
}

escapeCSV(value, delimiter) {
  if (value === null || value === undefined) return '';
  
  const str = String(value);
  
  // Escape if contains delimiter, quotes, or newlines
  if (str.includes(delimiter) || str.includes('"') || str.includes('\n')) {
    return '"' + str.replace(/"/g, '""') + '"';
  }
  
  return str;
}
```

#### CSV with Multiple Sheets (as separate files)

```javascript
exportMultipleCSV() {
  const sheets = {
    'trades': this.getTradesData(),
    'performance': this.getPerformanceData(),
    'risk': this.getRiskData()
  };
  
  Object.entries(sheets).forEach(([name, data]) => {
    let csv = `# ${name.toUpperCase()}\n`;
    csv += `# Generated: ${new Date().toISOString()}\n\n`;
    
    const headers = Object.keys(data[0]);
    csv += headers.join(',') + '\n';
    data.forEach(row => {
      csv += headers.map(h => this.escapeCSV(row[h], ',')).join(',') + '\n';
    });
    
    this.download(csv, `dashboard_${name}_${Date.now()}.csv`, 'text/csv');
  });
}
```

---

## 📗 Excel Export (SheetJS)

### Installation

#### Option 1: CDN (Recommended for quick setup)

```html
<!-- Add to dashboard.html <head> -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
```

#### Option 2: NPM (Recommended for production)

```bash
npm install xlsx
```

### Basic Implementation

Add to `ExportSystem` in `dashboard-optimized.js`:

```javascript
toExcel() {
  if (typeof XLSX === 'undefined') {
    Logger.error('SheetJS library not loaded');
    alert('Excel export requires SheetJS library. Please contact administrator.');
    return;
  }
  
  Logger.export('Exporting to Excel...');
  
  // Create workbook
  const wb = XLSX.utils.book_new();
  
  // Add metadata
  wb.Props = {
    Title: 'BotV2 Dashboard Export',
    Subject: 'Trading Dashboard Data',
    Author: 'BotV2',
    CreatedDate: new Date()
  };
  
  // Get data
  const data = this.gatherExportData();
  
  // Convert to worksheet
  const ws = XLSX.utils.json_to_sheet(data);
  
  // Add to workbook
  XLSX.utils.book_append_sheet(wb, ws, 'Dashboard');
  
  // Generate Excel file
  XLSX.writeFile(wb, `dashboard_export_${Date.now()}.xlsx`);
  
  Logger.export('Excel export complete');
}
```

### Advanced Excel Export

#### Multi-Sheet Workbook

```javascript
toExcelAdvanced() {
  const wb = XLSX.utils.book_new();
  
  // Metadata
  wb.Props = {
    Title: 'BotV2 Dashboard Export',
    Subject: 'Complete Trading Analysis',
    Author: 'BotV2',
    CreatedDate: new Date()
  };
  
  // Sheet 1: Summary
  const summaryData = [
    { Metric: 'Total Return', Value: '45.2%' },
    { Metric: 'Sharpe Ratio', Value: 1.8 },
    { Metric: 'Max Drawdown', Value: '-12.3%' },
    { Metric: 'Win Rate', Value: '67.5%' },
    { Metric: 'Total Trades', Value: 234 }
  ];
  const wsSummary = XLSX.utils.json_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');
  
  // Sheet 2: Trades
  const tradesData = this.getTradesData();
  const wsTrades = XLSX.utils.json_to_sheet(tradesData);
  XLSX.utils.book_append_sheet(wb, wsTrades, 'Trades');
  
  // Sheet 3: Performance
  const performanceData = this.getPerformanceData();
  const wsPerformance = XLSX.utils.json_to_sheet(performanceData);
  XLSX.utils.book_append_sheet(wb, wsPerformance, 'Performance');
  
  // Sheet 4: Risk Metrics
  const riskData = this.getRiskData();
  const wsRisk = XLSX.utils.json_to_sheet(riskData);
  XLSX.utils.book_append_sheet(wb, wsRisk, 'Risk Analysis');
  
  // Generate file
  XLSX.writeFile(wb, `botv2_complete_export_${Date.now()}.xlsx`);
  
  Logger.export('Advanced Excel export complete with 4 sheets');
}
```

#### Formatted Excel with Styles

```javascript
toExcelStyled() {
  const wb = XLSX.utils.book_new();
  
  // Create data with formatting
  const data = this.gatherExportData();
  const ws = XLSX.utils.json_to_sheet(data);
  
  // Define column widths
  ws['!cols'] = [
    { wch: 20 }, // Column A
    { wch: 15 }, // Column B
    { wch: 15 }, // Column C
    { wch: 20 }  // Column D
  ];
  
  // Freeze first row (headers)
  ws['!freeze'] = { xSplit: 0, ySplit: 1 };
  
  // Auto-filter on headers
  const range = XLSX.utils.decode_range(ws['!ref']);
  ws['!autofilter'] = { ref: XLSX.utils.encode_range(range) };
  
  // Cell styles (requires xlsx-style or similar plugin)
  // Note: Basic xlsx doesn't support full styling
  // For advanced styling, use xlsx-js-style or SheetJS Pro
  
  XLSX.utils.book_append_sheet(wb, ws, 'Styled Data');
  XLSX.writeFile(wb, `styled_export_${Date.now()}.xlsx`);
}
```

#### Export Chart Data to Excel

```javascript
exportChartToExcel(chartId) {
  // Get chart data from Plotly
  const chartDiv = document.getElementById(chartId);
  if (!chartDiv || !chartDiv.data) {
    Logger.error('Chart not found or has no data');
    return;
  }
  
  const wb = XLSX.utils.book_new();
  
  // Convert each trace to a sheet
  chartDiv.data.forEach((trace, index) => {
    const sheetData = trace.x.map((x, i) => ({
      X: x,
      Y: trace.y[i],
      Name: trace.name || `Trace ${index + 1}`
    }));
    
    const ws = XLSX.utils.json_to_sheet(sheetData);
    XLSX.utils.book_append_sheet(wb, ws, trace.name || `Trace ${index + 1}`);
  });
  
  XLSX.writeFile(wb, `chart_${chartId}_${Date.now()}.xlsx`);
  Logger.export(`Chart ${chartId} exported to Excel`);
}
```

### Integration into Dashboard

```javascript
// Update toExcel() method in ExportSystem (line 712)
toExcel() {
  if (typeof XLSX === 'undefined') {
    Logger.error('Excel export requires SheetJS library');
    alert('Please install SheetJS to enable Excel exports.');
    return;
  }
  
  Logger.export('Exporting to Excel with multiple sheets...');
  
  const wb = XLSX.utils.book_new();
  
  wb.Props = {
    Title: 'BotV2 Dashboard Export',
    Subject: 'Trading Dashboard Data',
    Author: 'BotV2',
    CreatedDate: new Date()
  };
  
  // Summary sheet
  const summaryData = this.gatherExportData();
  const wsSummary = XLSX.utils.json_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(wb, wsSummary, 'Summary');
  
  // Trades sheet (if available)
  if (typeof this.getTradesData === 'function') {
    const tradesData = this.getTradesData();
    const wsTrades = XLSX.utils.json_to_sheet(tradesData);
    XLSX.utils.book_append_sheet(wb, wsTrades, 'Trades');
  }
  
  // Performance sheet (if available)
  if (typeof this.getPerformanceData === 'function') {
    const perfData = this.getPerformanceData();
    const wsPerf = XLSX.utils.json_to_sheet(perfData);
    XLSX.utils.book_append_sheet(wb, wsPerf, 'Performance');
  }
  
  XLSX.writeFile(wb, `botv2_export_${Date.now()}.xlsx`);
  
  Logger.export('Excel export complete');
}
```

---

## 📝 PDF Export (jsPDF)

### Installation

#### Option 1: CDN

```html
<!-- Add to dashboard.html <head> -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.31/jspdf.plugin.autotable.min.js"></script>
```

#### Option 2: NPM

```bash
npm install jspdf jspdf-autotable
```

### Basic Implementation

```javascript
toPDF() {
  if (typeof jspdf === 'undefined' && typeof jsPDF === 'undefined') {
    Logger.error('jsPDF library not loaded');
    alert('PDF export requires jsPDF library. Please contact administrator.');
    return;
  }
  
  Logger.export('Exporting to PDF...');
  
  // Create PDF (A4 size)
  const { jsPDF } = window.jspdf || window;
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text('BotV2 Dashboard Export', 14, 20);
  
  // Subtitle
  doc.setFontSize(10);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);
  
  // Data
  const data = this.gatherExportData();
  
  // Convert to table format
  const tableData = data.map(row => Object.values(row));
  const tableHeaders = [Object.keys(data[0])];
  
  // Add table
  doc.autoTable({
    head: tableHeaders,
    body: tableData,
    startY: 35,
    theme: 'grid',
    headStyles: { fillColor: [47, 129, 247] }, // BotV2 blue
    styles: { fontSize: 9 }
  });
  
  // Save
  doc.save(`dashboard_export_${Date.now()}.pdf`);
  
  Logger.export('PDF export complete');
}
```

### Advanced PDF Export

#### Multi-Page PDF Report

```javascript
toPDFAdvanced() {
  const { jsPDF } = window.jspdf || window;
  const doc = new jsPDF();
  
  // Page 1: Cover
  this.addCoverPage(doc);
  
  // Page 2: Summary
  doc.addPage();
  this.addSummaryPage(doc);
  
  // Page 3: Trades
  doc.addPage();
  this.addTradesPage(doc);
  
  // Page 4: Performance Charts
  doc.addPage();
  this.addChartsPage(doc);
  
  // Save
  doc.save(`botv2_report_${Date.now()}.pdf`);
  Logger.export('Advanced PDF report generated');
}

addCoverPage(doc) {
  // Logo (if available)
  // doc.addImage(logoBase64, 'PNG', 80, 40, 50, 50);
  
  // Title
  doc.setFontSize(28);
  doc.setFont('helvetica', 'bold');
  doc.text('BotV2 Trading Dashboard', 105, 100, { align: 'center' });
  
  // Subtitle
  doc.setFontSize(16);
  doc.setFont('helvetica', 'normal');
  doc.text('Complete Performance Report', 105, 110, { align: 'center' });
  
  // Date
  doc.setFontSize(12);
  doc.text(`Report Date: ${new Date().toLocaleDateString()}`, 105, 130, { align: 'center' });
  
  // Footer
  doc.setFontSize(10);
  doc.setTextColor(150);
  doc.text('Private & Confidential', 105, 280, { align: 'center' });
}

addSummaryPage(doc) {
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Performance Summary', 14, 20);
  
  // Key metrics table
  const summaryData = [
    ['Total Return', '45.2%'],
    ['Sharpe Ratio', '1.8'],
    ['Max Drawdown', '-12.3%'],
    ['Win Rate', '67.5%'],
    ['Total Trades', '234'],
    ['Average Trade', '€1,245']
  ];
  
  doc.autoTable({
    head: [['Metric', 'Value']],
    body: summaryData,
    startY: 30,
    theme: 'striped',
    headStyles: { fillColor: [47, 129, 247] }
  });
  
  // Footer with page number
  doc.setFontSize(10);
  doc.text('Page 2', 105, 285, { align: 'center' });
}

addTradesPage(doc) {
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Recent Trades', 14, 20);
  
  const tradesData = this.getTradesData() || [];
  const tableData = tradesData.slice(0, 20).map(trade => [
    trade.date,
    trade.symbol,
    trade.action,
    trade.size,
    trade.price,
    trade.pnl
  ]);
  
  doc.autoTable({
    head: [['Date', 'Symbol', 'Action', 'Size', 'Price', 'P&L']],
    body: tableData,
    startY: 30,
    theme: 'grid',
    headStyles: { fillColor: [47, 129, 247] },
    styles: { fontSize: 8 },
    columnStyles: {
      5: { halign: 'right' } // Align P&L to right
    }
  });
  
  doc.setFontSize(10);
  doc.text('Page 3', 105, 285, { align: 'center' });
}

addChartsPage(doc) {
  doc.setFontSize(18);
  doc.setFont('helvetica', 'bold');
  doc.text('Performance Charts', 14, 20);
  
  // Export chart as image
  const chartDiv = document.getElementById('equity-container');
  if (chartDiv) {
    Plotly.toImage(chartDiv, { format: 'png', width: 800, height: 400 })
      .then(imgData => {
        doc.addImage(imgData, 'PNG', 14, 30, 180, 90);
        doc.setFontSize(10);
        doc.text('Page 4', 105, 285, { align: 'center' });
      });
  }
}
```

#### PDF with Charts

```javascript
async exportPDFWithCharts() {
  const { jsPDF } = window.jspdf || window;
  const doc = new jsPDF();
  
  // Title
  doc.setFontSize(20);
  doc.text('BotV2 Dashboard Report', 14, 20);
  
  // Export Plotly chart to image
  const chartDiv = document.getElementById('equity-container');
  
  if (chartDiv && window.Plotly) {
    try {
      const imgData = await Plotly.toImage(chartDiv, {
        format: 'png',
        width: 800,
        height: 400
      });
      
      // Add chart image to PDF
      doc.addImage(imgData, 'PNG', 14, 30, 180, 90);
      
      // Add data table below chart
      const data = this.gatherExportData();
      doc.autoTable({
        head: [Object.keys(data[0])],
        body: data.map(row => Object.values(row)),
        startY: 130,
        theme: 'striped'
      });
      
      doc.save(`report_with_charts_${Date.now()}.pdf`);
      Logger.export('PDF with charts exported');
    } catch (error) {
      Logger.error('Failed to export chart to PDF', error);
    }
  }
}
```

### Integration into Dashboard

```javascript
// Update toPDF() method in ExportSystem (line 716)
toPDF() {
  if (typeof jspdf === 'undefined' && typeof jsPDF === 'undefined') {
    Logger.error('PDF export requires jsPDF library');
    alert('Please install jsPDF to enable PDF exports.');
    return;
  }
  
  Logger.export('Generating PDF report...');
  
  const { jsPDF } = window.jspdf || window;
  const doc = new jsPDF();
  
  // Title page
  doc.setFontSize(24);
  doc.setFont('helvetica', 'bold');
  doc.text('BotV2 Dashboard Report', 105, 60, { align: 'center' });
  
  doc.setFontSize(12);
  doc.setFont('helvetica', 'normal');
  doc.text(`Generated: ${new Date().toLocaleString()}`, 105, 70, { align: 'center' });
  
  // Summary data
  const data = this.gatherExportData();
  
  doc.autoTable({
    head: [Object.keys(data[0])],
    body: data.map(row => Object.values(row)),
    startY: 90,
    theme: 'grid',
    headStyles: { 
      fillColor: [47, 129, 247],
      fontSize: 11,
      fontStyle: 'bold'
    },
    bodyStyles: {
      fontSize: 10
    },
    alternateRowStyles: {
      fillColor: [245, 245, 245]
    }
  });
  
  // Footer
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(10);
    doc.setTextColor(150);
    doc.text(
      `Page ${i} of ${pageCount} - BotV2 Dashboard`,
      105,
      285,
      { align: 'center' }
    );
  }
  
  doc.save(`botv2_report_${Date.now()}.pdf`);
  
  Logger.export('PDF export complete');
}
```

---

## 🎭 Custom Export Templates

### Create Export Template System

```javascript
// Add to ExportSystem
const ExportTemplates = {
  // Daily Summary Template
  dailySummary: {
    name: 'Daily Summary',
    format: 'excel',
    sheets: [
      {
        name: 'Overview',
        data: () => ({
          date: new Date().toISOString(),
          totalReturn: '45.2%',
          dailyPnL: '+€2,450',
          openPositions: 12,
          closedTrades: 5
        })
      },
      {
        name: 'Trades',
        data: () => this.getTradesData()
      }
    ]
  },
  
  // Monthly Report Template
  monthlyReport: {
    name: 'Monthly Report',
    format: 'pdf',
    sections: [
      { type: 'cover', title: 'Monthly Performance Report' },
      { type: 'summary', data: () => this.getMonthlyMetrics() },
      { type: 'charts', charts: ['equity-curve', 'drawdown'] },
      { type: 'trades', data: () => this.getMonthlyTrades() }
    ]
  },
  
  // Risk Report Template
  riskReport: {
    name: 'Risk Analysis Report',
    format: 'pdf',
    sections: [
      { type: 'cover', title: 'Risk Analysis Report' },
      { type: 'var', data: () => this.getVaRMetrics() },
      { type: 'stress_tests', data: () => this.getStressTests() },
      { type: 'correlations', data: () => this.getCorrelations() }
    ]
  }
};

// Export using template
exportWithTemplate(templateName) {
  const template = ExportTemplates[templateName];
  
  if (!template) {
    Logger.error(`Template not found: ${templateName}`);
    return;
  }
  
  Logger.export(`Exporting with template: ${template.name}`);
  
  switch(template.format) {
    case 'excel':
      this.exportExcelTemplate(template);
      break;
    case 'pdf':
      this.exportPDFTemplate(template);
      break;
    case 'csv':
      this.exportCSVTemplate(template);
      break;
  }
}
```

---

## 🔒 Security Considerations

### Data Sanitization

```javascript
// Sanitize data before export
sanitizeForExport(data) {
  return data.map(row => {
    const sanitized = {};
    
    Object.entries(row).forEach(([key, value]) => {
      // Remove sensitive fields
      if (['password', 'api_key', 'secret'].includes(key)) {
        return;
      }
      
      // Sanitize HTML
      if (typeof value === 'string') {
        sanitized[key] = this.stripHTML(value);
      } else {
        sanitized[key] = value;
      }
    });
    
    return sanitized;
  });
}

stripHTML(html) {
  const tmp = document.createElement('div');
  tmp.textContent = html;
  return tmp.innerHTML;
}
```

### Access Control

```javascript
// Check export permissions
canExport() {
  // Implement your authorization logic
  const user = getCurrentUser();
  
  if (!user.permissions.includes('export')) {
    Logger.warn('User does not have export permission');
    alert('You do not have permission to export data.');
    return false;
  }
  
  return true;
}

executeExport() {
  if (!this.canExport()) return;
  
  // Continue with export...
}
```

### Watermarking PDFs

```javascript
addWatermark(doc) {
  const pageCount = doc.internal.getNumberOfPages();
  
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    
    // Semi-transparent watermark
    doc.setTextColor(200, 200, 200);
    doc.setFontSize(60);
    doc.text('CONFIDENTIAL', 105, 150, {
      align: 'center',
      angle: 45
    });
  }
}
```

---

## ⚡ Performance Optimization

### Large Dataset Handling

```javascript
// Paginate large exports
exportLargeDataset(data, chunkSize = 1000) {
  const chunks = [];
  
  for (let i = 0; i < data.length; i += chunkSize) {
    chunks.push(data.slice(i, i + chunkSize));
  }
  
  Logger.export(`Exporting ${chunks.length} chunks of ${chunkSize} rows each`);
  
  chunks.forEach((chunk, index) => {
    const csv = this.generateCSV(chunk);
    this.download(csv, `export_part_${index + 1}_of_${chunks.length}.csv`, 'text/csv');
  });
}
```

### Async Export with Progress

```javascript
async exportWithProgress(data) {
  const progressBar = document.getElementById('export-progress');
  const progressText = document.getElementById('export-progress-text');
  
  progressBar.style.display = 'block';
  
  try {
    // Step 1: Gather data
    progressText.textContent = 'Gathering data...';
    progressBar.value = 25;
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Step 2: Format data
    progressText.textContent = 'Formatting data...';
    progressBar.value = 50;
    const formatted = await this.formatData(data);
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Step 3: Generate file
    progressText.textContent = 'Generating file...';
    progressBar.value = 75;
    const file = await this.generateFile(formatted);
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Step 4: Download
    progressText.textContent = 'Downloading...';
    progressBar.value = 100;
    this.download(file, 'export.csv', 'text/csv');
    
    // Success
    setTimeout(() => {
      progressBar.style.display = 'none';
      progressText.textContent = '';
    }, 500);
  } catch (error) {
    Logger.error('Export failed', error);
    progressBar.style.display = 'none';
  }
}
```

---

## 🧪 Testing Exports

### Unit Tests

```javascript
describe('Export System', () => {
  
  test('CSV export generates valid CSV', () => {
    const data = [
      { metric: 'Return', value: '45.2%' },
      { metric: 'Sharpe', value: '1.8' }
    ];
    
    const csv = ExportSystem.generateCSV(data);
    
    expect(csv).toContain('metric,value');
    expect(csv).toContain('Return,45.2%');
    expect(csv).toContain('Sharpe,1.8');
  });
  
  test('Excel export creates workbook', () => {
    const data = [{ a: 1, b: 2 }];
    
    const wb = ExportSystem.createExcelWorkbook(data);
    
    expect(wb.SheetNames).toContain('Summary');
    expect(wb.Sheets['Summary']).toBeDefined();
  });
  
  test('PDF export creates document', () => {
    const data = [{ a: 1, b: 2 }];
    
    const doc = ExportSystem.createPDF(data);
    
    expect(doc.internal.getNumberOfPages()).toBeGreaterThan(0);
  });
  
});
```

---

**📥 Export Library Integration Complete**

For questions or issues, contact: juanca755@hotmail.com
