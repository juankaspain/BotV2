/**
 * BotV2 Dashboard v7.4 - Unit Tests
 * Comprehensive test suite for dashboard functionality
 * 
 * @author Juan Carlos Garcia
 * @version 7.4.0
 * @date 25-01-2026
 * 
 * How to run:
 * 1. Open browser console
 * 2. Run: DashboardTests.runAll()
 * 3. View results in console
 */

'use strict';

const DashboardTests = (() => {
    
    const results = {
        passed: 0,
        failed: 0,
        errors: []
    };
    
    // ==================== TEST UTILITIES ====================
    
    const assert = {
        equal: (actual, expected, message) => {
            if (actual !== expected) {
                throw new Error(`${message}: expected ${expected}, got ${actual}`);
            }
        },
        
        notEqual: (actual, notExpected, message) => {
            if (actual === notExpected) {
                throw new Error(`${message}: expected not ${notExpected}, got ${actual}`);
            }
        },
        
        truthy: (value, message) => {
            if (!value) {
                throw new Error(`${message}: expected truthy value, got ${value}`);
            }
        },
        
        falsy: (value, message) => {
            if (value) {
                throw new Error(`${message}: expected falsy value, got ${value}`);
            }
        },
        
        exists: (value, message) => {
            if (value === undefined || value === null) {
                throw new Error(`${message}: value should exist`);
            }
        },
        
        typeOf: (value, type, message) => {
            if (typeof value !== type) {
                throw new Error(`${message}: expected type ${type}, got ${typeof value}`);
            }
        },
        
        arrayLength: (array, length, message) => {
            if (!Array.isArray(array) || array.length !== length) {
                throw new Error(`${message}: expected array of length ${length}, got ${array?.length}`);
            }
        },
        
        contains: (array, item, message) => {
            if (!array.includes(item)) {
                throw new Error(`${message}: array does not contain ${item}`);
            }
        }
    };
    
    const test = (name, fn) => {
        try {
            fn();
            console.log(`%c✅ PASS%c ${name}`, 'background:#10b981;color:white;padding:2px 6px;border-radius:3px;font-weight:600', 'color:#7d8590');
            results.passed++;
        } catch (error) {
            console.error(`%c❌ FAIL%c ${name}`, 'background:#f85149;color:white;padding:2px 6px;border-radius:3px;font-weight:600', 'color:#7d8590');
            console.error('  Error:', error.message);
            results.failed++;
            results.errors.push({ test: name, error: error.message });
        }
    };
    
    // ==================== LOGGER TESTS ====================
    
    const testLogger = () => {
        console.group('%c🚨 Logger Tests', 'font-weight:700;color:#2f81f7');
        
        test('Logger exists', () => {
            assert.exists(Logger, 'Logger should be defined');
        });
        
        test('Logger has required methods', () => {
            const methods = ['system', 'success', 'warn', 'error', 'chart', 'data', 'ws', 'cache', 'modal', 'filter', 'export'];
            methods.forEach(method => {
                assert.typeOf(Logger[method], 'function', `Logger.${method} should be a function`);
            });
        });
        
        test('Logger.perf has start and end', () => {
            assert.typeOf(Logger.perf.start, 'function', 'Logger.perf.start should be a function');
            assert.typeOf(Logger.perf.end, 'function', 'Logger.perf.end should be a function');
        });
        
        test('Logger methods work without throwing', () => {
            Logger.system('Test message');
            Logger.success('Test success');
            Logger.warn('Test warning');
            Logger.error('Test error', new Error('Mock error'));
        });
        
        console.groupEnd();
    };
    
    // ==================== STATE TESTS ====================
    
    const testState = () => {
        console.group('%c📦 State Tests', 'font-weight:700;color:#2f81f7');
        
        test('AppState exists', () => {
            assert.exists(AppState, 'AppState should be defined');
        });
        
        test('AppState has required properties', () => {
            const props = ['currentSection', 'currentTheme', 'chartInstances', 'activeFilters', 'comparisonMode'];
            props.forEach(prop => {
                assert.exists(AppState[prop], `AppState.${prop} should exist`);
            });
        });
        
        test('Config has required properties', () => {
            assert.exists(Config.maxDataPoints, 'Config.maxDataPoints should exist');
            assert.exists(Config.debounceDelay, 'Config.debounceDelay should exist');
            assert.exists(Config.localStorageKey, 'Config.localStorageKey should exist');
        });
        
        console.groupEnd();
    };
    
    // ==================== CACHE TESTS ====================
    
    const testCache = () => {
        console.group('%c💾 Cache Tests', 'font-weight:700;color:#2f81f7');
        
        test('sectionCache exists', () => {
            assert.exists(window.PerformanceOptimizer, 'PerformanceOptimizer should exist');
            assert.exists(window.PerformanceOptimizer.sectionCache, 'sectionCache should exist');
        });
        
        test('sectionCache can set and get', () => {
            const { sectionCache } = window.PerformanceOptimizer;
            const testData = { test: 'data' };
            sectionCache.set('test-section', testData);
            const retrieved = sectionCache.get('test-section');
            assert.exists(retrieved, 'Retrieved data should exist');
        });
        
        test('sectionCache returns null for non-existent keys', () => {
            const { sectionCache } = window.PerformanceOptimizer;
            const retrieved = sectionCache.get('non-existent-key-12345');
            assert.equal(retrieved, null, 'Should return null for non-existent key');
        });
        
        console.groupEnd();
    };
    
    // ==================== MODAL TESTS ====================
    
    const testModals = () => {
        console.group('%c🪟 Modal Tests', 'font-weight:700;color:#2f81f7');
        
        test('ModalSystem exists', () => {
            assert.exists(ModalSystem, 'ModalSystem should be defined');
        });
        
        test('ModalSystem has required methods', () => {
            assert.typeOf(ModalSystem.show, 'function', 'ModalSystem.show should be a function');
            assert.typeOf(ModalSystem.close, 'function', 'ModalSystem.close should be a function');
        });
        
        test('Modal overlay exists in DOM', () => {
            const overlay = document.getElementById('modalOverlay');
            assert.exists(overlay, 'Modal overlay should exist in DOM');
        });
        
        console.groupEnd();
    };
    
    // ==================== FILTER TESTS ====================
    
    const testFilters = () => {
        console.group('%c🔍 Filter Tests', 'font-weight:700;color:#2f81f7');
        
        test('AdvancedFilters exists', () => {
            assert.exists(AdvancedFilters, 'AdvancedFilters should be defined');
        });
        
        test('AdvancedFilters has required methods', () => {
            assert.typeOf(AdvancedFilters.apply, 'function', 'AdvancedFilters.apply should be a function');
            assert.typeOf(AdvancedFilters.clear, 'function', 'AdvancedFilters.clear should be a function');
        });
        
        test('Filters can be applied', () => {
            const chartId = 'test-chart';
            const filters = { dateFrom: '2025-01-01', dateTo: '2025-12-31' };
            AdvancedFilters.apply(chartId, filters);
            assert.exists(AppState.activeFilters[chartId], 'Filters should be stored in AppState');
        });
        
        test('Filters can be cleared', () => {
            const chartId = 'test-chart';
            AdvancedFilters.clear(chartId);
            assert.falsy(AppState.activeFilters[chartId], 'Filters should be cleared from AppState');
        });
        
        console.groupEnd();
    };
    
    // ==================== EXPORT TESTS ====================
    
    const testExport = () => {
        console.group('%c📥 Export Tests', 'font-weight:700;color:#2f81f7');
        
        test('ExportLibrary exists', () => {
            assert.exists(ExportLibrary, 'ExportLibrary should be defined');
        });
        
        test('ExportLibrary has required methods', () => {
            assert.typeOf(ExportLibrary.exportToCSV, 'function', 'ExportLibrary.exportToCSV should be a function');
            assert.typeOf(ExportLibrary.exportToExcel, 'function', 'ExportLibrary.exportToExcel should be a function');
            assert.typeOf(ExportLibrary.exportToPDF, 'function', 'ExportLibrary.exportToPDF should be a function');
        });
        
        test('ExportLibrary has correct version', () => {
            assert.equal(ExportLibrary.version, '7.4.0', 'ExportLibrary version should be 7.4.0');
        });
        
        test('ExportLibrary supported formats', () => {
            assert.contains(ExportLibrary.supportedFormats, 'csv', 'Should support CSV');
            assert.contains(ExportLibrary.supportedFormats, 'excel', 'Should support Excel');
            assert.contains(ExportLibrary.supportedFormats, 'pdf', 'Should support PDF');
        });
        
        test('ExportSystem exists', () => {
            assert.exists(ExportSystem, 'ExportSystem should be defined');
        });
        
        test('ExportSystem can gather data', () => {
            const data = ExportSystem.gatherExportData();
            assert.exists(data, 'Should return data');
            assert.truthy(Array.isArray(data) || typeof data === 'object', 'Data should be array or object');
        });
        
        console.groupEnd();
    };
    
    // ==================== ANALYTICS TESTS ====================
    
    const testAnalytics = () => {
        console.group('%c📊 Analytics Tests', 'font-weight:700;color:#2f81f7');
        
        test('AnalyticsManager exists', () => {
            assert.exists(AnalyticsManager, 'AnalyticsManager should be defined');
        });
        
        test('AnalyticsManager has required methods', () => {
            assert.typeOf(AnalyticsManager.track, 'function', 'AnalyticsManager.track should be a function');
            assert.typeOf(AnalyticsManager.trackPageView, 'function', 'AnalyticsManager.trackPageView should be a function');
            assert.typeOf(AnalyticsManager.trackError, 'function', 'AnalyticsManager.trackError should be a function');
        });
        
        test('AnalyticsManager can track events', () => {
            const initialLength = AnalyticsManager.events.length;
            AnalyticsManager.track('test_event', { test: 'data' });
            assert.truthy(AnalyticsManager.events.length > initialLength, 'Should add event to queue');
        });
        
        console.groupEnd();
    };
    
    // ==================== GLOBAL API TESTS ====================
    
    const testGlobalAPI = () => {
        console.group('%c🌐 Global API Tests', 'font-weight:700;color:#2f81f7');
        
        test('DashboardApp exists', () => {
            assert.exists(window.DashboardApp, 'DashboardApp should be exposed globally');
        });
        
        test('DashboardApp has required methods', () => {
            const methods = ['loadSection', 'showModal', 'closeModal', 'applyChartFilter', 'executeExport'];
            methods.forEach(method => {
                assert.typeOf(window.DashboardApp[method], 'function', `DashboardApp.${method} should be a function`);
            });
        });
        
        test('DashboardApp version is correct', () => {
            assert.equal(window.DashboardApp.version, '7.4.0', 'DashboardApp version should be 7.4.0');
        });
        
        console.groupEnd();
    };
    
    // ==================== RUN ALL TESTS ====================
    
    const runAll = () => {
        console.clear();
        console.log(
            `%c
` +
            `  ██████╗ ██████╗ ███████╗██╗   ██╗██████╗ 
` +
            `  ██╔══██╗██╔═══██╗╚══██╔══║██║   ██║╚════██╗
` +
            `  ██████╔╝██║   ██║   ██║   ██║   ██║ █████╔╝
` +
            `  ██╔══██╗██║   ██║   ██║   ╚██╗ ██╔╝██╔═══╝ 
` +
            `  ██████╔╝╚██████╔╝   ██║    ╚████╔╝ ███████╗
` +
            `  ╚═════╝  ╚═════╝    ╚═╝     ╚═══╝  ╚══════╝
` +
            `
%c  Dashboard v7.4 - Unit Tests  %c

`,
            'color:#2f81f7;font-weight:600',
            'background:#2f81f7;color:white;padding:4px 12px;border-radius:4px;font-weight:600',
            'color:#7d8590'
        );
        
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color:#30363d');
        
        // Reset results
        results.passed = 0;
        results.failed = 0;
        results.errors = [];
        
        // Run test suites
        testLogger();
        testState();
        testCache();
        testModals();
        testFilters();
        testExport();
        testAnalytics();
        testGlobalAPI();
        
        // Summary
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color:#30363d');
        console.log('');
        console.log('%c📋 TEST SUMMARY', 'background:#2f81f7;color:white;padding:4px 12px;border-radius:4px;font-weight:700');
        console.log('');
        console.log(`%c  ✅ Passed: ${results.passed}`, 'color:#10b981;font-weight:700');
        console.log(`%c  ❌ Failed: ${results.failed}`, 'color:#f85149;font-weight:700');
        console.log(`%c  📊 Total: ${results.passed + results.failed}`, 'color:#7d8590;font-weight:600');
        
        if (results.failed > 0) {
            console.log('');
            console.log('%c⚠️ FAILED TESTS:', 'background:#f85149;color:white;padding:2px 8px;border-radius:3px;font-weight:600');
            results.errors.forEach(({ test, error }) => {
                console.log(`  • ${test}: ${error}`);
            });
        }
        
        console.log('');
        console.log('%c━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━', 'color:#30363d');
        
        return {
            passed: results.passed,
            failed: results.failed,
            total: results.passed + results.failed,
            success: results.failed === 0,
            errors: results.errors
        };
    };
    
    // ==================== PUBLIC API ====================
    
    return {
        runAll,
        testLogger,
        testState,
        testCache,
        testModals,
        testFilters,
        testExport,
        testAnalytics,
        testGlobalAPI,
        getResults: () => ({ ...results })
    };
    
})();

// Export to global
window.DashboardTests = DashboardTests;

console.log('%c🧪 Unit Tests v7.4 loaded', 'background:#8338ec;color:white;padding:4px 8px;border-radius:3px;font-weight:600');
console.log('  Run: DashboardTests.runAll()');
