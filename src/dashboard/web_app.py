"""
Web Dashboard
Real-time monitoring dashboard using Flask/Dash
SECURITY: HTTP Basic Authentication implemented
"""

import logging
import os
from flask import Flask, request, Response
from functools import wraps
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List
import hashlib
import secrets

logger = logging.getLogger(__name__)


class DashboardAuth:
    """
    HTTP Basic Authentication for Dashboard
    
    Uses environment variables for credentials:
    - DASHBOARD_USERNAME (default: admin)
    - DASHBOARD_PASSWORD (required, no default for security)
    """
    
    def __init__(self):
        """Initialize authentication"""
        
        self.username = os.getenv('DASHBOARD_USERNAME', 'admin')
        self.password_hash = self._get_password_hash()
        
        if not self.password_hash:
            logger.critical(
                "⚠️ DASHBOARD_PASSWORD not set! Dashboard will be INSECURE. "
                "Set environment variable before starting."
            )
            # Generate temporary password for first run
            temp_password = secrets.token_urlsafe(16)
            logger.warning(f"🔑 Temporary password generated: {temp_password}")
            logger.warning("IMPORTANT: Set DASHBOARD_PASSWORD env var for production!")
            self.password_hash = self._hash_password(temp_password)
    
    def _get_password_hash(self) -> str:
        """Get password hash from environment"""
        password = os.getenv('DASHBOARD_PASSWORD')
        if password:
            return self._hash_password(password)
        return None
    
    def _hash_password(self, password: str) -> str:
        """Hash password with SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def check_credentials(self, username: str, password: str) -> bool:
        """
        Verify username and password
        
        Args:
            username: Provided username
            password: Provided password
            
        Returns:
            True if credentials valid, False otherwise
        """
        if not self.password_hash:
            # If no password set, allow access (dev mode)
            logger.warning("⚠️ No password configured, allowing access (DEV MODE)")
            return True
        
        username_match = secrets.compare_digest(username, self.username)
        password_match = secrets.compare_digest(
            self._hash_password(password),
            self.password_hash
        )
        
        return username_match and password_match
    
    def authenticate_decorator(self, f):
        """
        Decorator for Flask routes requiring authentication
        
        Usage:
            @auth.authenticate_decorator
            def my_route():
                return "Protected content"
        """
        @wraps(f)
        def decorated(*args, **kwargs):
            auth = request.authorization
            
            if not auth or not self.check_credentials(auth.username, auth.password):
                logger.warning(
                    f"Failed login attempt from {request.remote_addr} "
                    f"(username: {auth.username if auth else 'none'})"
                )
                return Response(
                    'Authentication required.\n'
                    'Please login with valid credentials.',
                    401,
                    {'WWW-Authenticate': 'Basic realm="BotV2 Dashboard"'}
                )
            
            logger.debug(f"Authenticated user: {auth.username} from {request.remote_addr}")
            return f(*args, **kwargs)
        
        return decorated


class TradingDashboard:
    """
    Real-time trading dashboard with authentication
    
    Features:
    - 🔒 HTTP Basic Authentication
    - Equity curve
    - Live P&L
    - Strategy performance
    - Risk metrics
    - Trade history
    
    Security:
    - Credentials from environment variables
    - Password hashing (SHA-256)
    - Constant-time comparison to prevent timing attacks
    - Login attempt logging
    - Auto-generated temporary password if not configured
    """
    
    def __init__(self, config):
        """Initialize dashboard with authentication"""
        
        self.config = config
        
        # Dashboard config
        dash_config = config.get('dashboard', {})
        self.host = dash_config.get('host', '0.0.0.0')
        self.port = dash_config.get('port', 8050)
        self.debug = dash_config.get('debug', False)
        self.refresh_rate = dash_config.get('refresh_rate', 5) * 1000  # Convert to ms
        
        # Initialize authentication
        self.auth = DashboardAuth()
        
        # Flask/Dash app
        self.server = Flask(__name__)
        self.app = dash.Dash(__name__, server=self.server)
        
        # Apply authentication to all routes
        self._setup_authentication()
        
        # Data (shared with main system)
        self.portfolio_data = []
        self.trades_data = []
        self.strategy_data = {}
        self.risk_metrics = {}
        
        # Build layout
        self._build_layout()
        self._setup_callbacks()
        
        logger.info(f"✅ Dashboard initialized on {self.host}:{self.port}")
        logger.info(f"🔒 Authentication: ENABLED (user: {self.auth.username})")
    
    def _setup_authentication(self):
        """Setup authentication for all Flask routes"""
        
        @self.server.before_request
        @self.auth.authenticate_decorator
        def require_auth():
            """Require authentication for all requests"""
            pass
        
        logger.info("✅ Authentication middleware installed")
    
    def _build_layout(self):
        """Build dashboard layout"""
        
        self.app.layout = html.Div([
            # Header with security badge
            html.Div([
                html.H1("BotV2 Trading Dashboard", style={'display': 'inline-block', 'marginRight': 20}),
                html.Span("🔒 Secured", style={
                    'backgroundColor': '#28a745',
                    'color': 'white',
                    'padding': '5px 15px',
                    'borderRadius': '5px',
                    'fontSize': '14px',
                    'fontWeight': 'bold'
                })
            ], style={'textAlign': 'center', 'marginBottom': 20}),
            
            # Auto-refresh interval
            dcc.Interval(
                id='interval-component',
                interval=self.refresh_rate,
                n_intervals=0
            ),
            
            # Portfolio Summary Row
            html.Div([
                html.Div([
                    html.H3("Portfolio Value"),
                    html.Div(id='portfolio-value', style={'fontSize': 32, 'fontWeight': 'bold'})
                ], className='summary-box', style={'flex': 1, 'textAlign': 'center', 'padding': 20, 'border': '1px solid #ddd', 'margin': 10}),
                
                html.Div([
                    html.H3("Total P&L"),
                    html.Div(id='total-pnl', style={'fontSize': 32, 'fontWeight': 'bold'})
                ], className='summary-box', style={'flex': 1, 'textAlign': 'center', 'padding': 20, 'border': '1px solid #ddd', 'margin': 10}),
                
                html.Div([
                    html.H3("Win Rate"),
                    html.Div(id='win-rate', style={'fontSize': 32, 'fontWeight': 'bold'})
                ], className='summary-box', style={'flex': 1, 'textAlign': 'center', 'padding': 20, 'border': '1px solid #ddd', 'margin': 10}),
                
                html.Div([
                    html.H3("Sharpe Ratio"),
                    html.Div(id='sharpe-ratio', style={'fontSize': 32, 'fontWeight': 'bold'})
                ], className='summary-box', style={'flex': 1, 'textAlign': 'center', 'padding': 20, 'border': '1px solid #ddd', 'margin': 10}),
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'marginBottom': 20}),
            
            # Equity Curve
            html.Div([
                html.H2("Equity Curve"),
                dcc.Graph(id='equity-curve')
            ]),
            
            # Daily Returns
            html.Div([
                html.H2("Daily Returns"),
                dcc.Graph(id='daily-returns')
            ]),
            
            # Strategy Performance
            html.Div([
                html.H2("Strategy Performance"),
                dcc.Graph(id='strategy-performance')
            ]),
            
            # Risk Metrics
            html.Div([
                html.H2("Risk Metrics"),
                html.Div(id='risk-metrics')
            ]),
            
            # Recent Trades
            html.Div([
                html.H2("Recent Trades"),
                html.Div(id='recent-trades')
            ])
            
        ], style={'padding': 20})
    
    def _setup_callbacks(self):
        """Setup Dash callbacks for interactivity"""
        
        @self.app.callback(
            [
                Output('portfolio-value', 'children'),
                Output('total-pnl', 'children'),
                Output('win-rate', 'children'),
                Output('sharpe-ratio', 'children'),
                Output('equity-curve', 'figure'),
                Output('daily-returns', 'figure'),
                Output('strategy-performance', 'figure'),
                Output('risk-metrics', 'children'),
                Output('recent-trades', 'children')
            ],
            Input('interval-component', 'n_intervals')
        )
        def update_dashboard(n):
            """Update all dashboard components"""
            
            # Portfolio value
            portfolio_value = self._get_portfolio_value()
            
            # Total P&L
            total_pnl = self._get_total_pnl()
            
            # Win rate
            win_rate = self._get_win_rate()
            
            # Sharpe ratio
            sharpe = self._get_sharpe_ratio()
            
            # Equity curve chart
            equity_fig = self._create_equity_curve()
            
            # Daily returns chart
            returns_fig = self._create_returns_chart()
            
            # Strategy performance chart
            strategy_fig = self._create_strategy_chart()
            
            # Risk metrics table
            risk_table = self._create_risk_table()
            
            # Recent trades table
            trades_table = self._create_trades_table()
            
            return (
                portfolio_value,
                total_pnl,
                win_rate,
                sharpe,
                equity_fig,
                returns_fig,
                strategy_fig,
                risk_table,
                trades_table
            )
    
    def _get_portfolio_value(self) -> str:
        """Get current portfolio value"""
        if self.portfolio_data:
            value = self.portfolio_data[-1].get('equity', 0)
            return f"€{value:,.2f}"
        return "€0.00"
    
    def _get_total_pnl(self) -> str:
        """Get total P&L"""
        if len(self.portfolio_data) > 1:
            initial = self.portfolio_data[0].get('equity', 0)
            current = self.portfolio_data[-1].get('equity', 0)
            pnl = current - initial
            pnl_pct = (pnl / initial) * 100 if initial > 0 else 0
            
            color = 'green' if pnl >= 0 else 'red'
            return html.Span(
                f"€{pnl:,.2f} ({pnl_pct:+.2f}%)",
                style={'color': color}
            )
        return "€0.00 (0.00%)"
    
    def _get_win_rate(self) -> str:
        """Get win rate"""
        if self.trades_data:
            winning = sum(1 for t in self.trades_data if t.get('pnl', 0) > 0)
            win_rate = (winning / len(self.trades_data)) * 100
            return f"{win_rate:.1f}%"
        return "0.0%"
    
    def _get_sharpe_ratio(self) -> str:
        """Get Sharpe ratio"""
        if 'sharpe' in self.risk_metrics:
            sharpe = self.risk_metrics['sharpe']
            return f"{sharpe:.2f}"
        return "0.00"
    
    def _create_equity_curve(self) -> go.Figure:
        """Create equity curve chart"""
        
        if not self.portfolio_data:
            return go.Figure()
        
        df = pd.DataFrame(self.portfolio_data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['equity'],
            mode='lines',
            name='Equity',
            line=dict(color='#00CC96', width=2)
        ))
        
        fig.update_layout(
            title='Portfolio Equity Curve',
            xaxis_title='Time',
            yaxis_title='Equity (EUR)',
            hovermode='x unified',
            template='plotly_dark'
        )
        
        return fig
    
    def _create_returns_chart(self) -> go.Figure:
        """Create daily returns chart"""
        
        if not self.portfolio_data or len(self.portfolio_data) < 2:
            return go.Figure()
        
        df = pd.DataFrame(self.portfolio_data)
        df['returns'] = df['equity'].pct_change()
        
        colors = ['green' if x >= 0 else 'red' for x in df['returns']]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df.index,
            y=df['returns'] * 100,
            marker_color=colors,
            name='Daily Return %'
        ))
        
        fig.update_layout(
            title='Daily Returns',
            xaxis_title='Time',
            yaxis_title='Return (%)',
            template='plotly_dark'
        )
        
        return fig
    
    def _create_strategy_chart(self) -> go.Figure:
        """Create strategy performance chart"""
        
        if not self.strategy_data:
            return go.Figure()
        
        strategies = list(self.strategy_data.keys())
        returns = [self.strategy_data[s].get('total_return', 0) * 100 for s in strategies]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=strategies,
            y=returns,
            marker_color='#636EFA',
            name='Total Return %'
        ))
        
        fig.update_layout(
            title='Strategy Performance',
            xaxis_title='Strategy',
            yaxis_title='Return (%)',
            template='plotly_dark'
        )
        
        return fig
    
    def _create_risk_table(self) -> html.Table:
        """Create risk metrics table"""
        
        if not self.risk_metrics:
            return html.Div("No risk metrics available", style={'padding': 20})
        
        rows = []
        for metric, value in self.risk_metrics.items():
            rows.append(html.Tr([
                html.Td(metric.replace('_', ' ').title(), style={'padding': 10, 'fontWeight': 'bold'}),
                html.Td(f"{value:.2f}", style={'padding': 10})
            ]))
        
        return html.Table(
            [html.Tbody(rows)],
            style={'width': '100%', 'border': '1px solid #ddd'}
        )
    
    def _create_trades_table(self) -> html.Table:
        """Create recent trades table"""
        
        if not self.trades_data:
            return html.Div("No trades yet", style={'padding': 20})
        
        # Show last 10 trades
        recent = self.trades_data[-10:]
        
        header = html.Tr([
            html.Th('Time', style={'padding': 10, 'backgroundColor': '#f0f0f0'}),
            html.Th('Strategy', style={'padding': 10, 'backgroundColor': '#f0f0f0'}),
            html.Th('Action', style={'padding': 10, 'backgroundColor': '#f0f0f0'}),
            html.Th('Size', style={'padding': 10, 'backgroundColor': '#f0f0f0'}),
            html.Th('P&L', style={'padding': 10, 'backgroundColor': '#f0f0f0'})
        ])
        
        rows = []
        for trade in reversed(recent):
            pnl = trade.get('pnl', 0)
            pnl_color = 'green' if pnl >= 0 else 'red'
            
            rows.append(html.Tr([
                html.Td(trade.get('timestamp', 'N/A'), style={'padding': 10}),
                html.Td(trade.get('strategy', 'N/A'), style={'padding': 10}),
                html.Td(trade.get('action', 'N/A'), style={'padding': 10}),
                html.Td(f"{trade.get('size', 0):.4f}", style={'padding': 10}),
                html.Td(f"€{pnl:,.2f}", style={'padding': 10, 'color': pnl_color})
            ]))
        
        return html.Table(
            [html.Thead(header), html.Tbody(rows)],
            style={'width': '100%', 'border': '1px solid #ddd', 'borderCollapse': 'collapse'}
        )
    
    def update_data(self, portfolio: Dict, trades: List, strategies: Dict, risk: Dict):
        """
        Update dashboard data from main trading system
        
        Args:
            portfolio: Current portfolio state
            trades: Recent trades list
            strategies: Strategy performance dict
            risk: Risk metrics dict
        """
        self.portfolio_data.append({
            'timestamp': datetime.now(),
            'equity': portfolio.get('equity', 0),
            'cash': portfolio.get('cash', 0),
            'positions': len(portfolio.get('positions', {}))
        })
        
        self.trades_data = trades
        self.strategy_data = strategies
        self.risk_metrics = risk
    
    def run(self):
        """Start dashboard server"""
        
        logger.info("="*70)
        logger.info("🚀 Starting BotV2 Dashboard...")
        logger.info(f"🌐 URL: http://{self.host}:{self.port}")
        logger.info(f"🔒 Authentication: REQUIRED")
        logger.info(f"👤 Username: {self.auth.username}")
        logger.info("🔑 Password: Set via DASHBOARD_PASSWORD env var")
        logger.info("="*70)
        
        self.app.run_server(
            host=self.host,
            port=self.port,
            debug=self.debug
        )


if __name__ == "__main__":
    # Test dashboard standalone
    from src.config.config_manager import ConfigManager
    
    config = ConfigManager()
    dashboard = TradingDashboard(config)
    dashboard.run()
