/**
 * Excel Export Web Worker v7.6
 * 
 * Isolates SheetJS library in worker context to eliminate unsafe-eval
 * from main thread CSP.
 * 
 * Security: Worker has separate CSP allowing unsafe-eval, but cannot
 * access DOM, cookies, or localStorage.
 * 
 * @version 1.0.0
 * @date January 25, 2026
 */

// Import SheetJS in worker context
importScripts('https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js');

// Worker state
let initialized = false;

/**
 * Initialize worker and verify SheetJS loaded
 */
function initialize() {
    if (typeof XLSX === 'undefined') {
        throw new Error('SheetJS failed to load in worker');
    }
    initialized = true;
    console.log('[ExcelWorker] Initialized with SheetJS', XLSX.version);
}

/**
 * Convert JSON data to Excel workbook
 * @param {Array} data - Array of objects
 * @param {Object} options - Export options
 * @returns {ArrayBuffer} Excel file as ArrayBuffer
 */
function jsonToExcel(data, options = {}) {
    if (!initialized) initialize();
    
    // Validate data
    if (!Array.isArray(data)) {
        throw new Error('Data must be an array');
    }
    
    if (data.length === 0) {
        throw new Error('Data array is empty');
    }
    
    // Create worksheet from JSON
    const ws = XLSX.utils.json_to_sheet(data, {
        header: options.headers || undefined,
        skipHeader: options.skipHeader || false
    });
    
    // Apply column widths if provided
    if (options.columnWidths) {
        ws['!cols'] = options.columnWidths.map(w => ({ wch: w }));
    }
    
    // Apply styles if provided (basic support)
    if (options.autoFilter && data.length > 0) {
        const range = XLSX.utils.decode_range(ws['!ref']);
        ws['!autofilter'] = { ref: XLSX.utils.encode_range(range) };
    }
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, options.sheetName || 'Sheet1');
    
    // Add metadata
    wb.Props = {
        Title: options.title || 'BotV2 Export',
        Author: 'BotV2 Dashboard v7.6',
        CreatedDate: new Date()
    };
    
    // Generate Excel file (ArrayBuffer)
    const wbout = XLSX.write(wb, {
        bookType: 'xlsx',
        type: 'array',  // Returns ArrayBuffer
        compression: true
    });
    
    return wbout;
}

/**
 * Convert HTML table to Excel workbook
 * @param {string} tableHTML - HTML table as string
 * @param {Object} options - Export options
 * @returns {ArrayBuffer} Excel file as ArrayBuffer
 */
function tableToExcel(tableHTML, options = {}) {
    if (!initialized) initialize();
    
    // Parse HTML to extract table data
    const parser = new DOMParser();
    const doc = parser.parseFromString(tableHTML, 'text/html');
    const table = doc.querySelector('table');
    
    if (!table) {
        throw new Error('No table found in HTML');
    }
    
    // Convert table to worksheet
    const ws = XLSX.utils.table_to_sheet(table, {
        raw: options.raw || false
    });
    
    // Apply column widths if provided
    if (options.columnWidths) {
        ws['!cols'] = options.columnWidths.map(w => ({ wch: w }));
    }
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, options.sheetName || 'Sheet1');
    
    // Add metadata
    wb.Props = {
        Title: options.title || 'BotV2 Table Export',
        Author: 'BotV2 Dashboard v7.6',
        CreatedDate: new Date()
    };
    
    // Generate Excel file
    const wbout = XLSX.write(wb, {
        bookType: 'xlsx',
        type: 'array',
        compression: true
    });
    
    return wbout;
}

/**
 * Message handler - receives commands from main thread
 */
self.onmessage = function(e) {
    const { id, action, data, options } = e.data;
    
    const startTime = performance.now();
    
    try {
        let result;
        
        switch (action) {
            case 'init':
                initialize();
                self.postMessage({
                    id,
                    status: 'success',
                    message: 'Worker initialized',
                    version: XLSX.version
                });
                break;
            
            case 'export-json':
                result = jsonToExcel(data, options);
                const duration = performance.now() - startTime;
                self.postMessage({
                    id,
                    status: 'success',
                    data: result,
                    size: result.byteLength,
                    duration: Math.round(duration),
                    rows: data.length
                }, [result.buffer]);  // Transfer ownership (zero-copy)
                break;
            
            case 'export-table':
                result = tableToExcel(data, options);
                const tableDuration = performance.now() - startTime;
                self.postMessage({
                    id,
                    status: 'success',
                    data: result,
                    size: result.byteLength,
                    duration: Math.round(tableDuration)
                }, [result.buffer]);
                break;
            
            case 'ping':
                self.postMessage({
                    id,
                    status: 'success',
                    message: 'pong',
                    timestamp: Date.now(),
                    uptime: performance.now()
                });
                break;
            
            case 'stats':
                self.postMessage({
                    id,
                    status: 'success',
                    stats: {
                        initialized,
                        xlsxVersion: typeof XLSX !== 'undefined' ? XLSX.version : 'not loaded',
                        uptime: performance.now(),
                        memory: self.performance && self.performance.memory 
                            ? {
                                usedJSHeapSize: self.performance.memory.usedJSHeapSize,
                                totalJSHeapSize: self.performance.memory.totalJSHeapSize
                            }
                            : null
                    }
                });
                break;
            
            default:
                throw new Error(`Unknown action: ${action}`);
        }
        
    } catch (error) {
        console.error('[ExcelWorker] Error:', error);
        self.postMessage({
            id,
            status: 'error',
            error: error.message,
            stack: error.stack
        });
    }
};

// Handle worker errors
self.onerror = function(error) {
    console.error('[ExcelWorker] Uncaught error:', error);
    self.postMessage({
        status: 'error',
        error: error.message || 'Unknown worker error',
        filename: error.filename,
        lineno: error.lineno
    });
};

// Worker ready signal
self.postMessage({
    status: 'ready',
    message: 'Excel Worker loaded and ready',
    timestamp: Date.now(),
    version: '7.6.0'
});

console.log('[ExcelWorker] Worker script loaded successfully');
