/**
 * BotV2 Dashboard Export Library v7.4
 * Professional Export System with SheetJS and jsPDF
 * 
 * @author Juan Carlos Garcia
 * @version 7.4.0
 * @date 25-01-2026
 * 
 * Dependencies (loaded from CDN):
 * - SheetJS: https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js
 * - jsPDF: https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js
 * - jsPDF-AutoTable: https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.31/jspdf.plugin.autotable.min.js
 */

'use strict';

// ==================== EXPORT LIBRARY ====================
const ExportLibrary = (() => {
    
    // Check if libraries are loaded
    const checkDependencies = () => {
        const deps = {
            xlsx: typeof XLSX !== 'undefined',
            jspdf: typeof window.jspdf !== 'undefined'
        };
        
        if (!deps.xlsx) {
            console.warn('SheetJS not loaded. Excel exports will be limited.');
        }
        
        if (!deps.jspdf) {
            console.warn('jsPDF not loaded. PDF exports will be limited.');
        }
        
        return deps;
    };
    
    // ==================== CSV EXPORT ====================
    const exportToCSV = (data, filename = 'export.csv', options = {}) => {
        console.log('[Export] Starting CSV export:', filename);
        
        try {
            // Convert data to CSV
            let csv = '';
            
            // Add metadata headers
            if (options.includeMetadata !== false) {
                csv += `# BotV2 Dashboard Export\n`;
                csv += `# Generated: ${new Date().toISOString()}\n`;
                csv += `# Section: ${options.section || 'dashboard'}\n`;
                csv += `\n`;
            }
            
            // Handle array of objects
            if (Array.isArray(data) && data.length > 0) {
                // Headers
                const headers = Object.keys(data[0]);
                csv += headers.join(',') + '\n';
                
                // Rows
                data.forEach(row => {
                    const values = headers.map(header => {
                        const value = row[header];
                        // Handle special characters and commas
                        if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
                            return `"${value.replace(/"/g, '""')}"`;
                        }
                        return value !== null && value !== undefined ? value : '';
                    });
                    csv += values.join(',') + '\n';
                });
            } else {
                // Handle simple key-value data
                csv += 'Metric,Value\n';
                Object.entries(data).forEach(([key, value]) => {
                    csv += `${key},${value}\n`;
                });
            }
            
            // Create and download
            downloadFile(csv, filename, 'text/csv');
            
            console.log('[Export] CSV export completed');
            return { success: true, format: 'csv', filename };
            
        } catch (error) {
            console.error('[Export] CSV export failed:', error);
            return { success: false, error: error.message };
        }
    };
    
    // ==================== EXCEL EXPORT ====================
    const exportToExcel = (data, filename = 'export.xlsx', options = {}) => {
        console.log('[Export] Starting Excel export:', filename);
        
        const deps = checkDependencies();
        
        if (!deps.xlsx) {
            console.error('[Export] SheetJS not loaded. Falling back to CSV.');
            return exportToCSV(data, filename.replace('.xlsx', '.csv'), options);
        }
        
        try {
            // Create workbook
            const wb = XLSX.utils.book_new();
            
            // Handle multiple sheets
            if (options.multiSheet && typeof data === 'object' && !Array.isArray(data)) {
                // data is { sheetName: sheetData }
                Object.entries(data).forEach(([sheetName, sheetData]) => {
                    const ws = XLSX.utils.json_to_sheet(sheetData);
                    XLSX.utils.book_append_sheet(wb, ws, sheetName);
                });
            } else {
                // Single sheet
                const ws = XLSX.utils.json_to_sheet(Array.isArray(data) ? data : [data]);
                XLSX.utils.book_append_sheet(wb, ws, options.sheetName || 'Data');
            }
            
            // Add metadata sheet if requested
            if (options.includeMetadata !== false) {
                const metadata = [
                    { Property: 'Export Source', Value: 'BotV2 Dashboard' },
                    { Property: 'Generated', Value: new Date().toISOString() },
                    { Property: 'Section', Value: options.section || 'dashboard' },
                    { Property: 'Version', Value: '7.4.0' }
                ];
                const metaWs = XLSX.utils.json_to_sheet(metadata);
                XLSX.utils.book_append_sheet(wb, metaWs, 'Metadata');
            }
            
            // Write file
            XLSX.writeFile(wb, filename);
            
            console.log('[Export] Excel export completed');
            return { success: true, format: 'excel', filename };
            
        } catch (error) {
            console.error('[Export] Excel export failed:', error);
            return { success: false, error: error.message };
        }
    };
    
    // ==================== PDF EXPORT ====================
    const exportToPDF = (data, filename = 'export.pdf', options = {}) => {
        console.log('[Export] Starting PDF export:', filename);
        
        const deps = checkDependencies();
        
        if (!deps.jspdf) {
            console.error('[Export] jsPDF not loaded. Cannot export to PDF.');
            alert('PDF export requires jsPDF library. Falling back to CSV.');
            return exportToCSV(data, filename.replace('.pdf', '.csv'), options);
        }
        
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // Add header
            doc.setFontSize(20);
            doc.setTextColor(47, 129, 247); // Primary blue
            doc.text('BotV2 Dashboard Export', 14, 20);
            
            // Add metadata
            doc.setFontSize(10);
            doc.setTextColor(125, 133, 144); // Secondary gray
            doc.text(`Generated: ${new Date().toLocaleString()}`, 14, 28);
            doc.text(`Section: ${options.section || 'Dashboard'}`, 14, 33);
            
            // Add line separator
            doc.setDrawColor(48, 54, 61);
            doc.line(14, 36, 196, 36);
            
            let yPosition = 45;
            
            // Handle table data
            if (Array.isArray(data) && data.length > 0 && typeof doc.autoTable === 'function') {
                // Use autoTable plugin if available
                const headers = Object.keys(data[0]);
                const rows = data.map(row => headers.map(h => row[h]));
                
                doc.autoTable({
                    head: [headers],
                    body: rows,
                    startY: yPosition,
                    theme: 'grid',
                    headStyles: {
                        fillColor: [47, 129, 247],
                        textColor: [255, 255, 255],
                        fontStyle: 'bold'
                    },
                    alternateRowStyles: {
                        fillColor: [246, 248, 250]
                    },
                    styles: {
                        fontSize: 9,
                        cellPadding: 3
                    }
                });
                
            } else {
                // Simple key-value display
                doc.setFontSize(12);
                doc.setTextColor(31, 35, 40);
                
                Object.entries(data).forEach(([key, value]) => {
                    if (yPosition > 270) {
                        doc.addPage();
                        yPosition = 20;
                    }
                    
                    doc.setFont(undefined, 'bold');
                    doc.text(`${key}:`, 14, yPosition);
                    doc.setFont(undefined, 'normal');
                    doc.text(String(value), 80, yPosition);
                    
                    yPosition += 7;
                });
            }
            
            // Add footer
            const pageCount = doc.internal.getNumberOfPages();
            for (let i = 1; i <= pageCount; i++) {
                doc.setPage(i);
                doc.setFontSize(8);
                doc.setTextColor(125, 133, 144);
                doc.text(`Page ${i} of ${pageCount}`, 14, 287);
                doc.text('BotV2 Dashboard v7.4', 196, 287, { align: 'right' });
            }
            
            // Save
            doc.save(filename);
            
            console.log('[Export] PDF export completed');
            return { success: true, format: 'pdf', filename };
            
        } catch (error) {
            console.error('[Export] PDF export failed:', error);
            return { success: false, error: error.message };
        }
    };
    
    // ==================== HELPER FUNCTIONS ====================
    
    const downloadFile = (content, filename, mimeType) => {
        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    };
    
    const showProgress = (message) => {
        console.log(`[Export] ${message}`);
        // Could add UI progress indicator here
    };
    
    // ==================== UNIFIED EXPORT FUNCTION ====================
    
    const exportData = (format, data, filename, options = {}) => {
        showProgress(`Starting ${format.toUpperCase()} export...`);
        
        let result;
        
        switch (format.toLowerCase()) {
            case 'csv':
                result = exportToCSV(data, filename || 'export.csv', options);
                break;
            case 'excel':
            case 'xlsx':
                result = exportToExcel(data, filename || 'export.xlsx', options);
                break;
            case 'pdf':
                result = exportToPDF(data, filename || 'export.pdf', options);
                break;
            default:
                console.error('[Export] Unknown format:', format);
                result = { success: false, error: 'Unknown format' };
        }
        
        if (result.success) {
            showProgress(`Export completed: ${result.filename}`);
        } else {
            showProgress(`Export failed: ${result.error}`);
        }
        
        return result;
    };
    
    // ==================== BATCH EXPORT ====================
    
    const exportBatch = async (exports) => {
        console.log('[Export] Starting batch export:', exports.length, 'files');
        
        const results = [];
        
        for (const exp of exports) {
            const { format, data, filename, options } = exp;
            const result = exportData(format, data, filename, options);
            results.push(result);
            
            // Small delay between exports
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        console.log('[Export] Batch export completed');
        return results;
    };
    
    // ==================== PUBLIC API ====================
    
    return {
        // Export functions
        exportToCSV,
        exportToExcel,
        exportToPDF,
        exportData,
        exportBatch,
        
        // Utilities
        checkDependencies,
        
        // Info
        version: '7.4.0',
        supportedFormats: ['csv', 'excel', 'xlsx', 'pdf']
    };
    
})();

