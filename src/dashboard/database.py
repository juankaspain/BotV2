"""Database Layer for BotV2 Dashboard
Provides DB-backed data access with session management and query helpers.
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from sqlalchemy import (
    create_engine,
    and_,
    or_,
    desc,
    func,
    cast,
    String
)
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Centralized database management with connection pooling and session handling."""
    
    def __init__(self, database_url: str = 'sqlite:///data/dashboard.db'):
        """Initialize database manager.
        
        Args:
            database_url: SQLAlchemy database URL
        """
        self.database_url = database_url
        self.engine = None
        self.SessionFactory = None
        self.session_pool = None
        self._initialized = False
        
    def initialize(self) -> bool:
        """Initialize database connection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from pathlib import Path
            # Create data directory for SQLite
            if self.database_url.startswith('sqlite:'):
                db_path = self.database_url.replace('sqlite:///', '')
                Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Create engine with connection pooling
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,  # Validate connections
                pool_size=10,         # Connection pool size
                max_overflow=20      # Max overflow connections
            )
            
            # Create session factory
            self.SessionFactory = sessionmaker(bind=self.engine)
            self.session_pool = scoped_session(self.SessionFactory)
            
            # Create tables
            try:
                from .models import Base
                Base.metadata.create_all(self.engine)
                logger.info(f"\u2705 Database initialized: {self.database_url}")
            except ImportError:
                logger.warning("\u26a0\ufe0f Models not available, skipping table creation")
            
            self._initialized = True
            return True
            
        except Exception as e:
            logger.error(f"\u274c Database initialization failed: {e}")
            self._initialized = False
            return False
    
    @contextmanager
    def get_session(self) -> Session:
        """Get a database session context manager.
        
        Yields:
            Session: SQLAlchemy session
            
        Example:
            with db.get_session() as session:
                result = session.query(Trade).all()
        """
        session = self.session_pool()
        try:
            yield session
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def close(self):
        """Close all database connections."""
        if self.session_pool:
            self.session_pool.remove()
        if self.engine:
            self.engine.dispose()
        self._initialized = False


class PortfolioDAO:
    """Data Access Object for Portfolio queries."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_current(self) -> Dict[str, Any]:
        """Get current portfolio state."""
        try:
            with self.db.get_session() as session:
                from .models import Portfolio
                portfolio = session.query(Portfolio).order_by(desc(Portfolio.created_at)).first()
                if portfolio:
                    return {
                        'total_value': float(portfolio.total_value),
                        'cash': float(portfolio.cash),
                        'invested': float(portfolio.invested),
                        'created_at': portfolio.created_at.isoformat()
                    }
                return {'total_value': 0, 'cash': 0, 'invested': 0}
        except Exception as e:
            logger.error(f"Error fetching portfolio: {e}")
            return {'total_value': 0, 'cash': 0, 'invested': 0}
    
    def get_history(self, days: int = 30) -> List[Dict]:
        """Get portfolio history for the last N days."""
        try:
            with self.db.get_session() as session:
                from .models import Portfolio
                start_date = datetime.now() - timedelta(days=days)
                history = session.query(Portfolio).filter(
                    Portfolio.created_at >= start_date
                ).order_by(Portfolio.created_at).all()
                
                return [{
                    'date': p.created_at.isoformat(),
                    'total_value': float(p.total_value),
                    'cash': float(p.cash)
                } for p in history]
        except Exception as e:
            logger.error(f"Error fetching portfolio history: {e}")
            return []


