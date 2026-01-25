/**
 * Excel Export Manager v7.6
 * 
 * Manages communication with Excel Web Worker for secure Excel exports
 * without requiring unsafe-eval in main thread CSP.
 * 
 * @version 1.0.0
 * @date January 25, 2026
 */

class ExcelExportManager {
    constructor() {
        this.worker = null;
        this.initialized = false;
        this.pendingRequests = new Map();
        this.requestId = 0;
        this.workerPath = '/static/js/workers/excel-worker.js';
        this.initPromise = null;
    }
    
    /**
     * Initialize worker and wait for ready signal
     * @returns {Promise<void>}
     */
    async init() {
        // If already initialized, return immediately
        if (this.initialized) return;
        
        // If initialization in progress, wait for it
        if (this.initPromise) return this.initPromise;
        
        // Start new initialization
        this.initPromise = new Promise((resolve, reject) => {
            try {
                console.log('[ExcelManager] Initializing worker...');
                
                // Create worker
                this.worker = new Worker(this.workerPath);
                
                // Setup message handler
                this.worker.onmessage = this._handleMessage.bind(this);
                
                // Setup error handler
                this.worker.onerror = (error) => {
                    console.error('[ExcelManager] Worker error:', error);
                    this.initialized = false;
                    reject(new Error(`Worker error: ${error.message}`));
                };
                
                // Wait for ready signal
                const readyHandler = (e) => {
                    if (e.data.status === 'ready') {
                        this.initialized = true;
                        console.log('[ExcelManager] Worker ready:', e.data.version);
                        this.worker.removeEventListener('message', readyHandler);
                        resolve();
                    }
                };
                
                this.worker.addEventListener('message', readyHandler);
                
                // Timeout after 10 seconds
                setTimeout(() => {
                    if (!this.initialized) {
                        this.worker.removeEventListener('message', readyHandler);
                        reject(new Error('Worker initialization timeout (10s)'));
                    }
                }, 10000);
                
            } catch (error) {
                console.error('[ExcelManager] Init error:', error);
                this.initialized = false;
                reject(error);
            }
        });
        
        try {
            await this.initPromise;
        } finally {
            this.initPromise = null;
        }
    }
    
    /**
     * Handle messages from worker
     * @private
     */
    _handleMessage(e) {
        const { id, status, data, error, message } = e.data;
        
        // Ignore ready signal (handled in init)
        if (status === 'ready') return;
        
        // Find pending request
        const request = this.pendingRequests.get(id);
        if (!request) {
            console.warn('[ExcelManager] Unknown request ID:', id);
            return;
        }
        
        // Clear timeout
        clearTimeout(request.timeout);
        
        // Remove from pending
        this.pendingRequests.delete(id);
        
        // Resolve or reject
        if (status === 'success') {
            request.resolve(data);
        } else if (status === 'error') {
            request.reject(new Error(error || 'Unknown worker error'));
        }
    }
    
    /**
     * Send message to worker and wait for response
     * @private
     * @param {Object} message - Message to send
     * @param {number} timeout - Timeout in ms
     * @returns {Promise<any>}
     */
    _sendMessage(message, timeout = 30000) {
        if (!this.initialized) {
            return Promise.reject(new Error('Worker not initialized'));
        }
        
        return new Promise((resolve, reject) => {
            const id = ++this.requestId;
            
            // Store request
            const request = {
                id,
                resolve,
                reject,
                timestamp: Date.now(),
                timeout: setTimeout(() => {
                    this.pendingRequests.delete(id);
                    reject(new Error(`Worker request timeout (${timeout}ms)`));
                }, timeout)
            };
            
            this.pendingRequests.set(id, request);
            
            // Send to worker
            this.worker.postMessage({ id, ...message });
        });
    }
    
    /**
     * Export JSON data to Excel
     * @param {Array} data - Array of objects
     * @param {Object} options - Export options
     * @param {string} [options.sheetName='Sheet1'] - Sheet name
     * @param {Array<number>} [options.columnWidths] - Column widths
     * @param {Array<string>} [options.headers] - Custom headers
     * @param {boolean} [options.skipHeader=false] - Skip header row
     * @param {boolean} [options.autoFilter=false] - Enable auto filter
     * @param {string} [options.title] - Workbook title
     * @returns {Promise<ArrayBuffer>}
     */
    async exportJSON(data, options = {}) {
        // Auto-initialize if needed
        if (!this.initialized) {
            await this.init();
        }
        
        // Validate data
        if (!Array.isArray(data)) {
            throw new Error('Data must be an array');
        }
        
        if (data.length === 0) {
            throw new Error('Data array is empty');
        }
        
        console.log(`[ExcelManager] Exporting ${data.length} rows to Excel...`);
        
        const startTime = performance.now();
        
        try {
            const result = await this._sendMessage({
                action: 'export-json',
                data,
                options
            }, 60000);  // 60s timeout for large datasets
            
            const duration = performance.now() - startTime;
            console.log(`[ExcelManager] Export completed in ${Math.round(duration)}ms (${result.byteLength.toLocaleString()} bytes)`);
            
            return result;
        } catch (error) {
            console.error('[ExcelManager] Export failed:', error);
            throw error;
        }
    }
    
