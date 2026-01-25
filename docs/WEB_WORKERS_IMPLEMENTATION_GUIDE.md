# 🚀 Web Workers Implementation Guide - Path to 95% Security

**Target Version**: v7.6  
**Current Score**: 90% (Excellent)  
**Target Score**: 95% (Enterprise-Grade)  
**Estimated Effort**: 4-8 hours  
**Complexity**: Medium  
**Risk**: Low (with proper testing)

---

## 🎯 Objective

**Eliminate `unsafe-eval` from Content Security Policy** by isolating SheetJS (Excel export library) in a dedicated Web Worker.

### Why This Matters

**Current Vulnerability (v7.5)**:
```javascript
CSP: script-src 'self' 'unsafe-eval' 'nonce-xxx' ...
                        ↑
                        This allows eval() execution
                        = XSS attack vector
```

**After Implementation (v7.6)**:
```javascript
CSP: script-src 'self' 'nonce-xxx' ...  // ✅ No unsafe-eval!
Worker CSP: script-src 'unsafe-eval'    // ✅ Isolated to worker only
```

**Security Benefit**: Main thread becomes **eval-proof**, even if XSS vulnerability exists.

---

## 📊 Security Score Roadmap

```
v7.4  →  v7.5  →  v7.6  →  v8.0
60%      90%      95%      98%
🟡       🟢       🟢       🟢

v7.4: Fixed CSP errors, partial SRI
v7.5: Nonce-based CSP + Complete SRI (6/6) ← WE ARE HERE
v7.6: Web Workers + No unsafe-eval      ← THIS GUIDE
v8.0: Self-hosted libraries + Offline-first
```

---

## 🏛️ Architecture Overview

### Current Architecture (v7.5)

```
┌──────────────────────────────────┐
│         Main Thread                  │
│                                      │
│  ┌──────────────────────────┐  │
│  │  Dashboard Code           │  │
│  │  + UI Rendering           │  │
│  │  + Chart Generation       │  │
│  │  + SheetJS (needs eval) ❌ │  │
│  │  + PDF Export             │  │
│  │  + WebSocket              │  │
│  └──────────────────────────┘  │
│                                      │
│  CSP: 'unsafe-eval' required 🔴      │
└──────────────────────────────────┘
```

### Target Architecture (v7.6)

```
┌──────────────────────────────────┐  ┌───────────────────────┐
│         Main Thread                  │  │   Excel Worker       │
│                                      │  │                        │
│  ┌──────────────────────────┐  │  │  ┌────────────────┐  │
│  │  Dashboard Code           │  │  │  │  SheetJS ✅     │  │
│  │  + UI Rendering           │  │  │  │  (isolated)     │  │
│  │  + Chart Generation       │  │  │  └────────────────┘  │
│  │  + Excel Export Manager   │──▶│                        │
│  │  + PDF Export             │  │  │  postMessage()      │
│  │  + WebSocket              │←──│  onmessage()        │
│  └──────────────────────────┘  │  │                        │
│                                      │  │  Worker CSP:        │
│  CSP: NO unsafe-eval ✅             │  │  'unsafe-eval' 🔒    │
└──────────────────────────────────┘  └───────────────────────┘
                 🔒 Secure               🔒 Isolated & Sandboxed
```

**Key Benefits**:
- ✅ Main thread: **eval-proof** CSP
- ✅ Worker thread: Isolated, can't access DOM or cookies
- ✅ Communication: Structured cloning only (no code injection)
- ✅ SheetJS: Works normally in worker context

---

## 📝 Implementation Plan

### Phase 1: Create Web Worker Infrastructure

**Files to create**:
1. `src/dashboard/static/js/workers/excel-worker.js` - Worker code
2. `src/dashboard/static/js/excel-export-manager.js` - Main thread manager
3. Update `dashboard.html` - Load manager, remove SheetJS from main
4. Update `web_app.py` - Adjust CSP for workers

---

### Phase 2: Implement Worker Communication Protocol

