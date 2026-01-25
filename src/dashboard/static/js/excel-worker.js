/**
 * 🏆 Excel Export Web Worker - v7.6 Enterprise Edition
 * 
 * Purpose: Isolate SheetJS (XLSX) execution in separate worker context
 * to eliminate need for unsafe-eval in main thread CSP.
 * 
 * Security Benefits:
 * - ✅ Main thread remains eval-free
 * - ✅ Worker context isolated from DOM
 * - ✅ Secure message passing only
 * - ✅ No direct access to window/document
 * 
 * Author: Juan Carlos Garcia
 * Date: January 25, 2026
 * Version: 1.0.0
 */

// Import SheetJS library (runs with eval in worker context, isolated from main thread)
importScripts('https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js');

/**
 * Handle messages from main thread
 */
self.addEventListener('message', async function(e) {
    const { action, data, options } = e.data;
    
    try {
        switch (action) {
            case 'export_excel':
                const result = await exportToExcel(data, options);
                self.postMessage({ success: true, data: result });
                break;
                
            case 'parse_excel':
                const parsed = await parseExcelData(data);
                self.postMessage({ success: true, data: parsed });
                break;
                
            case 'health_check':
                self.postMessage({ 
                    success: true, 
                    data: { 
                        ready: true, 
                        xlsxVersion: XLSX.version || 'unknown',
                        workerActive: true
                    } 
                });
                break;
                
            default:
                throw new Error(`Unknown action: ${action}`);
        }
    } catch (error) {
        self.postMessage({ 
            success: false, 
            error: error.message,
            stack: error.stack
        });
    }
});

/**
 * Export data to Excel format
 * @param {Array|Object} data - Data to export (array of objects or 2D array)
 * @param {Object} options - Export options
 * @returns {Object} - { blob, filename, size }
 */
async function exportToExcel(data, options = {}) {
    const {
        filename = 'export.xlsx',
        sheetName = 'Sheet1',
        includeHeaders = true,
        format = 'xlsx' // xlsx, csv, html
    } = options;
    
    // Create new workbook
    const wb = XLSX.utils.book_new();
    
    // Convert data to worksheet
    let ws;
    if (Array.isArray(data)) {
        if (data.length > 0 && typeof data[0] === 'object' && !Array.isArray(data[0])) {
            // Array of objects
            ws = XLSX.utils.json_to_sheet(data);
        } else {
            // 2D array
            ws = XLSX.utils.aoa_to_sheet(data);
        }
    } else if (typeof data === 'object') {
        // Single object to array
        ws = XLSX.utils.json_to_sheet([data]);
    } else {
        throw new Error('Invalid data format. Expected array or object.');
    }
    
    // Add worksheet to workbook
    XLSX.utils.book_append_sheet(wb, ws, sheetName);
    
    // Generate binary data
    const wbout = XLSX.write(wb, { 
        bookType: format, 
        type: 'array',
        compression: true
    });
    
    // Return data as transferable ArrayBuffer
    return {
        buffer: wbout.buffer,
        filename: filename,
        size: wbout.byteLength,
        mimeType: format === 'xlsx' 
            ? 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            : format === 'csv'
            ? 'text/csv'
            : 'text/html'
    };
}

/**
 * Parse Excel file data
 * @param {ArrayBuffer} data - Excel file buffer
 * @returns {Object} - Parsed data
 */
async function parseExcelData(data) {
    const wb = XLSX.read(data, { type: 'array' });
    
    const result = {
        sheetNames: wb.SheetNames,
        sheets: {}
    };
    
    // Parse each sheet
    wb.SheetNames.forEach(sheetName => {
        const ws = wb.Sheets[sheetName];
        result.sheets[sheetName] = {
            json: XLSX.utils.sheet_to_json(ws),
            csv: XLSX.utils.sheet_to_csv(ws),
            html: XLSX.utils.sheet_to_html(ws)
        };
    });
    
    return result;
}

// Signal that worker is ready
self.postMessage({ 
    type: 'worker_ready',
    success: true,
    data: { 
        initialized: true,
        xlsxLoaded: typeof XLSX !== 'undefined',
        xlsxVersion: typeof XLSX !== 'undefined' ? XLSX.version : null
    }
});
