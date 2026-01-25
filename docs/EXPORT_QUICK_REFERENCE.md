# ⚡ Export Quick Reference - Dashboard v7.4

**One-page reference for implementing Excel and PDF exports**

---

## 🚀 Quick Start (5 Minutes)

### 1. Add Scripts to dashboard.html

**Location**: Before closing `</body>` tag

```html
<!-- Export Libraries -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
```

### 2. Verify Loading (Browser Console)

```javascript
console.log('XLSX:', typeof XLSX !== 'undefined');
console.log('jsPDF:', typeof jspdf !== 'undefined');
// Both should return: true
```

### 3. Test Exports

- Press `Ctrl+E` or click Export button
- Select format: CSV / Excel / PDF
- Click "Execute Export"
- Verify file downloads

---

## 📋 Code Snippets

### Excel Export (Copy-Paste)

**Replace `toExcel()` in `dashboard-optimized.js`:**

```javascript
toExcel() {
    Logger.export('Exporting to Excel...');
    
    try {
        if (typeof XLSX === 'undefined') {
            throw new Error('SheetJS library not loaded');
        }
        
        const data = this.gatherExportData();
        const wb = XLSX.utils.book_new();
        
        // Create sheet
        const summaryData = [
            ['BotV2 Dashboard Export'],
            ['Generated:', new Date().toISOString()],
            [''],
            ['Metric', 'Value'],
            ...data.map(item => [item.metric, item.value])
        ];
        const ws = XLSX.utils.aoa_to_sheet(summaryData);
        ws['!cols'] = [{ wch: 30 }, { wch: 20 }];
        XLSX.utils.book_append_sheet(wb, ws, 'Summary');
        
        // Download
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

### PDF Export (Copy-Paste)

**Replace `toPDF()` in `dashboard-optimized.js`:**

```javascript
toPDF() {
    Logger.export('Exporting to PDF...');
    
    try {
        if (typeof jspdf === 'undefined') {
            throw new Error('jsPDF library not loaded');
        }
        
        const { jsPDF } = jspdf;
        const doc = new jsPDF();
        
        // Header
        doc.setFontSize(20);
        doc.setTextColor(47, 129, 247);
        doc.text('BotV2 Dashboard Report', 20, 20);
        
        doc.setFontSize(12);
        doc.setTextColor(100);
        doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 30);
        
        doc.setDrawColor(48, 54, 61);
        doc.line(20, 35, 190, 35);
        
        // Table
        doc.setFontSize(14);
        doc.setTextColor(0);
        doc.text('Summary Metrics', 20, 45);
        
        const data = this.gatherExportData();
        doc.autoTable({
            startY: 50,
            head: [['Metric', 'Value']],
            body: data.map(item => [item.metric, item.value]),
            theme: 'grid',
            headStyles: { 
                fillColor: [47, 129, 247],
                textColor: 255,
                fontStyle: 'bold'
            },
            alternateRowStyles: { fillColor: [246, 248, 250] }
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

### Helper Methods (Add to ExportSystem)

```javascript
showExportSuccess(format, filename) {
    Logger.export(`${format} export successful: ${filename}`);
    if (typeof AnalyticsManager !== 'undefined') {
        AnalyticsManager.track('export_success', { format, filename });
    }
    this.showToast(`✅ ${format} export successful`, 'success');
},

showExportError(format, message) {
    Logger.error(`${format} export failed`, message);
    if (typeof ErrorTracker !== 'undefined') {
        ErrorTracker.track(`${format} export failed`, message);
    }
    this.showToast(`❌ ${format} export failed`, 'error');
},

showToast(message, type) {
    const toast = document.createElement('div');
    toast.textContent = message;
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
        font-weight: 600;
        animation: slideInRight 0.3s ease-out;
    `;
    document.body.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
```

### CSS Animations (Add to dashboard.html)

```css
/* Add to <style> section */
@keyframes slideInRight {
    from { transform: translateX(400px); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(400px); opacity: 0; }
}
```

---

## 🧪 Testing Commands

### Console Verification

```javascript
// Check library versions
console.log('XLSX version:', XLSX.version);
console.log('jsPDF version:', new jspdf.jsPDF().version);

// Check DashboardApp
console.log('Dashboard version:', DashboardApp.version);
console.log('ExportSystem:', typeof ExportSystem);

// Test error handling
delete window.XLSX;  // Then try Excel export
delete window.jspdf; // Then try PDF export
```

### Performance Testing

```javascript
// Measure export time
console.time('export');
// Execute export
console.timeEnd('export');
// Should be < 2 seconds
```

### Memory Testing

```javascript
// Before export
console.log('Memory before:', performance.memory?.usedJSHeapSize);

// Execute export

// After export
console.log('Memory after:', performance.memory?.usedJSHeapSize);
```

---

## 🔧 Common Issues & Solutions

### Issue: "XLSX is not defined"

**Solution**:
```html
<!-- Verify script order in dashboard.html -->
<!-- Libraries MUST come BEFORE dashboard-optimized.js -->
<script src="XLSX_CDN"></script>
<script src="jsPDF_CDN"></script>
<script src="dashboard-optimized.js"></script>
```

### Issue: Download doesn't start

**Solution**:
```javascript
// Check browser console for errors
// Check popup blocker settings
// Try manual trigger:
const link = document.createElement('a');
link.href = URL.createObjectURL(blob);
link.download = 'filename.xlsx';
link.click();
```

### Issue: Excel file corrupted

**Solution**:
```javascript
// Ensure proper data format
const data = [
    ['String', 'Number', 'Date'],
    ['Text', 123, new Date()]
];
// Avoid: null, undefined, circular references
```

### Issue: PDF layout broken

**Solution**:
```javascript
// Use doc.lastAutoTable.finalY for positioning
let currentY = 50;
doc.autoTable({ startY: currentY, /* ... */ });
currentY = doc.lastAutoTable.finalY + 10;
doc.text('Next section', 20, currentY);
```

---

## 📊 Advanced Features

### Multi-Sheet Excel

```javascript
const wb = XLSX.utils.book_new();

// Sheet 1
const ws1 = XLSX.utils.json_to_sheet(data1);
XLSX.utils.book_append_sheet(wb, ws1, 'Overview');

// Sheet 2
const ws2 = XLSX.utils.json_to_sheet(data2);
XLSX.utils.book_append_sheet(wb, ws2, 'Details');

XLSX.writeFile(wb, 'report.xlsx');
```

### Multi-Page PDF

```javascript
const doc = new jsPDF();

// Page 1
doc.text('Page 1 Title', 20, 20);
doc.autoTable({ /* ... */ });

// Page 2
doc.addPage();
doc.text('Page 2 Title', 20, 20);
doc.autoTable({ /* ... */ });

doc.save('report.pdf');
```

### Styled Cells (Excel)

```javascript
const ws = XLSX.utils.aoa_to_sheet(data);

// Column widths
ws['!cols'] = [
    { wch: 20 },  // Column A
    { wch: 15 },  // Column B
    { wch: 30 }   // Column C
];

// Row heights
ws['!rows'] = [
    { hpt: 30 }   // Row 1 height
];

// Merge cells
ws['!merges'] = [
    { s: { r: 0, c: 0 }, e: { r: 0, c: 2 } }  // Merge A1:C1
];
```

### Colored Tables (PDF)

```javascript
doc.autoTable({
    head: [['Name', 'Value', 'Status']],
    body: data,
    didParseCell: (data) => {
        // Color based on value
        if (data.column.index === 2 && data.section === 'body') {
            const value = data.cell.text[0];
            if (value === 'Success') {
                data.cell.styles.textColor = [63, 185, 80]; // Green
            } else if (value === 'Error') {
                data.cell.styles.textColor = [248, 81, 73]; // Red
            }
        }
    }
});
```

---

## 📝 Git Commands

### Implementation

```bash
# Create feature branch
git checkout -b feature/export-integration

# Make changes
# ...

# Commit
git add .
git commit -m "feat: Add Excel and PDF export functionality"

# Push
git push origin feature/export-integration
```

### Deployment

```bash
# Merge to main
git checkout main
git merge feature/export-integration
git push origin main

# Tag release
git tag -a v7.4.1 -m "feat: Excel and PDF exports"
git push origin v7.4.1
```

### Rollback

```bash
# Revert last commit
git revert HEAD
git push origin main

# Or restore from backup
cp dashboard.html.backup dashboard.html
cp dashboard-optimized.js.backup dashboard-optimized.js
```

---

## 🎯 Success Checklist

- [ ] Libraries loaded (check console)
- [ ] CSV export works
- [ ] Excel export works
- [ ] PDF export works
- [ ] Toast notifications show
- [ ] No console errors
- [ ] Files download correctly
- [ ] Files open without corruption
- [ ] Cross-browser tested
- [ ] Performance < 2 seconds
- [ ] Error handling works
- [ ] Analytics tracking works

---

## 📚 Documentation

### Full Guides
- [Export Library Integration Guide](./EXPORT_LIBRARY_INTEGRATION_GUIDE.md)
- [Export Integration Checklist](./EXPORT_INTEGRATION_CHECKLIST.md)
- [Dashboard v7.4 Audit](./DASHBOARD_AUDIT_V7.3.md)

### External Links
- [SheetJS Docs](https://docs.sheetjs.com/)
- [jsPDF Docs](https://artskydj.github.io/jsPDF/docs/)
- [jsPDF-AutoTable](https://github.com/simonbengtsson/jsPDF-AutoTable)

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Add CDN scripts | 5 min |
| Replace toExcel() | 15 min |
| Replace toPDF() | 15 min |
| Add helper methods | 10 min |
| Add CSS animations | 5 min |
| Testing | 30 min |
| **Total** | **~1.5 hours** |

---

## 🚀 Next Steps

### Immediate (Do Now)
1. Add CDN scripts to dashboard.html
2. Replace toExcel() and toPDF() methods
3. Test all export formats

### Short-term (This Week)
1. Add multi-sheet Excel support
2. Add chart screenshots to PDF
3. Implement progress indicators

### Long-term (Next Sprint)
1. Backend API for real data
2. Scheduled exports
3. Export history tracking
4. Custom templates

---

**Document Version**: 1.0.0  
**Last Updated**: January 25, 2026  
**Format**: Quick Reference / Cheatsheet