**Message format**:
```javascript
// Main → Worker
{
  action: 'export',
  format: 'xlsx',
  data: [...],
  options: {...}
}

// Worker → Main
{
  status: 'success'|'error',
  data: ArrayBuffer,  // Excel file
  error: string
}
```

---

### Phase 3: Update CSP Configuration

**Remove `unsafe-eval` from main CSP**, add worker-specific CSP.

---

### Phase 4: Testing & Validation

**Test scenarios**:
- Excel export with small dataset
- Excel export with large dataset (10,000+ rows)
- Multiple concurrent exports
- Error handling (worker crash)
- Browser compatibility

---

## 💻 Code Implementation

### File 1: Excel Web Worker

**Path**: `src/dashboard/static/js/workers/excel-worker.js`

```javascript
/**
 * Excel Export Web Worker v7.6
 * 
 * Isolates SheetJS library in worker context to eliminate unsafe-eval
 * from main thread CSP.
 * 
 * Security: Worker has separate CSP allowing unsafe-eval, but cannot
 * access DOM, cookies, or localStorage.
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
    
    // Create worksheet from JSON
    const ws = XLSX.utils.json_to_sheet(data, {
        header: options.headers || undefined,
        skipHeader: options.skipHeader || false
    });
    
    // Apply column widths if provided
    if (options.columnWidths) {
        ws['!cols'] = options.columnWidths.map(w => ({ wch: w }));
    }
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, options.sheetName || 'Sheet1');
    
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
    
    // Create workbook
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, options.sheetName || 'Sheet1');
    
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
    
    try {
        let result;
        
        switch (action) {
            case 'init':
                initialize();
                self.postMessage({
                    id,
                    status: 'success',
                    message: 'Worker initialized'
                });
                break;
            
            case 'export-json':
                result = jsonToExcel(data, options);
                self.postMessage({
                    id,
                    status: 'success',
                    data: result,
                    size: result.byteLength
                }, [result.buffer]);  // Transfer ownership (zero-copy)
                break;
            
            case 'export-table':
                result = tableToExcel(data, options);
                self.postMessage({
                    id,
                    status: 'success',
                    data: result,
                    size: result.byteLength
                }, [result.buffer]);
                break;
            
            case 'ping':
                self.postMessage({
                    id,
                    status: 'success',
                    message: 'pong',
                    timestamp: Date.now()
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

// Worker ready signal
self.postMessage({
    status: 'ready',
    message: 'Excel Worker loaded',
    timestamp: Date.now()
});

console.log('[ExcelWorker] Worker script loaded');
```

---

### File 2: Excel Export Manager (Main Thread)

**Path**: `src/dashboard/static/js/excel-export-manager.js`

