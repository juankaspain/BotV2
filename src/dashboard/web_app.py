"""
Web Dashboard
Real-time monitoring dashboard using Flask/Dash
"""

import logging
from flask import Flask
import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
from datetime import datetime
import pandas as pd
import numpy as np
from typing import Dict, List

logger = logging.getLogger(__name__)


class TradingDashboard:
    """
    Real-time trading dashboard
    
    Features:
    - Equity curve
    - Live P&L
    - Strategy performance
    - Risk metrics
    - Trade history
    """
    
    def __init__(self, config):
        """Initialize dashboard"""
        
        self.config = config
        
        # Dashboard config
        dash_config = config.get('dashboard', {})
        self.host = dash_config.get('host', '0.0.0.0')
        self.port = dash_config.get('port', 8050)
        self.debug = dash_config.get('debug', False)
        self.refresh_rate = dash_config.get('refresh_rate', 5) * 1000  # Convert to ms
        
        # Flask/Dash app
        self.server = Flask(__name__)
        self.app = dash.Dash(__name__, server=self.server)
        
        # Data (shared with main system)
        self.portfolio_data = []
        self.trades_data = []
        self.strategy_data = {}
        self.risk_metrics = {}
        
        # Build layout
        self._build_layout()
        self._setup_callbacks()
        
        logger.info(f"✓ Dashboard initialized on {self.host}:{self.port}")
    
    def _build_layout(self):
        """Build dashboard layout"""
        
        self.app.layout = html.Div([
            html.H1("BotV2 Trading Dashboard", style={'textAlign': 'center'}),
            
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
                ], className='summary-box'),
                
                html.Div([
                    html.H3("Total P&L"),
                    html.Div(id='total-pnl', style={'fontSize': 32, 'fontWeight': 'bold'})
                ], className='summary-box'),
                
                html.Div([
                    html.H3("Win Rate"),
                    html.Div(id='win-rate', style={'fontSize': 32, 'fontWeight': 'bold'})
                ], className='summary-box'),
                
                html.Div([
                    html.H3("Sharpe Ratio"),
                    html.Div(id='sharpe-ratio', style={'fontSize': 32, 'fontWeight': 'bold'})
                ], className='summary-box'),
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
            return html.Div("No risk metrics availab
