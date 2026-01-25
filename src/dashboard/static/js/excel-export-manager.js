/**
 * 🏆 Excel Export Manager - v7.6 Enterprise Edition
 * 
 * Purpose: Coordinate Excel exports between main thread and worker thread.
 * Provides backward-compatible API while using Web Worker internally.
 * 
 * Security: This runs in main thread (eval-free) and communicates with
 * excel-worker.js for actual XLSX operations.
 * 
 * Author: Juan Carlos Garcia
 * Date: January 25, 2026
 * Version: 1.0.0
 */

class ExcelExportManager {
    constructor() {
        this.worker = null;
        this.workerReady = false;
        this.pendingOperations = new Map();
        this.operationId = 0;
        this.initWorker();
    }
    
    /**
     * Initialize the Web Worker
     */
    initWorker() {
        try {
            const workerUrl = '/static/js/excel-worker.js';
            this.worker = new Worker(workerUrl);
            
            this.worker.addEventListener('message', (e) => this.handleWorkerMessage(e));
            this.worker.addEventListener('error', (e) => this.handleWorkerError(e));
            
            // Health check
            this.sendToWorker('health_check', null)
                .then(result => {
                    this.workerReady = true;
                    console.log('%c✅ Excel Worker initialized', 'color:#3fb950;font-weight:600', result.data);
                })
                .catch(err => {
                    console.error('%c❌ Excel Worker failed to initialize', 'color:#f85149;font-weight:600', err);
                });
        } catch (error) {
            console.error('Failed to create Excel Worker:', error);
            this.workerReady = false;
        }
    }
    
    /**
     * Handle messages from worker
     */
    handleWorkerMessage(e) {
        const { type, success, data, error, operationId } = e.data;
        
        if (type === 'worker_ready') {
            console.log('%c📦 SheetJS loaded in worker', 'color:#3fb950;font-weight:600', data);
            return;
        }
        
        if (operationId && this.pendingOperations.has(operationId)) {
            const { resolve, reject } = this.pendingOperations.get(operationId);
            this.pendingOperations.delete(operationId);
            
            if (success) {
                resolve(data);
            } else {
                reject(new Error(error || 'Worker operation failed'));
            }
        }
    }
    
    /**
     * Handle worker errors
     */
    handleWorkerError(e) {
        console.error('%c❌ Excel Worker error', 'color:#f85149;font-weight:600', e);
        // Reject all pending operations
        this.pendingOperations.forEach(({ reject }) => {
            reject(new Error('Worker error: ' + e.message));
        });
        this.pendingOperations.clear();
    }
    
    /**
     * Send message to worker and get promise for result
     */
    sendToWorker(action, data, options = {}) {
        return new Promise((resolve, reject) => {
            if (!this.worker) {
                reject(new Error('Excel Worker not available'));
                return;
            }
            
            const operationId = ++this.operationId;
            this.pendingOperations.set(operationId, { resolve, reject });
            
            this.worker.postMessage({
                operationId,
                action,
                data,
                options
            });
            
            // Timeout after 30 seconds
            setTimeout(() => {
                if (this.pendingOperations.has(operationId)) {
                    this.pendingOperations.delete(operationId);
                    reject(new Error('Excel Worker operation timeout'));
                }
            }, 30000);
        });
    }
    
    /**
     * Export data to Excel file
     * @param {Array|Object} data - Data to export
     * @param {Object} options - Export options
     * @returns {Promise<void>}
     */
    async exportToExcel(data, options = {}) {
        if (!this.workerReady) {
            throw new Error('Excel Worker not ready yet');
        }
        
        const defaultOptions = {
            filename: 'dashboard_export_' + new Date().toISOString().slice(0,10) + '.xlsx',
            sheetName: 'Data',
            format: 'xlsx'
        };
        
        const mergedOptions = { ...defaultOptions, ...options };
        
        try {
            const result = await this.sendToWorker('export_excel', data, mergedOptions);
            
            // Create blob from ArrayBuffer
            const blob = new Blob([result.buffer], { type: result.mimeType });
            
            // Trigger download
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = result.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            console.log(`%c✅ Excel export successful: ${result.filename} (${(result.size / 1024).toFixed(1)} KB)`, 'color:#3fb950;font-weight:600');
            
            return result;
        } catch (error) {
            console.error('%c❌ Excel export failed', 'color:#f85149;font-weight:600', error);
            throw error;
        }
    }
    
    /**
     * Parse Excel file
     * @param {File|ArrayBuffer} file - Excel file to parse
     * @returns {Promise<Object>}
     */
    async parseExcel(file) {
        if (!this.workerReady) {
            throw new Error('Excel Worker not ready yet');
        }
        
        let buffer;
        if (file instanceof File) {
            buffer = await file.arrayBuffer();
        } else if (file instanceof ArrayBuffer) {
            buffer = file;
        } else {
            throw new Error('Invalid file type. Expected File or ArrayBuffer.');
        }
        
        return await this.sendToWorker('parse_excel', buffer);
    }
    
    /**
     * Clean up worker
     */
    destroy() {
        if (this.worker) {
            this.worker.terminate();
            this.worker = null;
            this.workerReady = false;
            console.log('%c🗑️ Excel Worker terminated', 'color:#8b949e');
        }
    }
}

// Create global instance
window.excelManager = new ExcelExportManager();

// Backward compatibility: Add to window.XLSX namespace
if (typeof window.XLSX === 'undefined') {
    window.XLSX = {};
}

// Provide backward-compatible API
window.XLSX.exportToExcel = (data, options) => {
    return window.excelManager.exportToExcel(data, options);
};

window.XLSX.parseExcel = (file) => {
    return window.excelManager.parseExcel(file);
};

console.log('%c🏆 Excel Export Manager initialized (Worker-Based)', 'background:#f59e0b;color:white;padding:4px 12px;border-radius:4px;font-weight:600');