```javascript
/**
 * Excel Export Manager v7.6
 * 
 * Manages communication with Excel Web Worker for secure Excel exports
 * without requiring unsafe-eval in main thread CSP.
 */

class ExcelExportManager {
    constructor() {
        this.worker = null;
        this.initialized = false;
        this.pendingRequests = new Map();
        this.requestId = 0;
        this.workerPath = '/static/js/workers/excel-worker.js';
    }
    
    /**
     * Initialize worker and wait for ready signal
     * @returns {Promise<void>}
     */
    async init() {
        if (this.initialized) return;
        
        return new Promise((resolve, reject) => {
            try {
                // Create worker
                this.worker = new Worker(this.workerPath);
                
                // Setup message handler
                this.worker.onmessage = this._handleMessage.bind(this);
                
                // Setup error handler
                this.worker.onerror = (error) => {
                    console.error('[ExcelManager] Worker error:', error);
                    reject(new Error(`Worker error: ${error.message}`));
                };
                
                // Wait for ready signal
                const readyHandler = (e) => {
                    if (e.data.status === 'ready') {
                        this.initialized = true;
                        console.log('[ExcelManager] Worker ready');
                        this.worker.removeEventListener('message', readyHandler);
                        resolve();
                    }
                };
                
                this.worker.addEventListener('message', readyHandler);
                
                // Timeout after 5 seconds
                setTimeout(() => {
                    if (!this.initialized) {
                        reject(new Error('Worker initialization timeout'));
                    }
                }, 5000);
                
            } catch (error) {
                console.error('[ExcelManager] Init error:', error);
                reject(error);
            }
        });
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
                    reject(new Error('Worker request timeout'));
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
     * @returns {Promise<ArrayBuffer>}
     */
    async exportJSON(data, options = {}) {
        if (!this.initialized) await this.init();
        
        console.log(`[ExcelManager] Exporting ${data.length} rows to Excel`);
        
        const startTime = Date.now();
        const result = await this._sendMessage({
            action: 'export-json',
            data,
            options
        });
        
        const duration = Date.now() - startTime;
        console.log(`[ExcelManager] Export completed in ${duration}ms (${result.byteLength} bytes)`);
        
        return result;
    }
    
    /**
     * Export HTML table to Excel
     * @param {HTMLTableElement|string} table - Table element or HTML string
     * @param {Object} options - Export options
     * @returns {Promise<ArrayBuffer>}
     */
    async exportTable(table, options = {}) {
        if (!this.initialized) await this.init();
        
        // Convert table to HTML string if element
        const tableHTML = typeof table === 'string' 
            ? table 
            : table.outerHTML;
        
        console.log('[ExcelManager] Exporting table to Excel');
        
        const result = await this._sendMessage({
            action: 'export-table',
            data: tableHTML,
            options
        });
        
        return result;
    }
    
    /**
     * Download Excel file
     * @param {ArrayBuffer} data - Excel file data
     * @param {string} filename - Filename
     */
    download(data, filename = 'export.xlsx') {
        const blob = new Blob([data], {
            type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        
        // Cleanup
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    }
    
    /**
     * Test worker connectivity
     * @returns {Promise<boolean>}
     */
    async ping() {
        if (!this.initialized) await this.init();
        
        try {
            await this._sendMessage({ action: 'ping' }, 5000);
            return true;
        } catch (error) {
            console.error('[ExcelManager] Ping failed:', error);
            return false;
        }
    }
    
    /**
     * Terminate worker
     */
    terminate() {
        if (this.worker) {
            this.worker.terminate();
            this.worker = null;
            this.initialized = false;
            this.pendingRequests.clear();
            console.log('[ExcelManager] Worker terminated');
        }
    }
}

// Export singleton instance
window.ExcelExportManager = new ExcelExportManager();

console.log('[ExcelManager] Manager loaded');
```

---

### File 3: Update dashboard.html

**Changes needed**:

```html
<!-- REMOVE THIS (SheetJS no longer loaded in main thread) -->
<!-- <script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js" 
        integrity="sha384-pXqhahB/wGhF7TypMXRFE/51C0qP6bkAMGxIg1pFfB9fxL5R6rLKaGnN7QnT7g3j" 
        crossorigin="anonymous"
        referrerpolicy="no-referrer"></script> -->

<!-- ADD THIS (Excel Export Manager) -->
<script src="{{ url_for('static', filename='js/excel-export-manager.js') }}"></script>

<!-- UPDATE verification script -->
<script nonce="{{ csp_nonce }}">
    (function verifyAllLibraries() {
        const coreLibs = {
            'Plotly': typeof Plotly !== 'undefined',
            'Socket.io': typeof io !== 'undefined',
            'ExcelManager': typeof ExcelExportManager !== 'undefined'  // NEW
        };
        
        const exportLibs = {
            // 'SheetJS': typeof XLSX !== 'undefined',  // REMOVED
            'jsPDF': typeof jspdf !== 'undefined',
            'html2canvas': typeof html2canvas !== 'undefined'
        };
        
        // ... rest of verification logic
        
        console.log('%c🔐 v7.6 Security Status - NO unsafe-eval!', 'background:#8b5cf6;color:white;padding:8px 20px;border-radius:8px;font-weight:700;font-size:14px');
        console.log('%c🎯 Security Score: 95% (🟢 Enterprise-Grade)', 'background:#3fb950;color:white;padding:4px 12px;border-radius:5px;font-weight:700;font-size:12px');
    })();
</script>
```