class TradeDAO:
    """Data Access Object for Trade queries."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_trades(
        self,
        symbol: Optional[str] = None,
        strategy: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """Get trades with optional filters."""
        try:
            with self.db.get_session() as session:
                from .models import Trade
                query = session.query(Trade)
                
                if symbol:
                    query = query.filter(Trade.symbol == symbol)
                if strategy:
                    query = query.filter(Trade.strategy == strategy)
                if status:
                    query = query.filter(Trade.status == status)
                
                trades = query.order_by(desc(Trade.entry_time)).limit(limit).offset(offset).all()
                
                return [{
                    'id': t.id,
                    'symbol': t.symbol,
                    'strategy': t.strategy,
                    'entry_price': float(t.entry_price),
                    'exit_price': float(t.exit_price) if t.exit_price else None,
                    'pnl': float(t.pnl) if t.pnl else None,
                    'status': t.status,
                    'entry_time': t.entry_time.isoformat(),
                    'exit_time': t.exit_time.isoformat() if t.exit_time else None
                } for t in trades]
        except Exception as e:
            logger.error(f"Error fetching trades: {e}")
            return []
    
    def get_recent(self, hours: int = 24) -> List[Dict]:
        """Get trades from the last N hours."""
        try:
            with self.db.get_session() as session:
                from .models import Trade
                start_time = datetime.now() - timedelta(hours=hours)
                trades = session.query(Trade).filter(
                    Trade.entry_time >= start_time
                ).order_by(desc(Trade.entry_time)).all()
                
                return [{
                    'id': t.id,
                    'symbol': t.symbol,
                    'pnl': float(t.pnl) if t.pnl else 0
                } for t in trades]
        except Exception as e:
            logger.error(f"Error fetching recent trades: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get trade statistics."""
        try:
            with self.db.get_session() as session:
                from .models import Trade
                closed_trades = session.query(Trade).filter(
                    Trade.status == 'closed'
                ).all()
                
                if not closed_trades:
                    return {'total': 0, 'winners': 0, 'losers': 0}
                
                winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
                losing_trades = [t for t in closed_trades if t.pnl and t.pnl <= 0]
                
                total_profit = sum(t.pnl for t in closed_trades if t.pnl)
                
                return {
                    'total': len(closed_trades),
                    'winners': len(winning_trades),
                    'losers': len(losing_trades),
                    'win_rate': len(winning_trades) / len(closed_trades) if closed_trades else 0,
                    'total_profit': float(total_profit),
                    'avg_profit': float(total_profit / len(closed_trades)) if closed_trades else 0
                }
        except Exception as e:
            logger.error(f"Error fetching trade stats: {e}")
            return {}


class StrategyDAO:
    """Data Access Object for Strategy queries."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_all(self) -> List[Dict]:
        """Get all strategies."""
        try:
            with self.db.get_session() as session:
                from .models import Strategy
                strategies = session.query(Strategy).all()
                
                return [{
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'active': s.active,
                    'created_at': s.created_at.isoformat()
                } for s in strategies]
        except Exception as e:
            logger.error(f"Error fetching strategies: {e}")
            return []
    
    def get_performance(self, strategy_id: int) -> List[Dict]:
        """Get performance history for strategy."""
        try:
            with self.db.get_session() as session:
                from .models import StrategyPerformance
                perf = session.query(StrategyPerformance).filter(
                    StrategyPerformance.strategy_id == strategy_id
                ).order_by(StrategyPerformance.date).all()
                
                return [{
                    'date': p.date.isoformat(),
                    'return': float(p.return_pct),
                    'sharpe': float(p.sharpe_ratio) if p.sharpe_ratio else None
                } for p in perf]
        except Exception as e:
            logger.error(f"Error fetching strategy performance: {e}")
            return []


class RiskDAO:
    """Data Access Object for Risk queries."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics."""
        try:
            with self.db.get_session() as session:
                from .models import RiskMetrics
                metrics = session.query(RiskMetrics).order_by(
                    desc(RiskMetrics.created_at)
                ).first()
                
                if metrics:
                    return {
                        'var_95': float(metrics.var_95),
                        'max_drawdown': float(metrics.max_drawdown),
                        'sharpe_ratio': float(metrics.sharpe_ratio),
                        'created_at': metrics.created_at.isoformat()
                    }
                return {'var_95': 0, 'max_drawdown': 0, 'sharpe_ratio': 0}
        except Exception as e:
            logger.error(f"Error fetching risk metrics: {e}")
            return {}


# Global database instance
_db_manager = None

def init_database(database_url: str = 'sqlite:///data/dashboard.db') -> DatabaseManager:
    """Initialize global database manager."""
    global _db_manager
    _db_manager = DatabaseManager(database_url)
    _db_manager.initialize()
    return _db_manager

def get_database() -> Optional[DatabaseManager]:
    """Get global database manager."""
    return _db_manager