    /**
     * Export HTML table to Excel
     * @param {HTMLTableElement|string} table - Table element or HTML string
     * @param {Object} options - Export options
     * @param {string} [options.sheetName='Sheet1'] - Sheet name
     * @param {Array<number>} [options.columnWidths] - Column widths
     * @param {boolean} [options.raw=false] - Preserve raw values
     * @param {string} [options.title] - Workbook title
     * @returns {Promise<ArrayBuffer>}
     */
    async exportTable(table, options = {}) {
        // Auto-initialize if needed
        if (!this.initialized) {
            await this.init();
        }
        
        // Validate table
        if (!table) {
            throw new Error('Table element or HTML required');
        }
        
        // Convert table to HTML string if element
        const tableHTML = typeof table === 'string' 
            ? table 
            : table.outerHTML;
        
        console.log('[ExcelManager] Exporting HTML table to Excel...');
        
        try {
            const result = await this._sendMessage({
                action: 'export-table',
                data: tableHTML,
                options
            }, 30000);
            
            console.log(`[ExcelManager] Table export completed (${result.byteLength.toLocaleString()} bytes)`);
            
            return result;
        } catch (error) {
            console.error('[ExcelManager] Table export failed:', error);
            throw error;
        }
    }
    
    /**
     * Download Excel file to user's computer
     * @param {ArrayBuffer} data - Excel file data
     * @param {string} filename - Filename (default: 'export.xlsx')
     */
    download(data, filename = 'export.xlsx') {
        if (!filename.endsWith('.xlsx')) {
            filename += '.xlsx';
        }
        
        try {
            const blob = new Blob([data], {
                type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            });
            
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            
            // Cleanup blob URL after a short delay
            setTimeout(() => URL.revokeObjectURL(url), 1000);
            
            console.log(`[ExcelManager] Downloaded: ${filename} (${data.byteLength.toLocaleString()} bytes)`);
        } catch (error) {
            console.error('[ExcelManager] Download failed:', error);
            throw error;
        }
    }
    
    /**
     * Test worker connectivity
     * @returns {Promise<boolean>}
     */
    async ping() {
        if (!this.initialized) {
            await this.init();
        }
        
        try {
            await this._sendMessage({ action: 'ping' }, 5000);
            console.log('[ExcelManager] Ping successful');
            return true;
        } catch (error) {
            console.error('[ExcelManager] Ping failed:', error);
            return false;
        }
    }
    
    /**
     * Get worker statistics
     * @returns {Promise<Object>}
     */
    async getStats() {
        if (!this.initialized) {
            await this.init();
        }
        
        try {
            const stats = await this._sendMessage({ action: 'stats' }, 5000);
            return stats;
        } catch (error) {
            console.error('[ExcelManager] Failed to get stats:', error);
            throw error;
        }
    }
    
    /**
     * Terminate worker and clean up resources
     */
    terminate() {
        if (this.worker) {
            console.log('[ExcelManager] Terminating worker...');
            
            // Clear all pending requests
            for (const [id, request] of this.pendingRequests.entries()) {
                clearTimeout(request.timeout);
                request.reject(new Error('Worker terminated'));
            }
            this.pendingRequests.clear();
            
            // Terminate worker
            this.worker.terminate();
            this.worker = null;
            this.initialized = false;
            
            console.log('[ExcelManager] Worker terminated');
        }
    }
    
    /**
     * Restart worker (terminate and reinitialize)
     * @returns {Promise<void>}
     */
    async restart() {
        console.log('[ExcelManager] Restarting worker...');
        this.terminate();
        await this.init();
        console.log('[ExcelManager] Worker restarted');
    }
}

// Create and export singleton instance
if (typeof window !== 'undefined') {
    window.ExcelExportManager = new ExcelExportManager();
    console.log('[ExcelManager] Manager loaded and ready');
}

// Also export class for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExcelExportManager;
}