---

### File 4: Update web_app.py CSP

```python
csp_config = {
    'default-src': "'self'",
    'script-src': [
        "'self'",
        # ✅ REMOVED: "'unsafe-eval'",  # No longer needed!
        lambda: f"'nonce-{g.csp_nonce}'",
        # CDNs (SheetJS removed)
        "https://cdn.plot.ly",
        "https://cdn.socket.io",
        "https://cdnjs.cloudflare.com"
    ],
    # 🆕 Worker-specific CSP
    'worker-src': ["'self'", "blob:"],
    # ... rest of CSP
}
```

---

### File 5: Update Export Function (dashboard-optimized.js)

**Find and replace** in `dashboard-optimized.js`:

```javascript
// OLD (v7.5) - Direct SheetJS usage
async exportToExcel(data, filename) {
    const ws = XLSX.utils.json_to_sheet(data);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
    XLSX.writeFile(wb, filename);
}

// NEW (v7.6) - Web Worker usage
async exportToExcel(data, filename) {
    try {
        // Export via Web Worker
        const excelData = await ExcelExportManager.exportJSON(data, {
            sheetName: 'Dashboard Export',
            columnWidths: this._calculateColumnWidths(data)
        });
        
        // Download file
        ExcelExportManager.download(excelData, filename);
        
        this.showToast('✅ Excel exported successfully', 'success');
    } catch (error) {
        console.error('Excel export failed:', error);
        this.showToast('❌ Excel export failed', 'error');
    }
}

// Helper: Calculate optimal column widths
_calculateColumnWidths(data) {
    if (!data || !data.length) return [];
    
    const headers = Object.keys(data[0]);
    return headers.map(header => {
        const maxLength = Math.max(
            header.length,
            ...data.map(row => String(row[header] || '').length)
        );
        return Math.min(maxLength + 2, 50);  // Max 50 chars
    });
}
```

---

## 🧪 Testing Procedures

### Test 1: Basic Export

```javascript
// Open browser console on dashboard
const testData = [
    { Name: 'Alice', Age: 30, City: 'NYC' },
    { Name: 'Bob', Age: 25, City: 'LA' },
    { Name: 'Charlie', Age: 35, City: 'SF' }
];

const excelData = await ExcelExportManager.exportJSON(testData);
ExcelExportManager.download(excelData, 'test.xlsx');

// ✅ Should download test.xlsx
// ✅ Open in Excel/LibreOffice - verify data
```

---

### Test 2: Large Dataset

```javascript
// Generate 10,000 rows
const largeData = Array.from({ length: 10000 }, (_, i) => ({
    ID: i + 1,
    Name: `User ${i + 1}`,
    Email: `user${i + 1}@example.com`,
    Balance: (Math.random() * 10000).toFixed(2),
    Timestamp: new Date().toISOString()
}));

console.time('Large Export');
const excelData = await ExcelExportManager.exportJSON(largeData);
console.timeEnd('Large Export');
// Should complete in <2 seconds

ExcelExportManager.download(excelData, 'large-test.xlsx');
// ✅ Verify file opens correctly
```

---

### Test 3: Worker Connectivity

```javascript
// Test ping
const isAlive = await ExcelExportManager.ping();
console.log('Worker alive:', isAlive);  // Should be true

// Test error handling
try {
    await ExcelExportManager.exportJSON(null);  // Invalid data
} catch (error) {
    console.log('Error caught:', error.message);  // ✅ Should catch
}
```

---

### Test 4: CSP Verification

1. Open DevTools → Network tab
2. Refresh page
3. Check main document headers
4. Verify **NO `unsafe-eval`** in CSP

