#!/usr/bin/env python3
"""
ADD THIS TO web_app.py

Insert after other blueprint registrations (around line 50-60):
"""

# Import control routes
from .control_routes import control_bp

# Register control blueprint
app.register_blueprint(control_bp)

# Add route for control panel page
@app.route('/control')
@login_required
def control_panel():
    """Control panel page"""
    return render_template('control.html')
