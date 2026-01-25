// ==================== ExportLibrary v1.0 - Professional Data Export ====================
// 📥 Complete export system for CSV, Excel, PDF
// 🎯 Integration with Dashboard v7.4
// 📦 Dependencies: SheetJS (xlsx), jsPDF, jsPDF-AutoTable
// Author: Juan Carlos Garcia
// Date: 25-01-2026
// Version: 1.0.0

'use strict';

// ==================== DISPLAY BANNER ====================
(function showBanner() {
    console.log(
        '%c📥 ExportLibrary v1.0 ',
        'background:#8338ec;color:white;padding:4px 12px;border-radius:4px;font-weight:600',
        '- Professional data export system loaded'
    );
})();

// ==================== EXPORT LIBRARY ====================
window.ExportLibrary = (() => {
    
    // Configuration
    const CONFIG = {
        maxRowsCSV: 1000000,
        maxRowsExcel: 100000,
        maxRowsPDF: 10000,
        chunkSize: 1000,
        dateFormat: 'YYYY-MM-DD HH:mm:ss',
        timezone: 'Europe/Madrid'
    };
    
    // State
    const state = {
        exporting: false,
        currentExport: null,
        history: []
    };
    
    // ==================== LOGGER ====================
    const Logger = {
        info: (msg) => console.log(`%c[EXPORT]%c ℹ️ ${msg}`, 'background:#8338ec;color:white;padding:2px 8px;border-radius:3px;font-weight:600', 'color:#7d8590'),
        success: (msg) => console.log(`%c[EXPORT]%c ✅ ${msg}`, 'background:#3fb950;color:white;padding:2px 8px;border-radius:3px;font-weight:600', 'color:#7d8590'),
        error: (msg, err) => {
            console.error(`%c[EXPORT]%c ❌ ${msg}`, 'background:#f85149;color:white;padding:2px 8px;border-radius:3px;font-weight:600', 'color:#7d8590');
            if (err) console.error(err);
        },
        progress: (msg, percent) => console.log(`%c[EXPORT]%c 📊 ${msg} (${percent}%)`, 'background:#8338ec;color:white;padding:2px 8px;border-radius:3px;font-weight:600', 'color:#7d8590')
    };
    
    // ==================== UTILITIES ====================
    
    /**
     * Format date according to config
     */
    function formatDate(date) {
        if (!date) return '';
        const d = new Date(date);
        const year = d.getFullYear();
        const month = String(d.getMonth() + 1).padStart(2, '0');
        const day = String(d.getDate()).padStart(2, '0');
        const hours = String(d.getHours()).padStart(2, '0');
        const minutes = String(d.getMinutes()).padStart(2, '0');
        const seconds = String(d.getSeconds()).padStart(2, '0');
        return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
    }
    
    /**
     * Format number with locale
     */
    function formatNumber(num, decimals = 2) {
        if (typeof num !== 'number') return num;
        return num.toLocaleString('es-ES', { 
            minimumFractionDigits: decimals, 
            maximumFractionDigits: decimals 
        });
    }
    
    /**
     * Escape CSV field
     */
    function escapeCSV(field) {
        if (field === null || field === undefined) return '';
        const str = String(field);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            return '"' + str.replace(/"/g, '""') + '"';
        }
        return str;
    }
    
    /**
     * Download file to browser
     */
    function downloadFile(content, filename, mimeType) {
        try {
            const blob = new Blob([content], { type: mimeType });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = filename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            Logger.success(`File downloaded: ${filename}`);
        } catch (error) {
            Logger.error('Download failed', error);
            throw error;
        }
    }
    
    /**
     * Show progress indicator
     */
    function showProgress(message, percent) {
        Logger.progress(message, percent);
        
        // Update UI if progress element exists
        const progressEl = document.getElementById('export-progress');
        if (progressEl) {
            progressEl.style.display = 'block';
            progressEl.querySelector('.progress-bar').style.width = `${percent}%`;
            progressEl.querySelector('.progress-text').textContent = `${message} ${percent}%`;
        }
    }
    
    /**
     * Hide progress indicator
     */
    function hideProgress() {
        const progressEl = document.getElementById('export-progress');
        if (progressEl) {
            progressEl.style.display = 'none';
        }
    }
    
    // ==================== CSV EXPORT ====================
    
    /**
     * Export data to CSV format
     * @param {Array} data - Array of objects
     * @param {Object} options - Export options
     */
    function toCSV(data, options = {}) {
        Logger.info('Starting CSV export...');
        
        const {
            filename = 'export.csv',
            headers = null,
            metadata = true,
            delimiter = ',',
            includeTimestamp = true
        } = options;
        
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('Data must be a non-empty array');
        }
        
        if (data.length > CONFIG.maxRowsCSV) {
            throw new Error(`Data exceeds maximum rows for CSV (${CONFIG.maxRowsCSV})`);
        }
        
        try {
            let csv = '';
            
            // Add metadata header
            if (metadata) {
                csv += '# BotV2 Dashboard Export\n';
                csv += `# Generated: ${formatDate(new Date())}\n`;
                csv += `# Rows: ${data.length}\n`;
                csv += `# Format: CSV\n`;
                csv += '\n';
            }
            
            // Get headers
            const cols = headers || Object.keys(data[0]);
            
            // Add header row
            csv += cols.map(escapeCSV).join(delimiter) + '\n';
            
            // Add data rows
            const totalRows = data.length;
            data.forEach((row, index) => {
                const values = cols.map(col => {
                    const value = row[col];
                    if (value instanceof Date) return formatDate(value);
                    if (typeof value === 'number') return value;
                    return escapeCSV(value);
                });
                csv += values.join(delimiter) + '\n';
                
                // Show progress every 10%
                if (index % Math.floor(totalRows / 10) === 0) {
                    const percent = Math.floor((index / totalRows) * 100);
                    showProgress('Exporting CSV', percent);
                }
            });
            
            showProgress('Exporting CSV', 100);
            
            // Add timestamp to filename
            const finalFilename = includeTimestamp 
                ? filename.replace('.csv', `_${Date.now()}.csv`)
                : filename;
            
            // Download
            downloadFile(csv, finalFilename, 'text/csv;charset=utf-8;');
            
            hideProgress();
            
            // Track in history
            addToHistory('csv', finalFilename, data.length);
            
            Logger.success(`CSV export completed: ${data.length} rows`);
            return { success: true, filename: finalFilename, rows: data.length };
            
        } catch (error) {
            hideProgress();
            Logger.error('CSV export failed', error);
            throw error;
        }
    }
    
    // ==================== EXCEL EXPORT ====================
    
    /**
     * Export data to Excel format (requires SheetJS)
     * @param {Array|Object} data - Array of objects or object with sheet names as keys
     * @param {Object} options - Export options
     */
    function toExcel(data, options = {}) {
        Logger.info('Starting Excel export...');
        
        // Check if SheetJS is loaded
        if (typeof XLSX === 'undefined') {
            Logger.error('SheetJS (XLSX) library not loaded. Please include: <script src="https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js"></script>');
            throw new Error('SheetJS library required for Excel export');
        }
        
        const {
            filename = 'export.xlsx',
            sheetName = 'Data',
            includeTimestamp = true,
            autoFilter = true,
            freezeHeader = true
        } = options;
        
        try {
            const workbook = XLSX.utils.book_new();
            
            // Handle multiple sheets
            const sheets = Array.isArray(data) 
                ? { [sheetName]: data }
                : data;
            
            let totalRows = 0;
            Object.entries(sheets).forEach(([name, sheetData]) => {
                if (!Array.isArray(sheetData) || sheetData.length === 0) {
                    Logger.error(`Sheet "${name}" has no data`);
                    return;
                }
                
                if (sheetData.length > CONFIG.maxRowsExcel) {
                    Logger.error(`Sheet "${name}" exceeds maximum rows (${CONFIG.maxRowsExcel})`);
                    return;
                }
                
                totalRows += sheetData.length;
                
                // Convert to worksheet
                const worksheet = XLSX.utils.json_to_sheet(sheetData);
                
                // Add auto-filter
                if (autoFilter) {
                    const range = XLSX.utils.decode_range(worksheet['!ref']);
                    worksheet['!autofilter'] = { ref: XLSX.utils.encode_range(range) };
                }
                
                // Freeze header row
                if (freezeHeader) {
                    worksheet['!freeze'] = { xSplit: 0, ySplit: 1 };
                }
                
                // Add worksheet to workbook
                XLSX.utils.book_append_sheet(workbook, worksheet, name);
                
                showProgress(`Creating Excel sheets`, 50);
            });
            
            showProgress('Generating Excel file', 75);
            
            // Generate Excel file
            const excelBuffer = XLSX.write(workbook, { 
                bookType: 'xlsx', 
                type: 'array',
                compression: true
            });
            
            showProgress('Preparing download', 90);
            
            // Add timestamp to filename
            const finalFilename = includeTimestamp 
                ? filename.replace('.xlsx', `_${Date.now()}.xlsx`)
                : filename;
            
            // Download
            const blob = new Blob([excelBuffer], { 
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
            });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = finalFilename;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            showProgress('Excel export complete', 100);
            hideProgress();
            
            // Track in history
            addToHistory('excel', finalFilename, totalRows);
            
            Logger.success(`Excel export completed: ${totalRows} rows, ${Object.keys(sheets).length} sheets`);
            return { 
                success: true, 
                filename: finalFilename, 
                rows: totalRows, 
                sheets: Object.keys(sheets).length 
            };
            
        } catch (error) {
            hideProgress();
            Logger.error('Excel export failed', error);
            throw error;
        }
    }
    
    // ==================== PDF EXPORT ====================
    
    /**
     * Export data to PDF format (requires jsPDF and jsPDF-AutoTable)
     * @param {Array} data - Array of objects
     * @param {Object} options - Export options
     */
    function toPDF(data, options = {}) {
        Logger.info('Starting PDF export...');
        
        // Check if jsPDF is loaded
        if (typeof jspdf === 'undefined' && typeof jsPDF === 'undefined') {
            Logger.error('jsPDF library not loaded. Please include: <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>');
            throw new Error('jsPDF library required for PDF export');
        }
        
        const {
            filename = 'export.pdf',
            title = 'BotV2 Dashboard Export',
            orientation = 'portrait',
            includeTimestamp = true,
            pageNumbers = true,
            metadata = true
        } = options;
        
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('Data must be a non-empty array');
        }
        
        if (data.length > CONFIG.maxRowsPDF) {
            throw new Error(`Data exceeds maximum rows for PDF (${CONFIG.maxRowsPDF})`);
        }
        
        try {
            showProgress('Initializing PDF', 10);
            
            // Initialize jsPDF
            const { jsPDF } = window.jspdf || window;
            const doc = new jsPDF({
                orientation: orientation,
                unit: 'mm',
                format: 'a4'
            });
            
            showProgress('Adding metadata', 20);
            
            // Add metadata
            if (metadata) {
                doc.setProperties({
                    title: title,
                    subject: 'Trading Dashboard Export',
                    author: 'BotV2',
                    creator: 'ExportLibrary v1.0',
                    created: new Date()
                });
            }
            
            // Add title
            doc.setFontSize(20);
            doc.setFont('helvetica', 'bold');
            doc.text(title, 14, 20);
            
            // Add generation info
            doc.setFontSize(10);
            doc.setFont('helvetica', 'normal');
            doc.text(`Generated: ${formatDate(new Date())}`, 14, 28);
            doc.text(`Total Records: ${data.length}`, 14, 34);
            
            showProgress('Preparing table', 40);
            
            // Check if autoTable is available
            if (doc.autoTable) {
                // Get headers
                const headers = Object.keys(data[0]);
                const tableData = data.map(row => headers.map(header => {
                    const value = row[header];
                    if (value instanceof Date) return formatDate(value);
                    if (typeof value === 'number') return formatNumber(value);
                    return String(value || '');
                }));
                
                showProgress('Generating table', 60);
                
                // Add table
                doc.autoTable({
                    head: [headers],
                    body: tableData,
                    startY: 40,
                    theme: 'grid',
                    headStyles: {
                        fillColor: [47, 129, 247],
                        textColor: [255, 255, 255],
                        fontStyle: 'bold'
                    },
                    styles: {
                        fontSize: 8,
                        cellPadding: 2
                    },
                    alternateRowStyles: {
                        fillColor: [245, 245, 245]
                    },
                    margin: { top: 40 },
                    didDrawPage: function(data) {
                        // Page numbers
                        if (pageNumbers) {
                            doc.setFontSize(8);
                            doc.text(
                                `Page ${doc.internal.getNumberOfPages()}`,
                                doc.internal.pageSize.width / 2,
                                doc.internal.pageSize.height - 10,
                                { align: 'center' }
                            );
                        }
                    }
                });
            } else {
                Logger.error('jsPDF-AutoTable plugin not loaded. Tables will not be formatted properly.');
                
                // Fallback: simple text output
                let yPos = 45;
                data.slice(0, 50).forEach((row, index) => {
                    const text = Object.values(row).join(' | ');
                    doc.text(text, 14, yPos);
                    yPos += 6;
                    
                    if (yPos > 280) {
                        doc.addPage();
                        yPos = 20;
                    }
                });
            }
            
            showProgress('Finalizing PDF', 90);
            
            // Add timestamp to filename
            const finalFilename = includeTimestamp 
                ? filename.replace('.pdf', `_${Date.now()}.pdf`)
                : filename;
            
            // Save PDF
            doc.save(finalFilename);
            
            showProgress('PDF export complete', 100);
            hideProgress();
            
            // Track in history
            addToHistory('pdf', finalFilename, data.length);
            
            Logger.success(`PDF export completed: ${data.length} rows`);
            return { success: true, filename: finalFilename, rows: data.length };
            
        } catch (error) {
            hideProgress();
            Logger.error('PDF export failed', error);
            throw error;
        }
    }
    
    // ==================== HISTORY MANAGEMENT ====================
    
    function addToHistory(format, filename, rows) {
        state.history.push({
            format,
            filename,
            rows,
            timestamp: new Date().toISOString()
        });
        
        // Keep only last 50 exports
        if (state.history.length > 50) {
            state.history.shift();
        }
    }
    
    function getHistory() {
        return [...state.history];
    }
    
    function clearHistory() {
        state.history = [];
        Logger.info('Export history cleared');
    }
    
    // ==================== BATCH EXPORT ====================
    
    /**
     * Export same data to multiple formats
     */
    async function batchExport(data, formats = ['csv', 'excel', 'pdf'], options = {}) {
        Logger.info(`Starting batch export: ${formats.join(', ')}`);
        
        const results = [];
        
        for (const format of formats) {
            try {
                let result;
                switch(format.toLowerCase()) {
                    case 'csv':
                        result = toCSV(data, options.csv || {});
                        break;
                    case 'excel':
                    case 'xlsx':
                        result = toExcel(data, options.excel || {});
                        break;
                    case 'pdf':
                        result = toPDF(data, options.pdf || {});
                        break;
                    default:
                        Logger.error(`Unknown format: ${format}`);
                        continue;
                }
                results.push({ format, ...result });
                
                // Small delay between exports
                await new Promise(resolve => setTimeout(resolve, 500));
                
            } catch (error) {
                Logger.error(`Batch export failed for ${format}`, error);
                results.push({ format, success: false, error: error.message });
            }
        }
        
        Logger.success(`Batch export completed: ${results.filter(r => r.success).length}/${formats.length} successful`);
        return results;
    }
    
    // ==================== PUBLIC API ====================
    
    return {
        // Export functions
        toCSV,
        toExcel,
        toPDF,
        batchExport,
        
        // History
        getHistory,
        clearHistory,
        
        // Utilities
        formatDate,
        formatNumber,
        
        // Config
        getConfig: () => ({ ...CONFIG }),
        
        // State
        isExporting: () => state.exporting,
        
        // Version
        version: '1.0.0'
    };
    
})();

// ==================== EXPORT ====================
console.log(
    '%c✅ ExportLibrary ready',
    'color:#3fb950;font-weight:600',
    '- Use ExportLibrary.toCSV(), .toExcel(), .toPDF()'
);