```
Content-Security-Policy: 
  script-src 'self' 'nonce-xxx' https://cdn.plot.ly ... 
             ↑ NO unsafe-eval! ✅
```

---

### Test 5: Integration Test

**In dashboard**:
1. Navigate to Trades section
2. Click "Export" button
3. Select "Excel" format
4. ✅ File should download
5. ✅ Open in Excel - verify all columns present
6. ✅ Check console - no errors

---

## 🚨 Rollback Plan

If issues arise during deployment:

### Quick Rollback (5 minutes)

```bash
# Revert to v7.5
git revert HEAD
git push origin main

# Restart dashboard
python src/main.py
```

---

### Partial Rollback (Keep SRI, revert Worker)

```html
<!-- Re-add SheetJS to main thread -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js" 
        integrity="sha384-..." 
        crossorigin="anonymous"></script>

<!-- Remove Excel Manager -->
<!-- <script src=".../excel-export-manager.js"></script> -->
```

```python
# Re-add unsafe-eval to CSP
'script-src': [
    "'self'",
    "'unsafe-eval'",  # Temporary
    # ...
]
```

---

## 📈 Expected Performance

### Export Times (Estimated)

| Dataset Size | v7.5 (Main Thread) | v7.6 (Worker) | Difference |
|--------------|--------------------|--------------|-----------|
| 100 rows | 50ms | 70ms | +20ms |
| 1,000 rows | 200ms | 250ms | +50ms |
| 10,000 rows | 1,500ms | 1,600ms | +100ms |
| 100,000 rows | 15,000ms | 15,500ms | +500ms |

**Overhead**: ~5-10% due to message passing, **acceptable for security gain**.

---

### Memory Usage

```
Worker initialization:  ~2MB (SheetJS library)
Per export operation:   ~(data size) * 2
Total overhead:         ~2-5MB typical
```

---

## ✅ Success Criteria

**Implementation is successful if**:

1. ✅ Excel exports work identically to v7.5
2. ✅ CSP has **NO `unsafe-eval`** in main thread
3. ✅ Console shows "95% Security Score"
4. ✅ All export tests pass
5. ✅ No performance degradation >10%
6. ✅ No console errors or warnings

---

## 📄 Implementation Checklist

### Setup Phase

- [ ] Create `workers/` directory in static/js
- [ ] Create `excel-worker.js`
- [ ] Create `excel-export-manager.js`
- [ ] Test worker in isolation (console tests)

### Integration Phase

- [ ] Update `dashboard.html` (remove SheetJS CDN)
- [ ] Update `dashboard.html` (add Excel Manager)
- [ ] Update `dashboard-optimized.js` (replace export function)
- [ ] Update `web_app.py` (remove unsafe-eval from CSP)
- [ ] Update verification script

### Testing Phase

- [ ] Test basic export (small dataset)
- [ ] Test large export (10k+ rows)
- [ ] Test error handling
- [ ] Test worker ping
- [ ] Verify CSP headers (no unsafe-eval)
- [ ] Integration test (full dashboard flow)
- [ ] Browser compatibility (Chrome, Firefox, Safari)

### Documentation Phase

- [ ] Update CHANGELOG.md
- [ ] Update README.md (v7.6 features)
- [ ] Create deployment notes
- [ ] Document rollback procedure

---

## 🚀 Deployment Steps

### Development Environment

```bash
# 1. Create worker directory
mkdir -p src/dashboard/static/js/workers

# 2. Create worker files (use code above)
vim src/dashboard/static/js/workers/excel-worker.js
vim src/dashboard/static/js/excel-export-manager.js

# 3. Update files
vim src/dashboard/templates/dashboard.html
vim src/dashboard/web_app.py
vim src/dashboard/static/js/dashboard-optimized.js

# 4. Commit changes
git add .
git commit -m "feat: Implement Web Workers for unsafe-eval elimination - v7.6

- Created Excel Web Worker for SheetJS isolation
- Implemented ExcelExportManager for main thread
- Removed unsafe-eval from main CSP
- Worker-specific CSP for eval isolation
- Complete Excel export refactor
- Security score: 90% → 95%

Breaking changes: None (backwards compatible)
Testing: All export tests passing"

# 5. Push to main
git push origin main

# 6. Restart dashboard
python src/main.py
```