// ==================== LOAD EXTERNAL LIBRARIES ====================

(function loadExportLibraries() {
    console.log('[Export] Loading external libraries...');
    
    // SheetJS for Excel
    if (typeof XLSX === 'undefined') {
        const xlsxScript = document.createElement('script');
        xlsxScript.src = 'https://cdn.sheetjs.com/xlsx-latest/package/dist/xlsx.full.min.js';
        xlsxScript.onload = () => {
            console.log('[Export] SheetJS loaded successfully');
        };
        xlsxScript.onerror = () => {
            console.warn('[Export] Failed to load SheetJS. Excel exports will be limited.');
        };
        document.head.appendChild(xlsxScript);
    }
    
    // jsPDF for PDF
    if (typeof window.jspdf === 'undefined') {
        const jspdfScript = document.createElement('script');
        jspdfScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
        jspdfScript.onload = () => {
            console.log('[Export] jsPDF loaded successfully');
            
            // Load autoTable plugin
            const autoTableScript = document.createElement('script');
            autoTableScript.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.5.31/jspdf.plugin.autotable.min.js';
            autoTableScript.onload = () => {
                console.log('[Export] jsPDF-AutoTable loaded successfully');
            };
            autoTableScript.onerror = () => {
                console.warn('[Export] Failed to load jsPDF-AutoTable. PDF tables will be limited.');
            };
            document.head.appendChild(autoTableScript);
        };
        jspdfScript.onerror = () => {
            console.warn('[Export] Failed to load jsPDF. PDF exports will be unavailable.');
        };
        document.head.appendChild(jspdfScript);
    }
})();

// ==================== EXPORT TO GLOBAL ====================

window.ExportLibrary = ExportLibrary;

console.log('%c📥 Export Library v7.4.0 loaded', 'background:#8338ec;color:white;padding:4px 8px;border-radius:3px;font-weight:600');
console.log('  ✅ CSV export ready');
console.log('  ⏳ Loading SheetJS for Excel...');
console.log('  ⏳ Loading jsPDF for PDF...');
