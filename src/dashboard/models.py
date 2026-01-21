"""Database models for BotV2 Dashboard

Models:
- Portfolio: Current portfolio state
- Trade: Individual trade records
- Strategy: Strategy configurations
- StrategyPerformance: Performance metrics over time
- RiskMetrics: Risk calculations
- MarketData: OHLCV price data
- Annotation: User annotations on charts
- Alert: System alerts and notifications

Database: PostgreSQL (production) / SQLite (development)
ORM: SQLAlchemy
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Portfolio(Base):
    """Current portfolio state snapshot
    
    Stores the current state of the portfolio including total value,
    open positions, and daily changes.
    """
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Portfolio values
    total_value = Column(Float, nullable=False)
    cash_balance = Column(Float, default=0.0)
    margin_used = Column(Float, default=0.0)
    margin_available = Column(Float, default=0.0)
    
    # Daily changes
    daily_change = Column(Float, default=0.0)
    daily_change_pct = Column(Float, default=0.0)
    
    # Total P&L
    total_pnl = Column(Float, default=0.0)
    total_pnl_pct = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    
    # Positions (JSON array)
    positions = Column(JSON, default=[])
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, value={self.total_value}, pnl={self.total_pnl})>"
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'total_value': self.total_value,
            'cash_balance': self.cash_balance,
            'margin_used': self.margin_used,
            'margin_available': self.margin_available,
            'daily_change': self.daily_change,
            'daily_change_pct': self.daily_change_pct,
            'total_pnl': self.total_pnl,
            'total_pnl_pct': self.total_pnl_pct,
            'realized_pnl': self.realized_pnl,
            'unrealized_pnl': self.unrealized_pnl,
            'positions': self.positions
        }


class Trade(Base):
    """Individual trade record
    
    Complete history of all trades executed by the bot.
    """
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    
    # Trade identification
    trade_id = Column(String(50), unique=True, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    
    # Strategy
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='SET NULL'))
    strategy = relationship('Strategy', back_populates='trades')
    
    # Trade details
    direction = Column(String(10), nullable=False)  # 'long' or 'short'
    size = Column(Float, nullable=False)
    leverage = Column(Float, default=1.0)
    
    # Prices
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    
    # Timing
    entry_time = Column(DateTime, nullable=False, index=True)
    exit_time = Column(DateTime, index=True)
    duration_seconds = Column(Integer)
    
    # P&L
    pnl = Column(Float)
    pnl_pct = Column(Float)
    fees = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    net_pnl = Column(Float)  # pnl - fees - slippage
    
    # Status
    status = Column(String(20), default='open', index=True)  # 'open', 'closed', 'cancelled'
    exit_reason = Column(String(50))  # 'take_profit', 'stop_loss', 'manual', 'signal'
    
    # Metadata
    notes = Column(Text)
    tags = Column(JSON, default=[])
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_trades_symbol_entry_time', 'symbol', 'entry_time'),
        Index('ix_trades_strategy_status', 'strategy_id', 'status'),
    )
    
    def __repr__(self):
        return f"<Trade(id={self.trade_id}, symbol={self.symbol}, pnl={self.pnl})>"
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': self.id,
            'trade_id': self.trade_id,
            'symbol': self.symbol,
            'strategy': self.strategy.name if self.strategy else None,
            'direction': self.direction,
            'size': self.size,
            'leverage': self.leverage,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'entry_time': self.entry_time.isoformat() if self.entry_time else None,
            'exit_time': self.exit_time.isoformat() if self.exit_time else None,
            'duration_seconds': self.duration_seconds,
            'pnl': self.pnl,
            'pnl_pct': self.pnl_pct,
            'fees': self.fees,
            'slippage': self.slippage,
            'net_pnl': self.net_pnl,
            'status': self.status,
            'exit_reason': self.exit_reason,
            'notes': self.notes,
            'tags': self.tags
        }


class Strategy(Base):
    """Strategy configuration and metadata
    
    Defines trading strategies and their parameters.
    """
    __tablename__ = 'strategies'
    
    id = Column(Integer, primary_key=True)
    
    # Strategy identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Configuration
    parameters = Column(JSON, default={})  # Strategy-specific parameters
    enabled = Column(Boolean, default=True)
    
    # Risk management
    max_position_size = Column(Float)
    max_daily_loss = Column(Float)
    max_drawdown = Column(Float)
    
    # Relationships
    trades = relationship('Trade', back_populates='strategy', cascade='all, delete-orphan')
    performance = relationship('StrategyPerformance', back_populates='strategy', cascade='all, delete-orphan')
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Strategy(name={self.name}, enabled={self.enabled})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'parameters': self.parameters,
            'enabled': self.enabled,
            'max_position_size': self.max_position_size,
            'max_daily_loss': self.max_daily_loss,
            'max_drawdown': self.max_drawdown
        }


class StrategyPerformance(Base):
    """Strategy performance metrics over time
    
    Time-series data of strategy performance for chart generation.
    """
    __tablename__ = 'strategy_performance'
    
    id = Column(Integer, primary_key=True)
    
    # Strategy reference
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='CASCADE'), nullable=False)
    strategy = relationship('Strategy', back_populates='performance')
    
    # Time period
    timestamp = Column(DateTime, nullable=False, index=True)
    period = Column(String(20), default='daily')  # 'daily', 'weekly', 'monthly'
    
    # Performance metrics
    equity = Column(Float, nullable=False)
    return_pct = Column(Float)
    
    # Risk metrics
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    max_drawdown = Column(Float)
    volatility = Column(Float)
    
    # Trade statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)
    win_rate = Column(Float)
    
    # P&L
    gross_pnl = Column(Float, default=0.0)
    net_pnl = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_perf_strategy_timestamp', 'strategy_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<StrategyPerformance(strategy_id={self.strategy_id}, equity={self.equity})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'strategy_id': self.strategy_id,
            'timestamp': self.timestamp.isoformat(),
            'period': self.period,
            'equity': self.equity,
            'return_pct': self.return_pct,
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'max_drawdown': self.max_drawdown,
            'volatility': self.volatility,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': self.win_rate,
            'gross_pnl': self.gross_pnl,
            'net_pnl': self.net_pnl
        }


class RiskMetrics(Base):
    """Portfolio risk metrics
    
    Calculated risk metrics for the entire portfolio.
    """
    __tablename__ = 'risk_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Risk ratios
    sharpe_ratio = Column(Float)
    sortino_ratio = Column(Float)
    calmar_ratio = Column(Float)
    
    # Drawdown
    current_drawdown = Column(Float)
    max_drawdown = Column(Float)
    drawdown_duration_days = Column(Integer)
    
    # Value at Risk
    var_95 = Column(Float)  # 95% confidence
    var_99 = Column(Float)  # 99% confidence
    cvar_95 = Column(Float)  # Conditional VaR (Expected Shortfall)
    
    # Volatility
    volatility = Column(Float)
    downside_volatility = Column(Float)
    
    # Beta and Alpha (vs benchmark)
    beta = Column(Float)
    alpha = Column(Float)
    correlation = Column(Float)
    
    # Additional metrics
    profit_factor = Column(Float)
    recovery_factor = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<RiskMetrics(sharpe={self.sharpe_ratio}, drawdown={self.max_drawdown})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'sharpe_ratio': self.sharpe_ratio,
            'sortino_ratio': self.sortino_ratio,
            'calmar_ratio': self.calmar_ratio,
            'current_drawdown': self.current_drawdown,
            'max_drawdown': self.max_drawdown,
            'drawdown_duration_days': self.drawdown_duration_days,
            'var_95': self.var_95,
            'var_99': self.var_99,
            'cvar_95': self.cvar_95,
            'volatility': self.volatility,
            'downside_volatility': self.downside_volatility,
            'beta': self.beta,
            'alpha': self.alpha,
            'correlation': self.correlation,
            'profit_factor': self.profit_factor,
            'recovery_factor': self.recovery_factor
        }


class MarketData(Base):
    """OHLCV market data
    
    Historical price data for candlestick charts.
    """
    __tablename__ = 'market_data'
    
    id = Column(Integer, primary_key=True)
    
    # Symbol and timeframe
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)  # '1m', '5m', '1h', '1d'
    timestamp = Column(DateTime, nullable=False, index=True)
    
    # OHLCV
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    
    # Additional data
    trades_count = Column(Integer)
    vwap = Column(Float)  # Volume-Weighted Average Price
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('ix_market_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<MarketData(symbol={self.symbol}, timestamp={self.timestamp}, close={self.close})>"
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'timestamp': self.timestamp.isoformat(),
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'trades_count': self.trades_count,
            'vwap': self.vwap
        }


class Annotation(Base):
    """User annotations on charts
    
    Stores user-created annotations for historical events.
    """
    __tablename__ = 'annotations'
    
    id = Column(Integer, primary_key=True)
    
    # Annotation details
    chart_id = Column(String(50), nullable=False, index=True)
    date = Column(DateTime, nullable=False)
    text = Column(Text, nullable=False)
    type = Column(String(20), default='custom')  # 'trade', 'signal', 'news', 'custom'
    
    # Visual properties
    color = Column(String(20))
    icon = Column(String(20))
    
    # Metadata
    user_id = Column(String(50))  # For multi-user support
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Annotation(chart={self.chart_id}, type={self.type}, text={self.text[:30]})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'chart_id': self.chart_id,
            'date': self.date.isoformat(),
            'text': self.text,
            'type': self.type,
            'color': self.color,
            'icon': self.icon,
            'created_at': self.created_at.isoformat()
        }


class Alert(Base):
    """System alerts and notifications
    
    Tracks important events and alerts generated by the system.
    """
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    
    # Alert details
    type = Column(String(50), nullable=False, index=True)  # 'risk', 'trade', 'system', 'performance'
    severity = Column(String(20), default='info')  # 'info', 'warning', 'error', 'critical'
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Related entities
    strategy_id = Column(Integer, ForeignKey('strategies.id', ondelete='CASCADE'))
    trade_id = Column(Integer, ForeignKey('trades.id', ondelete='CASCADE'))
    
    # Status
    status = Column(String(20), default='active')  # 'active', 'acknowledged', 'resolved'
    acknowledged_at = Column(DateTime)
    resolved_at = Column(DateTime)
    
    # Metadata
    data = Column(JSON)  # Additional context data
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<Alert(type={self.type}, severity={self.severity}, title={self.title})>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'severity': self.severity,
            'title': self.title,
            'message': self.message,
            'strategy_id': self.strategy_id,
            'trade_id': self.trade_id,
            'status': self.status,
            'acknowledged_at': self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'data': self.data,
            'created_at': self.created_at.isoformat()
        }


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_db(engine):
    """Initialize database tables
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully")


def drop_all(engine):
    """Drop all tables (use with caution!)
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(engine)
    print("⚠️  All database tables dropped")