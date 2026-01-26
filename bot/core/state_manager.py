"""
State Manager - Persistent State with Crash Recovery
PostgreSQL-based state persistence with automatic checkpointing
"""

import logging
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
import asyncio

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manages persistent state with crash recovery
    - Saves trades to database
    - Checkpoints portfolio state every 5 minutes
    - Recovers from crashes
    - Backs up to disk periodically
    """
    
    def __init__(self, config):
        """Initialize state manager"""
        
        self.config = config
        self.enabled = config.get('state_persistence.enabled', True)
        
        if not self.enabled:
            logger.warning("State persistence disabled")
            return
        
        # Storage configuration
        storage_config = config.get('state_persistence.storage', {})
        self.storage_type = storage_config.get('type', 'postgresql')
        
        # Checkpoint configuration
        self.checkpoint_frequency = config.get('state_persistence.checkpoint_frequency', 300)
        self.backup_frequency = config.get('state_persistence.backup_frequency', 3600)
        
        # Backup path
        backup_config = config.get('state_persistence.backup', {})
        self.backup_path = Path(backup_config.get('path', './backups'))
        self.backup_path.mkdir(parents=True, exist_ok=True)
        
        # State tracking
        self.last_checkpoint: Optional[datetime] = None
        self.last_backup: Optional[datetime] = None
        
        # Initialize storage
        self.db = None
        if self.storage_type == 'postgresql':
            self._init_postgresql()
        elif self.storage_type == 'sqlite':
            self._init_sqlite()
        
        logger.info(f"✓ State Manager initialized ({self.storage_type})")
    
    def _init_postgresql(self):
        """Initialize PostgreSQL connection"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            storage_config = self.config.get('state_persistence.storage', {})
            
            self.db = psycopg2.connect(
                host=storage_config.get('host', 'localhost'),
                port=storage_config.get('port', 5432),
                database=storage_config.get('database', 'botv2'),
                user=storage_config.get('user', 'botv2_user'),
                password=storage_config.get('password', ''),
                cursor_factory=RealDictCursor
            )
            
            # Create tables
            self._create_tables()
            
            logger.info("✓ PostgreSQL connection established")
            
        except ImportError:
            logger.error("psycopg2 not installed. Install: pip install psycopg2-binary")
            self.db = None
        except Exception as e:
            logger.error(f"PostgreSQL connection failed: {e}")
            self.db = None
    
    def _init_sqlite(self):
        """Initialize SQLite connection"""
        try:
            import sqlite3
            
            db_path = self.backup_path / 'botv2_state.db'
            self.db = sqlite3.connect(str(db_path))
            self.db.row_factory = sqlite3.Row
            
            # Create tables
            self._create_tables()
            
            logger.info(f"✓ SQLite connection established: {db_path}")
            
        except Exception as e:
            logger.error(f"SQLite connection failed: {e}")
            self.db = None
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        
        # Trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                symbol VARCHAR(50) NOT NULL,
                action VARCHAR(10) NOT NULL,
                strategy VARCHAR(50) NOT NULL,
                entry_price DECIMAL(18, 8),
                exit_price DECIMAL(18, 8),
                position_size DECIMAL(18, 8),
                pnl DECIMAL(18, 8),
                pnl_pct DECIMAL(10, 4),
                slippage DECIMAL(10, 6),
                commission DECIMAL(18, 8),
                metadata JSONB
            )
        """)
        
        # Portfolio checkpoints table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolio_checkpoints (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                cash DECIMAL(18, 8),
                equity DECIMAL(18, 8),
                positions JSONB,
                metadata JSONB
            )
        """)
        
        # Metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                total_return DECIMAL(10, 4),
                sharpe_ratio DECIMAL(10, 4),
                max_drawdown DECIMAL(10, 4),
                win_rate DECIMAL(10, 4),
                total_trades INTEGER,
                metadata JSONB
            )
        """)
        
        self.db.commit()
        logger.info("✓ Database tables created/verified")
    
    async def save_trade(self, trade: Dict):
        """
        Save trade to database
        
        Args:
            trade: Trade execution result dict
        """
        
        if not self.enabled or self.db is None:
            return
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                INSERT INTO trades (
                    timestamp, symbol, action, strategy,
                    entry_price, exit_price, position_size,
                    pnl, pnl_pct, slippage, commission, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                trade.get('symbol'),
                trade.get('action'),
                trade.get('strategy'),
                trade.get('entry_price'),
                trade.get('exit_price'),
                trade.get('position_size'),
                trade.get('pnl'),
                trade.get('pnl_pct'),
                trade.get('slippage'),
                trade.get('commission'),
                json.dumps(trade.get('metadata', {}))
            ))
            
            self.db.commit()
            logger.debug(f"✓ Trade saved: {trade.get('symbol')} {trade.get('action')}")
            
        except Exception as e:
            logger.error(f"Failed to save trade: {e}")
            self.db.rollback()
    
    async def save_portfolio(self, portfolio: Dict):
        """
        Save portfolio checkpoint
        
        Args:
            portfolio: Current portfolio state
        """
        
        if not self.enabled or self.db is None:
            return
        
        # Check if checkpoint needed
        now = datetime.now()
        if self.last_checkpoint is not None:
            elapsed = (now - self.last_checkpoint).total_seconds()
            if elapsed < self.checkpoint_frequency:
                return
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                INSERT INTO portfolio_checkpoints (
                    timestamp, cash, equity, positions, metadata
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                now,
                portfolio.get('cash', 0),
                portfolio.get('equity', 0),
                json.dumps(portfolio.get('positions', {})),
                json.dumps({})
            ))
            
            self.db.commit()
            self.last_checkpoint = now
            
            logger.debug(f"✓ Portfolio checkpoint saved: €{portfolio.get('equity', 0):.2f}")
            
        except Exception as e:
            logger.error(f"Failed to save portfolio: {e}")
            self.db.rollback()
        
        # Also save disk backup periodically
        await self._save_disk_backup(portfolio)
    
    async def save_metrics(self, metrics: Dict):
        """
        Save performance metrics
        
        Args:
            metrics: Performance metrics dict
        """
        
        if not self.enabled or self.db is None:
            return
        
        try:
            cursor = self.db.cursor()
            
            cursor.execute("""
                INSERT INTO performance_metrics (
                    timestamp, total_return, sharpe_ratio, max_drawdown,
                    win_rate, total_trades, metadata
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                metrics.get('total_return'),
                metrics.get('sharpe'),
                metrics.get('max_drawdown'),
                metrics.get('win_rate'),
                metrics.get('total_trades'),
                json.dumps(metrics)
            ))
            
            self.db.commit()
            logger.debug("✓ Metrics saved")
            
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
            self.db.rollback()
    
    async def recover(self) -> Optional[Dict]:
        """
        Recover state from latest checkpoint
        
        Returns:
            Dict with recovered portfolio state, or None if failed
        """
        
        if not self.enabled or self.db is None:
            logger.warning("Cannot recover: state persistence disabled or no DB")
            return None
        
        try:
            cursor = self.db.cursor()
            
            # Get latest checkpoint
            cursor.execute("""
                SELECT * FROM portfolio_checkpoints
                ORDER BY timestamp DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            
            if row is None:
                logger.warning("No checkpoint found")
                return None
            
            # Reconstruct portfolio
            portfolio = {
                'cash': float(row['cash']),
                'equity': float(row['equity']),
                'positions': json.loads(row['positions'])
            }
            
            logger.info(
                f"✓ State recovered from checkpoint "
                f"({row['timestamp']}, €{portfolio['equity']:.2f})"
            )
            
            return {'portfolio': portfolio}
            
        except Exception as e:
            logger.error(f"State recovery failed: {e}")
            return None
    
    async def _save_disk_backup(self, portfolio: Dict):
        """Save backup to disk"""
        
        now = datetime.now()
        
        # Check if backup needed
        if self.last_backup is not None:
            elapsed = (now - self.last_backup).total_seconds()
            if elapsed < self.backup_frequency:
                return
        
        try:
            backup_file = self.backup_path / f"portfolio_{now.strftime('%Y%m%d_%H%M%S')}.pkl"
            
            with open(backup_file, 'wb') as f:
                pickle.dump(portfolio, f)
            
            self.last_backup = now
            logger.debug(f"✓ Disk backup saved: {backup_file}")
            
            # Clean old backups
            self._cleanup_old_backups()
            
        except Exception as e:
            logger.error(f"Disk backup failed: {e}")
    
    def _cleanup_old_backups(self):
        """Remove old backup files"""
        
        retention_days = self.config.get('state_persistence.backup.retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for backup_file in self.backup_path.glob('portfolio_*.pkl'):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()
                logger.debug(f"Removed old backup: {backup_file}")
