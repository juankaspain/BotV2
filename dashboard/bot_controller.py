#!/usr/bin/env python3
"""
BotV2 - Bot Controller for Dashboard v4.2

Provides control interface for the dashboard to manage the bot:
- Start/Stop/Restart operations
- Strategy enable/disable
- Risk parameter updates
- Quick actions (close positions, pause trading)
"""

import json
import os
import signal
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
import threading

logger = logging.getLogger(__name__)


class BotController:
    """
    Controller for managing BotV2 from the dashboard.
    
    Uses file-based signaling for communication with main.py:
    - .bot_state.json: Current state (running/stopped/pid/uptime)
    - .bot_command.json: Commands from dashboard
    - config/: Configuration updates
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize bot controller"""
        self.base_dir = base_dir or Path(__file__).parent.parent.parent
        self.state_file = self.base_dir / '.bot_state.json'
        self.command_file = self.base_dir / '.bot_command.json'
        self.config_dir = self.base_dir / 'src' / 'config'
        self.main_script = self.base_dir / 'src' / 'main.py'
        
        # Internal state
        self._lock = threading.Lock()
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Ensure control files exist"""
        if not self.state_file.exists():
            self._write_state({
                'status': 'stopped',
                'pid': None,
                'start_time': None,
                'last_update': datetime.now().isoformat()
            })
        
        if not self.command_file.exists():
            self._write_command({'action': None})
    
    def _read_state(self) -> Dict:
        """Read current bot state"""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading state file: {e}")
            return {'status': 'unknown', 'pid': None}
    
    def _write_state(self, state: Dict):
        """Write bot state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(state, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing state file: {e}")
    
    def _write_command(self, command: Dict):
        """Write command for bot to process"""
        try:
            with open(self.command_file, 'w') as f:
                json.dump(command, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing command file: {e}")
    
    # ==================== BOT CONTROL OPERATIONS ====================
    
    def get_status(self) -> Dict:
        """
        Get current bot status
        
        Returns:
            {
                'status': 'running|stopped|paused',
                'pid': int or None,
                'uptime': seconds or None,
                'start_time': ISO timestamp or None,
                'is_trading': bool
            }
        """
        state = self._read_state()
        
        # Calculate uptime if running
        uptime = None
        if state.get('status') == 'running' and state.get('start_time'):
            try:
                start = datetime.fromisoformat(state['start_time'])
                uptime = (datetime.now() - start).total_seconds()
            except:
                pass
        
        # Check if process is actually running
        is_alive = self._check_process_alive(state.get('pid'))
        if not is_alive and state.get('status') == 'running':
            # Process died, update state
            state['status'] = 'stopped'
            state['pid'] = None
            self._write_state(state)
        
        return {
            'status': state.get('status', 'stopped'),
            'pid': state.get('pid'),
            'uptime': uptime,
            'start_time': state.get('start_time'),
            'is_trading': state.get('is_trading', False),
            'last_update': state.get('last_update')
        }
    
    def start_bot(self) -> Dict:
        """
        Start the bot
        
        Returns:
            {'success': bool, 'message': str, 'pid': int or None}
        """
        with self._lock:
            status = self.get_status()
            
            if status['status'] == 'running':
                return {
                    'success': False,
                    'message': 'Bot is already running',
                    'pid': status['pid']
                }
            
            try:
                # Start bot as subprocess
                process = subprocess.Popen(
                    ['python3', str(self.main_script)],
                    cwd=str(self.base_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    start_new_session=True  # Detach from parent
                )
                
                # Update state
                new_state = {
                    'status': 'running',
                    'pid': process.pid,
                    'start_time': datetime.now().isoformat(),
                    'last_update': datetime.now().isoformat(),
                    'is_trading': True
                }
                self._write_state(new_state)
                
                logger.info(f"Bot started with PID {process.pid}")
                
                return {
                    'success': True,
                    'message': f'Bot started successfully',
                    'pid': process.pid
                }
            
            except Exception as e:
                logger.error(f"Failed to start bot: {e}")
                return {
                    'success': False,
                    'message': f'Failed to start bot: {str(e)}',
                    'pid': None
                }
    
    def stop_bot(self, graceful: bool = True) -> Dict:
        """
        Stop the bot
        
        Args:
            graceful: If True, wait for current iteration to finish
        
        Returns:
            {'success': bool, 'message': str}
        """
        with self._lock:
            status = self.get_status()
            
            if status['status'] != 'running':
                return {
                    'success': False,
                    'message': 'Bot is not running'
                }
            
            pid = status['pid']
            if not pid:
                return {
                    'success': False,
                    'message': 'No PID found for bot'
                }
            
            try:
                # Send signal to bot
                if graceful:
                    # SIGTERM for graceful shutdown
                    os.kill(pid, signal.SIGTERM)
                    message = 'Bot stopping gracefully'
                else:
                    # SIGKILL for immediate stop
                    os.kill(pid, signal.SIGKILL)
                    message = 'Bot stopped immediately'
                
                # Update state
                state = self._read_state()
                state['status'] = 'stopped'
                state['pid'] = None
                state['last_update'] = datetime.now().isoformat()
                self._write_state(state)
                
                logger.info(f"Bot stopped (PID {pid})")
                
                return {
                    'success': True,
                    'message': message
                }
            
            except ProcessLookupError:
                # Process already dead
                state = self._read_state()
                state['status'] = 'stopped'
                state['pid'] = None
                self._write_state(state)
                
                return {
                    'success': True,
                    'message': 'Bot was already stopped'
                }
            
            except Exception as e:
                logger.error(f"Failed to stop bot: {e}")
                return {
                    'success': False,
                    'message': f'Failed to stop bot: {str(e)}'
                }
    
    def restart_bot(self) -> Dict:
        """
        Restart the bot (stop + start)
        
        Returns:
            {'success': bool, 'message': str, 'pid': int or None}
        """
        # Stop
        stop_result = self.stop_bot(graceful=True)
        
        if not stop_result['success']:
            return stop_result
        
        # Wait a bit for cleanup
        time.sleep(2)
        
        # Start
        return self.start_bot()
    
    def emergency_stop(self) -> Dict:
        """
        Emergency stop: Close all positions + immediate shutdown
        
        Returns:
            {'success': bool, 'message': str}
        """
        # Send emergency command
        self._write_command({
            'action': 'emergency_stop',
            'timestamp': datetime.now().isoformat()
        })
        
        # Wait a moment for bot to process
        time.sleep(1)
        
        # Force stop
        return self.stop_bot(graceful=False)
    
    def pause_trading(self) -> Dict:
        """
        Pause trading (bot runs but doesn't execute new trades)
        
        Returns:
            {'success': bool, 'message': str}
        """
        self._write_command({
            'action': 'pause_trading',
            'timestamp': datetime.now().isoformat()
        })
        
        # Update state
        state = self._read_state()
        state['is_trading'] = False
        state['last_update'] = datetime.now().isoformat()
        self._write_state(state)
        
        return {
            'success': True,
            'message': 'Trading paused - bot will not execute new trades'
        }
    
    def resume_trading(self) -> Dict:
        """
        Resume trading after pause
        
        Returns:
            {'success': bool, 'message': str}
        """
        self._write_command({
            'action': 'resume_trading',
            'timestamp': datetime.now().isoformat()
        })
        
        # Update state
        state = self._read_state()
        state['is_trading'] = True
        state['last_update'] = datetime.now().isoformat()
        self._write_state(state)
        
        return {
            'success': True,
            'message': 'Trading resumed'
        }
    
    # ==================== QUICK ACTIONS ====================
    
    def close_all_positions(self) -> Dict:
        """
        Close all open positions
        
        Returns:
            {'success': bool, 'message': str}
        """
        self._write_command({
            'action': 'close_all_positions',
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'message': 'Command sent to close all positions'
        }
    
    def reduce_positions(self, percentage: float = 50.0) -> Dict:
        """
        Reduce all positions by percentage
        
        Args:
            percentage: Percentage to reduce (0-100)
        
        Returns:
            {'success': bool, 'message': str}
        """
        if not 0 <= percentage <= 100:
            return {
                'success': False,
                'message': 'Percentage must be between 0 and 100'
            }
        
        self._write_command({
            'action': 'reduce_positions',
            'percentage': percentage,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': True,
            'message': f'Command sent to reduce positions by {percentage}%'
        }
    
    # ==================== HELPER METHODS ====================
    
    def _check_process_alive(self, pid: Optional[int]) -> bool:
        """
        Check if process is alive
        
        Args:
            pid: Process ID
        
        Returns:
            True if process exists and is running
        """
        if not pid:
            return False
        
        try:
            # Send signal 0 to check if process exists
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False


# Singleton instance
_bot_controller = None

def get_bot_controller() -> BotController:
    """Get singleton bot controller instance"""
    global _bot_controller
    if _bot_controller is None:
        _bot_controller = BotController()
    return _bot_controller
