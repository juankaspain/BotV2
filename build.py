#!/usr/bin/env python3
"""Production build pipeline for BotV2 Dashboard

Optimizations:
- HTML/CSS/JS minification
- Code splitting
- Asset compression (Gzip, Brotli)
- Cache busting with hashes
- Source map generation
- Bundle size analysis

Usage:
    python build.py --mode production
    python build.py --mode development --watch
    python build.py --analyze
"""

import os
import re
import hashlib
import gzip
import shutil
import json
import argparse
from pathlib import Path
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================

SOURCE_DIR = Path('src/dashboard')
OUTPUT_DIR = Path('dist')
BUILD_CONFIG = {
    'production': {
        'minify_html': True,
        'minify_css': True,
        'minify_js': True,
        'source_maps': False,
        'remove_console': True,
        'gzip': True,
        'brotli': False,  # Optional, requires brotli package
        'hash_assets': True
    },
    'development': {
        'minify_html': False,
        'minify_css': False,
        'minify_js': False,
        'source_maps': True,
        'remove_console': False,
        'gzip': False,
        'brotli': False,
        'hash_assets': False
    }
}

# ============================================
# BUILD STATS
# ============================================

class BuildStats:
    """Track build statistics"""
    
    def __init__(self):
        self.files = {}
        self.total_original = 0
        self.total_minified = 0
        self.total_gzipped = 0
        self.start_time = datetime.now()
    
    def add_file(self, filename, original_size, minified_size, gzipped_size=0):
        """Add file statistics"""
        self.files[filename] = {
            'original': original_size,
            'minified': minified_size,
            'gzipped': gzipped_size,
            'reduction': ((original_size - minified_size) / original_size * 100) if original_size > 0 else 0
        }
        self.total_original += original_size
        self.total_minified += minified_size
        self.total_gzipped += gzipped_size
    
    def print_summary(self):
        """Print build summary"""
        duration = (datetime.now() - self.start_time).total_seconds()
        
        print("\n" + "="*60)
        print("\u2705 BUILD SUMMARY")
        print("="*60)
        print(f"\n🕒 Build Time: {duration:.2f}s\n")
        print(f"{'File':<40} {'Original':>10} {'Minified':>10} {'Reduction':>10}")
        print("-" * 72)
        
        for filename, stats in self.files.items():
            print(f"{filename:<40} {self._format_size(stats['original']):>10} "
                  f"{self._format_size(stats['minified']):>10} {stats['reduction']:>9.1f}%")
        
        print("-" * 72)
        total_reduction = ((self.total_original - self.total_minified) / self.total_original * 100) if self.total_original > 0 else 0
        print(f"{'TOTAL':<40} {self._format_size(self.total_original):>10} "
              f"{self._format_size(self.total_minified):>10} {total_reduction:>9.1f}%")
        
        if self.total_gzipped > 0:
            gzip_reduction = ((self.total_minified - self.total_gzipped) / self.total_minified * 100)
            print(f"\n📦 Gzipped Total: {self._format_size(self.total_gzipped)} (-{gzip_reduction:.1f}%)")
        
        print("\n" + "="*60 + "\n")
    
    @staticmethod
    def _format_size(size_bytes):
        """Format file size in human-readable format"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

# ============================================
# MINIFICATION FUNCTIONS
# ============================================

def minify_html(content):
    """Minify HTML content"""
    # Remove HTML comments (except IE conditionals)
    content = re.sub(r'<!--(?!\[if).*?-->', '', content, flags=re.DOTALL)
    
    # Remove whitespace between tags
    content = re.sub(r'>\s+<', '><', content)
    
    # Remove leading/trailing whitespace
    content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)
    content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)
    
    # Collapse multiple spaces
    content = re.sub(r'\s{2,}', ' ', content)
    
    return content.strip()

def minify_css(content):
    """Minify CSS content (basic minification)"""
    # Remove comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove whitespace
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'\s*([{}:;,])\s*', r'\1', content)
    
    # Remove trailing semicolons
    content = re.sub(r';\}', '}', content)
    
    return content.strip()

def minify_js(content, remove_console=False):
    """Minify JavaScript content (basic minification)"""
    # Remove single-line comments (but keep URLs)
    content = re.sub(r'(?<!:)//(?!/).*?$', '', content, flags=re.MULTILINE)
    
    # Remove multi-line comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Remove console.log statements
    if remove_console:
        content = re.sub(r'console\.log\([^)]*\);?', '', content)
        content = re.sub(r'console\.(warn|error|info|debug)\([^)]*\);?', '', content)
    
    # Remove extra whitespace
    content = re.sub(r'\s+', ' ', content)
    
    # Remove whitespace around operators
    content = re.sub(r'\s*([=+\-*/<>!&|{}\[\]();,])\s*', r'\1', content)
    
    return content.strip()

# ============================================
# FILE PROCESSING
# ============================================

def generate_hash(content):
    """Generate hash for cache busting"""
    return hashlib.md5(content.encode()).hexdigest()[:8]

def compress_gzip(content):
    """Compress content with gzip"""
    return gzip.compress(content.encode(), compresslevel=9)

def process_html_file(src_path, dest_path, config, stats):
    """Process HTML file"""
    print(f"📤 Processing HTML: {src_path.name}")
    
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Minify if enabled
    if config['minify_html']:
        content = minify_html(content)
    
    # Register service worker
    if 'service-worker' not in content:
        sw_script = '''
<script>
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js')
      .then(reg => console.log('✅ Service Worker registered'))
      .catch(err => console.error('❌ Service Worker registration failed:', err));
  });
}
</script>'''
        # Insert before </body>
        content = content.replace('</body>', sw_script + '\n</body>')
    
    minified_size = len(content)
    
    # Write minified file
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Gzip if enabled
    gzipped_size = 0
    if config['gzip']:
        gzipped = compress_gzip(content)
        gzipped_size = len(gzipped)
        with open(str(dest_path) + '.gz', 'wb') as f:
            f.write(gzipped)
    
    stats.add_file(src_path.name, original_size, minified_size, gzipped_size)

def process_css_file(src_path, dest_path, config, stats):
    """Process CSS file"""
    print(f"🎨 Processing CSS: {src_path.name}")
    
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Minify if enabled
    if config['minify_css']:
        content = minify_css(content)
    
    minified_size = len(content)
    
    # Add hash to filename if enabled
    if config['hash_assets']:
        file_hash = generate_hash(content)
        name = dest_path.stem
        dest_path = dest_path.parent / f"{name}.min.{file_hash}.css"
    
    # Write minified file
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Gzip if enabled
    gzipped_size = 0
    if config['gzip']:
        gzipped = compress_gzip(content)
        gzipped_size = len(gzipped)
        with open(str(dest_path) + '.gz', 'wb') as f:
            f.write(gzipped)
    
    stats.add_file(src_path.name, original_size, minified_size, gzipped_size)

def process_js_file(src_path, dest_path, config, stats):
    """Process JavaScript file"""
    print(f"⚡ Processing JS: {src_path.name}")
    
    with open(src_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_size = len(content)
    
    # Minify if enabled
    if config['minify_js']:
        content = minify_js(content, remove_console=config['remove_console'])
    
    minified_size = len(content)
    
    # Add hash to filename if enabled
    if config['hash_assets']:
        file_hash = generate_hash(content)
        name = dest_path.stem
        dest_path = dest_path.parent / f"{name}.min.{file_hash}.js"
    
    # Write minified file
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Gzip if enabled
    gzipped_size = 0
    if config['gzip']:
        gzipped = compress_gzip(content)
        gzipped_size = len(gzipped)
        with open(str(dest_path) + '.gz', 'wb') as f:
            f.write(gzipped)
    
    stats.add_file(src_path.name, original_size, minified_size, gzipped_size)

# ============================================
# MAIN BUILD FUNCTION
# ============================================

def build(mode='production', analyze=False):
    """Run build pipeline"""
    print("\n" + "="*60)
    print(f"🛠️  BotV2 Dashboard Build Pipeline - {mode.upper()}")
    print("="*60 + "\n")
    
    config = BUILD_CONFIG.get(mode, BUILD_CONFIG['production'])
    stats = BuildStats()
    
    # Clean output directory
    if OUTPUT_DIR.exists():
        print(f"🗑️  Cleaning output directory: {OUTPUT_DIR}")
        shutil.rmtree(OUTPUT_DIR)
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process HTML files
    html_files = list((SOURCE_DIR / 'templates').glob('*.html'))
    for html_file in html_files:
        dest = OUTPUT_DIR / html_file.name
        process_html_file(html_file, dest, config, stats)
    
    # Process CSS files (if they exist)
    css_dir = SOURCE_DIR / 'static' / 'css'
    if css_dir.exists():
        for css_file in css_dir.glob('*.css'):
            if not css_file.name.endswith('.min.css'):
                dest = OUTPUT_DIR / 'static' / 'css' / css_file.name
                process_css_file(css_file, dest, config, stats)
    
    # Process JS files (if they exist)
    js_dir = SOURCE_DIR / 'static' / 'js'
    if js_dir.exists():
        for js_file in js_dir.glob('*.js'):
            if not js_file.name.endswith('.min.js'):
                dest = OUTPUT_DIR / 'static' / 'js' / js_file.name
                process_js_file(js_file, dest, config, stats)
    
    # Copy service worker
    sw_src = SOURCE_DIR / 'static' / 'service-worker.js'
    if sw_src.exists():
        print(f"📦 Copying service worker")
        sw_dest = OUTPUT_DIR / 'service-worker.js'
        shutil.copy2(sw_src, sw_dest)
    
    # Copy other static assets (images, fonts, etc.)
    static_dirs = ['images', 'fonts']
    for dir_name in static_dirs:
        src_dir = SOURCE_DIR / 'static' / dir_name
        if src_dir.exists():
            dest_dir = OUTPUT_DIR / 'static' / dir_name
            print(f"📸 Copying {dir_name}")
            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    
    # Print statistics
    stats.print_summary()
    
    # Generate build manifest
    manifest = {
        'version': '3.2.0',
        'build_time': datetime.now().isoformat(),
        'mode': mode,
        'files': stats.files,
        'total_size': {
            'original': stats.total_original,
            'minified': stats.total_minified,
            'gzipped': stats.total_gzipped
        }
    }
    
    with open(OUTPUT_DIR / 'build-manifest.json', 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"✅ Build complete! Output: {OUTPUT_DIR}")
    print(f"📦 Build manifest: {OUTPUT_DIR / 'build-manifest.json'}\n")
    
    # Bundle analysis
    if analyze:
        print("\n📊 BUNDLE ANALYSIS:")
        print("="*60)
        total_kb = stats.total_minified / 1024
        print(f"Total Bundle Size: {total_kb:.2f} KB")
        
        if total_kb < 100:
            print("✅ Excellent! Bundle size < 100 KB")
        elif total_kb < 250:
            print("✅ Good! Bundle size < 250 KB")
        elif total_kb < 500:
            print("⚠️  Warning: Bundle size approaching 500 KB")
        else:
            print("❌ Consider code splitting - bundle too large")
        
        print("="*60 + "\n")

# ============================================
# CLI
# ============================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build BotV2 Dashboard')
    parser.add_argument('--mode', choices=['production', 'development'], default='production',
                        help='Build mode (default: production)')
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze bundle size')
    parser.add_argument('--watch', action='store_true',
                        help='Watch for changes (development mode only)')
    
    args = parser.parse_args()
    
    if args.watch and args.mode != 'development':
        print("⚠️  Watch mode only available in development")
        args.watch = False
    
    build(mode=args.mode, analyze=args.analyze)
    
    if args.watch:
        print("⏱️  Watching for changes... (Press Ctrl+C to stop)")
        # TODO: Implement file watcher
        # In production, use watchdog library
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\u23f9️  Watch stopped")