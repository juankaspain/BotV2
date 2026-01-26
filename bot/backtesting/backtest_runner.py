"""
Backtest Runner
Orchestrates backtesting with realistic simulation
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio

from .realistic_simulator import RealisticSimulator
from .market_microstructure import MarketMicrostructure

logger = logging.getLogger(__name__)


class BacktestRunner:
    """
    Runs backtests with realistic market simulation
    
    Features:
    - Historical data replay
    - Realistic execution simulation
    - Performance analytics
    - Trade-by-trade analysis
    """
    
    def __init__(self, config):
        """Initialize backtest runner"""
        
        self.config = config
        
        # Backtest configuration
        bt_config = config.get('backtesting', {})
        self.start_date = bt_config.get('start_date', '2023-01-01')
        self.end_date = bt_config.get('end_date', '2025-12-31')
        self.initial_capital = bt_config.get('initial_capital', 3000)
        
        # Components
        self.simulator = RealisticSimulator(config)
        self.microstructure = MarketMicrostructure()
        
        # State
        self.portfolio = {
            'cash': self.initial_capital,
            'positions': {},
            'equity': self.initial_capital
        }
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        self.daily_returns: List[float] = []
        
        logger.info(
            f"✓ Backtest Runner initialized "
            f"({self.start_date} to {self.end_date}, capital=€{self.initial_capital})"
        )
    
    async def run_backtest(self,
                          historical_data: pd.DataFrame,
                          strategy) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            historical_data: DataFrame with OHLCV data
            strategy: Strategy instance to test
            
        Returns:
            Dict with backtest results
        """
        
        logger.info(f"Starting backtest for {strategy.name}...")
        
        # Filter data by date range
        data = self._filter_date_range(historical_data)
        
        if data.empty:
            logger.error("No data in specified date range")
            return {}
        
        logger.info(f"Backtesting {len(data)} data points")
        
        # Reset state
        self.portfolio['cash'] = self.initial_capital
        self.portfolio['positions'].clear()
        self.portfolio['equity'] = self.initial_capital
        self.trades.clear()
        self.equity_curve = [self.initial_capital]
        self.daily_returns.clear()
        
        # Iterate through historical data
        for i in range(len(data)):
            
            # Get data up to current point
            current_data = data.iloc[:i+1]
            
            if len(current_data) < 50:
                continue  # Need minimum data for indicators
            
            # Update microstructure
            self.microstructure.update(current_data)
            
            # Generate signal
            signal = await strategy.generate_signal(current_data)
            
            if signal is None:
                # Update equity (mark-to-market)
                self._update_equity(current_data.iloc[-1])
                continue
            
            # Check if we can trade
            if signal.action == 'BUY' and self.portfolio['cash'] < 100:
                continue  # Insufficient cash
            
            # Calculate position size (simplified)
            if signal.action == 'BUY':
                position_size = min(self.portfolio['cash'] * 0.1, self.portfolio['cash'])
            else:
                # For demo, skip sells if no position
                if not self.portfolio['positions']:
                    continue
                position_size = list(self.portfolio['positions'].values())[0].get('value', 0)
            
            # Simulate execution
            execution = self.simulator.simulate_trade(
                action=signal.action,
                size=position_size,
                price=signal.entry_price,
                market_data=current_data
            )
            
            if not execution['executed']:
                continue
            
            # Update portfolio
            self._process_execution(signal, execution)
            
            # Update equity
            self._update_equity(current_data.iloc[-1])
        
        # Calculate performance metrics
        results = self._calculate_performance()
        
        logger.info(f"✓ Backtest complete: {results.get('total_return', 0):.2%} return")
        
        return results
    
    def _filter_date_range(self, data: pd.DataFrame) -> pd.DataFrame:
        """Filter data by date range"""
        
        if 'timestamp' not in data.columns:
            return data
        
        mask = (
            (data['timestamp'] >= pd.to_datetime(self.start_date)) &
            (data['timestamp'] <= pd.to_datetime(self.end_date))
        )
        
        return data[mask].copy()
    
    def _process_execution(self, signal, execution: Dict):
        """Process trade execution and update portfolio"""
        
        if signal.action == 'BUY':
            # Buy: reduce cash, add position
            self.portfolio['cash'] -= execution['total_cost']
            
            self.portfolio['positions'][signal.symbol] = {
                'size': execution['size_filled'],
                'entry_price': execution['execution_price'],
                'value': execution['size_filled'],
                'entry_time': execution['timestamp']
            }
        
        else:  # SELL
            # Sell: add cash, remove position
            self.portfolio['cash'] += execution['size_filled']
            
            if signal.symbol in self.portfolio['positions']:
                del self.portfolio['positions'][signal.symbol]
        
        # Record trade
        trade_record = {
            **execution,
            'symbol': signal.symbol,
            'strategy': signal.strategy,
            'portfolio_value': self.portfolio['equity']
        }
        self.trades.append(trade_record)
    
    def _update_equity(self, current_market: pd.Series):
        """Update portfolio equity based on current prices"""
        
        equity = self.portfolio['cash']
        
        # Mark positions to market
        current_price = current_market.get('close', 0)
        for symbol, position in self.portfolio['positions'].items():
            position_value = position['size']
            equity += position_value
        
        self.portfolio['equity'] = equity
        self.equity_curve.append(equity)
        
        # Calculate daily return
        if len(self.equity_curve) > 1:
            daily_return = (equity - self.equity_curve[-2]) / self.equity_curve[-2]
            self.daily_returns.append(daily_return)
    
    def _calculate_performance(self) -> Dict:
        """Calculate comprehensive performance metrics"""
        
        if not self.trades or not self.equity_curve:
            return {}
        
        # Total return
        total_return = (self.portfolio['equity'] - self.initial_capital) / self.initial_capital
        
        # Sharpe ratio
        if len(self.daily_returns) > 1:
            sharpe = np.mean(self.daily_returns) / (np.std(self.daily_returns) + 1e-8) * np.sqrt(252)
        else:
            sharpe = 0.0
        
        # Max drawdown
        equity_array = np.array(self.equity_curve)
        running_max = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        # Win rate
        profitable_trades = sum(1 for t in self.trades if t.get('slippage', 0) < 0.01)
        win_rate = profitable_trades / len(self.trades) if self.trades else 0
        
        # Average trade
        avg_trade_return = np.mean([
            t.get('slippage', 0) for t in self.trades
        ]) if self.trades else 0
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': self.portfolio['equity'],
            'total_return': total_return,
            'total_return_pct': total_return * 100,
            'sharpe_ratio': sharpe,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown * 100,
            'total_trades': len(self.trades),
            'win_rate': win_rate,
            'avg_trade_return': avg_trade_return,
            'equity_curve': self.equity_curve,
            'daily_returns': self.daily_returns,
            'trades': self.trades
        }
    
    def save_results(self, results: Dict, filename: str = 'backtest_results.csv'):
        """Save backtest results to CSV"""
        
        if not results:
            return
        
        # Save trades
        trades_df = pd.DataFrame(results['trades'])
        trades_df.to_csv(f'logs/{filename}', index=False)
        
        logger.info(f"✓ Backtest results saved to logs/{filename}")