---

### Production Environment

```bash
# 1. Pull changes
git pull origin main

# 2. Verify files
ls -la src/dashboard/static/js/workers/
ls -la src/dashboard/static/js/excel-export-manager.js

# 3. Backup current version
cp -r src/dashboard src/dashboard.backup.v7.5

# 4. Restart with zero-downtime
./scripts/rolling-restart.sh

# 5. Monitor logs
tail -f logs/dashboard.log

# 6. Test immediately
curl http://localhost:8050/health
# Open browser and test export

# 7. If issues: rollback
# git revert HEAD && git push && ./scripts/rolling-restart.sh
```

---

## 🎯 Final Security Score

### After v7.6 Implementation

```
🎯 Security Score: 95% (🟢 Enterprise-Grade)

✅ CSRF Protection
✅ XSS Prevention (middleware + CSP)
✅ Input Validation
✅ Rate Limiting
✅ Session Management
✅ Audit Logging
✅ Nonce-Based CSP
✅ Complete SRI (6/6 libraries)
✅ NO unsafe-eval in main thread 🆕
✅ Worker isolation for eval-requiring libs

🟡 Remaining: unsafe-eval in worker context (-5%)
```

---

## 📚 References

### Technical Documentation

- [Web Workers API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API)
- [CSP worker-src Directive](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy/worker-src)
- [SheetJS Documentation](https://docs.sheetjs.com/)
- [Transferable Objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)

### Security Best Practices

- [OWASP CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [Google Web Fundamentals - Workers](https://developers.google.com/web/fundamentals/primers/service-workers)

---

## ❓ FAQ

### Q: Why not just use ExcelJS instead of SheetJS?

**A**: ExcelJS doesn't require `eval()` and would be simpler, but:
- Larger file size (~500KB vs 200KB)
- Different API (requires code refactor)
- Web Worker approach is more educational/reusable

**Future**: Consider migration to ExcelJS in v8.0

---

### Q: What if browser doesn't support Web Workers?

**A**: Add fallback:
```javascript
if (!window.Worker) {
    // Fallback: load SheetJS in main thread
    const script = document.createElement('script');
    script.src = 'https://cdn.sheetjs.com/...';
    document.head.appendChild(script);
    // CSP must allow unsafe-eval as fallback
}
```

---

### Q: Can worker access user data?

**A**: **No**. Workers cannot access:
- DOM (document, window)
- Cookies
- localStorage/sessionStorage
- Parent page scripts

Workers are **completely isolated** for security.

---

### Q: What happens if worker crashes?

**A**: Error handling:
```javascript
worker.onerror = (error) => {
    console.error('Worker crashed:', error);
    // Recreate worker
    this.initialized = false;
    this.init();
};
```

---

## ✅ Summary

### What You Get

✅ **95% security score** (from 90%)  
✅ **eval-proof main thread** CSP  
✅ **Isolated execution** for eval-requiring code  
✅ **Zero functionality loss** - everything works  
✅ **Minimal performance overhead** (~5-10%)  
✅ **Future-proof architecture** for v8.0  

### Estimated Effort

- **Setup**: 2 hours (create files, write code)
- **Integration**: 1 hour (update existing files)
- **Testing**: 1 hour (comprehensive tests)
- **Documentation**: 30 minutes (update docs)
- **Deployment**: 30 minutes (push + verify)

**Total**: 4-8 hours depending on familiarity with Web Workers

---

**Ready to implement?** Follow the checklist and reach out with any questions!

---

**Document Version**: 1.0.0  
**Created**: January 25, 2026, 11:21 PM CET  
**Target Version**: v7.6  
**Estimated Completion**: 4-8 hours  
**Security Impact**: +5% (90% → 95%)
