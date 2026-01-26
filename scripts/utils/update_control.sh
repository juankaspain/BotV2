#!/bin/bash

# BotV2 Control Panel Setup v4.2
# Run this to update web_app.py with control panel integration

echo "====================================="
echo "  BotV2 Control Panel v4.2 Setup"
echo "====================================="
echo ""

# Check if we're in the right directory
if [ ! -f "src/dashboard/web_app.py" ]; then
    echo "❌ Error: Must run from BotV2 root directory"
    exit 1
fi

echo "📋 Adding Control Panel integration to web_app.py..."

# Backup original
cp src/dashboard/web_app.py src/dashboard/web_app.py.backup

# Add control panel imports and routes
python3 << 'EOF'
import sys
sys.path.insert(0, 'src')

with open('src/dashboard/web_app.py', 'r') as f:
    content = f.read()

# Check if already integrated
if 'control_bp' in content:
    print("✓ Control Panel already integrated")
    sys.exit(0)

# Find where to insert
if 'from .ai_routes import ai_bp' in content:
    # Add after ai_routes import
    content = content.replace(
        'from .ai_routes import ai_bp',
        'from .ai_routes import ai_bp\nfrom .control_routes import control_bp'
    )
    print("✓ Added control_routes import")
else:
    print("⚠️  Could not find ai_routes import, adding at top")
    # Add after other imports
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('from flask'):
            lines.insert(i+1, 'from .control_routes import control_bp')
            break
    content = '\n'.join(lines)

# Register blueprint
if 'app.register_blueprint(ai_bp)' in content:
    content = content.replace(
        'app.register_blueprint(ai_bp)',
        'app.register_blueprint(ai_bp)\napp.register_blueprint(control_bp)'
    )
    print("✓ Registered control_bp blueprint")

# Add route
if '@app.route' in content:
    # Find a good place to add the route
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if '@app.route(\'/dashboard\')' in line or '@app.route(\"/dashboard\")' in line:
            # Add control panel route after dashboard route
            # Find the end of that function
            for j in range(i, len(lines)):
                if j > i and (lines[j].startswith('@app.route') or lines[j].startswith('if __name__')):
                    # Insert here
                    insert_code = '''
@app.route('/control')
@login_required
def control_panel():
    """Control panel page"""
    return render_template('control.html')
'''
                    lines.insert(j, insert_code)
                    print("✓ Added /control route")
                    break
            break
    content = '\n'.join(lines)

# Write back
with open('src/dashboard/web_app.py', 'w') as f:
    f.write(content)

print("✅ Integration complete!")
EOF

echo ""
echo "====================================="
echo "  ✅ Control Panel v4.2 Ready!"
echo "====================================="
echo ""
echo "URLs:"
echo "  Dashboard: http://localhost:8050/dashboard"
echo "  Control Panel: http://localhost:8050/control"
echo ""
echo "Next steps:"
echo "1. Restart dashboard: bash UPDATE.sh"
echo "2. Login and navigate to Control Panel"
echo "3. Start managing your bot!"
echo ""
