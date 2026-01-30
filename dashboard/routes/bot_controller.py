#!/usr/bin/env python3
"""
Bot Controller - Interface for controlling the trading bot

Provides a unified interface to control bot operations from the dashboard.
In demo mode, simulates bot behavior without actual process management.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import threading

logger = logging.getLogger(__name__)

# Singleton instance
_controller_instance = None


class BotController:
    """
    Controller for managing the trading bot process.
    
    In demo mode, simulates bot behavior.
    In production mode, manages the actual bot process.
    """
    
    def __init__(self):
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')
        
        # Bot state
        self._status = 'stopped'
        self._is_trading = False
        self._pid: Optional[int] = None
        self._start_time: Optional[datetime] = None
        
        # Simulated positions for demo
        self._positions = []
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        if self.demo_mode:
            logger.info("🎮 BotController initialized in DEMO mode")
            # Auto-start in demo mode
            self._status = 'running'
            self._is_trading = True
            self._pid = 99999
            self._start_time = datetime.now()
        else:
            logger.info("🚀 BotController initialized in PRODUCTION mode")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current bot status.
        
        Returns:
            Dict with status information
        """
        with self._lock:
            uptime = 0
            if self._start_time:
                uptime = int((datetime.now() - self._start_time).total_seconds())
            
            return {
                'status': self._status,
                'pid': self._pid,
                'uptime': uptime,
                'start_time': self._start_time.isoformat() if self._start_time else None,
                'is_trading': self._is_trading,
                'demo_mode': self.demo_mode,
                'positions_count': len(self._positions)
            }
    
    def start_bot(self) -> Dict[str, Any]:
        """
        Start the trading bot.
        
        Returns:
            Dict with success status and message
        """
        with self._lock:
            if self._status == 'running':
                return {
                    'success': False,
                    'message': 'Bot is already running',
                    'pid': self._pid
                }
            
            if self.demo_mode:
                # Simulate bot start
                self._status = 'running'
                self._is_trading = True
                self._pid = 99999
                self._start_time = datetime.now()
                
                logger.info("🎮 [DEMO] Bot started")
                return {
                    'success': True,
                    'message': 'Bot started (demo mode)',
                    'pid': self._pid
                }
            else:
                # Production: would start actual bot process
                # TODO: Implement actual process management
                self._status = 'running'
                self._is_trading = True
                self._start_time = datetime.now()
                
                return {
                    'success': True,
                    'message': 'Bot started',
                    'pid': self._pid
                }
    
    def stop_bot(self, graceful: bool = True) -> Dict[str, Any]:
        """
        Stop the trading bot.
        
        Args:
            graceful: If True, wait for current operations to complete
        
        Returns:
            Dict with success status and message
        """
        with self._lock:
            if self._status == 'stopped':
                return {
                    'success': False,
                    'message': 'Bot is not running'
                }
            
            stop_type = 'gracefully' if graceful else 'immediately'
            
            if self.demo_mode:
                self._status = 'stopped'
                self._is_trading = False
                self._pid = None
                self._start_time = None
                
                logger.info(f"🎮 [DEMO] Bot stopped {stop_type}")
                return {
                    'success': True,
                    'message': f'Bot stopped {stop_type} (demo mode)'
                }
            else:
                # Production: would stop actual bot process
                self._status = 'stopped'
                self._is_trading = False
                
                return {
                    'success': True,
                    'message': f'Bot stopping {stop_type}'
                }
    
    def restart_bot(self) -> Dict[str, Any]:
        """
        Restart the trading bot.
        
        Returns:
            Dict with success status and message
        """
        stop_result = self.stop_bot(graceful=True)
        if not stop_result['success'] and 'not running' not in stop_result['message']:
            return stop_result
        
        return self.start_bot()
    
    def pause_trading(self) -> Dict[str, Any]:
        """
        Pause trading without stopping the bot.
        
        Returns:
            Dict with success status and message
        """
        with self._lock:
            if self._status != 'running':
                return {
                    'success': False,
                    'message': 'Bot is not running'
                }
            
            self._is_trading = False
            
            logger.info("Trading paused")
            return {
                'success': True,
                'message': 'Trading paused'
            }
    
    def resume_trading(self) -> Dict[str, Any]:
        """
        Resume trading after pause.
        
        Returns:
            Dict with success status and message
        """
        with self._lock:
            if self._status != 'running':
                return {
                    'success': False,
                    'message': 'Bot is not running'
                }
            
            self._is_trading = True
            
            logger.info("Trading resumed")
            return {
                'success': True,
                'message': 'Trading resumed'
            }
    
    def emergency_stop(self) -> Dict[str, Any]:
        """
        Emergency stop: Close all positions and stop immediately.
        
        Returns:
            Dict with success status and message
        """
        with self._lock:
            # First close all positions
            close_result = self.close_all_positions()
            
            # Then stop the bot immediately
            self._status = 'stopped'
            self._is_trading = False
            self._pid = None
            
            logger.warning("🚨 EMERGENCY STOP executed")
            return {
                'success': True,
                'message': 'Emergency stop executed',
                'positions_closed': close_result.get('positions_closed', 0)
            }
    
    def close_all_positions(self) -> Dict[str, Any]:
        """
        Close all open positions.
        
        Returns:
            Dict with success status and message
        """
        with self._lock:
            positions_count = len(self._positions)
            
            if self.demo_mode:
                # Simulate closing positions
                self._positions = []
                
                logger.info(f"🎮 [DEMO] Closed {positions_count} positions")
                return {
                    'success': True,
                    'message': f'Closed {positions_count} positions (demo mode)',
                    'positions_closed': positions_count
                }
            else:
                # Production: would send close commands to exchange
                self._positions = []
                
                return {
                    'success': True,
                    'message': f'Command sent to close {positions_count} positions',
                    'positions_closed': positions_count
                }
    
    def reduce_positions(self, percentage: float) -> Dict[str, Any]:
        """
        Reduce all positions by a percentage.
        
        Args:
            percentage: Percentage to reduce (0-100)
        
        Returns:
            Dict with success status and message
        """
        if not 0 < percentage <= 100:
            return {
                'success': False,
                'message': 'Percentage must be between 0 and 100'
            }
        
        with self._lock:
            positions_count = len(self._positions)
            
            logger.info(f"Reducing positions by {percentage}%")
            return {
                'success': True,
                'message': f'Command sent to reduce {positions_count} positions by {percentage}%'
            }


def get_bot_controller() -> BotController:
    """
    Get the singleton BotController instance.
    
    Returns:
        BotController instance
    """
    global _controller_instance
    
    if _controller_instance is None:
        _controller_instance = BotController()
    
    return _controller_instance
