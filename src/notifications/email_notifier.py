"""
Email Notifier
Sends email notifications for daily summaries and critical events
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, List
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Email notification system for summaries and critical events
    
    Features:
    - HTML formatted emails
    - Daily/weekly summaries
    - Critical event notifications
    - SMTP with TLS
    - Attachment support
    
    Required env vars:
    - EMAIL_HOST: SMTP server (e.g., smtp.gmail.com)
    - EMAIL_PORT: SMTP port (e.g., 587)
    - EMAIL_USERNAME: Email username
    - EMAIL_PASSWORD: Email password
    - EMAIL_FROM: From address
    - EMAIL_TO: Recipient address(es)
    """
    
    def __init__(self,
                 smtp_host: Optional[str] = None,
                 smtp_port: Optional[int] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 from_email: Optional[str] = None,
                 to_emails: Optional[List[str]] = None):
        """
        Initialize email notifier
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            username: SMTP username
            password: SMTP password
            from_email: From email address
            to_emails: List of recipient emails
        """
        self.smtp_host = smtp_host or os.getenv('EMAIL_HOST', 'smtp.gmail.com')
        self.smtp_port = smtp_port or int(os.getenv('EMAIL_PORT', '587'))
        self.username = username or os.getenv('EMAIL_USERNAME')
        self.password = password or os.getenv('EMAIL_PASSWORD')
        self.from_email = from_email or os.getenv('EMAIL_FROM')
        to_env = os.getenv('EMAIL_TO', '')
        self.to_emails = to_emails or (to_env.split(',') if to_env else [])
        
        self.enabled = all([
            self.smtp_host,
            self.smtp_port,
            self.username,
            self.password,
            self.from_email,
            self.to_emails
        ])
        
        if not self.enabled:
            logger.warning("⚠️ Email notifier disabled: Missing configuration")
        else:
            logger.info(f"✓ Email notifier initialized (to: {len(self.to_emails)} recipients)")
        
        # Statistics
        self.emails_sent = 0
        self.emails_failed = 0
    
    def send_email(self,
                   subject: str,
                   body: str,
                   html: bool = False) -> bool:
        """
        Send email
        
        Args:
            subject: Email subject
            body: Email body (plain text or HTML)
            html: If True, body is HTML
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.debug(f"Email disabled, would send: {subject}")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.to_emails)
            
            # Attach body
            mime_type = 'html' if html else 'plain'
            msg.attach(MIMEText(body, mime_type))
            
            # Send via SMTP
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            self.emails_sent += 1
            logger.info(f"✓ Email sent: {subject}")
            return True
        
        except Exception as e:
            self.emails_failed += 1
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_daily_summary(self,
                          total_pnl: float,
                          trades_count: int,
                          win_rate: float,
                          equity: float,
                          additional_metrics: Optional[Dict] = None) -> bool:
        """
        Send daily performance summary
        
        Args:
            total_pnl: Daily P&L
            trades_count: Number of trades
            win_rate: Win rate percentage
            equity: Current equity
            additional_metrics: Optional additional metrics
        """
        subject = f"BotV2 Daily Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>🤖 BotV2 Trading Bot - Daily Summary</h2>
            <p><b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3>Performance</h3>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <td><b>Daily P&L</b></td>
                    <td style="color: {'green' if total_pnl >= 0 else 'red'};">
                        ${total_pnl:,.2f}
                    </td>
                </tr>
                <tr>
                    <td><b>Total Trades</b></td>
                    <td>{trades_count}</td>
                </tr>
                <tr>
                    <td><b>Win Rate</b></td>
                    <td>{win_rate:.1f}%</td>
                </tr>
                <tr>
                    <td><b>Current Equity</b></td>
                    <td>${equity:,.2f}</td>
                </tr>
        """
        
        if additional_metrics:
            for key, value in additional_metrics.items():
                html += f"""
                <tr>
                    <td><b>{key}</b></td>
                    <td>{value}</td>
                </tr>
                """
        
        html += """
            </table>
            
            <p style="margin-top: 30px; color: #666;">
                <small>This is an automated message from BotV2 Trading System</small>
            </p>
        </body>
        </html>
        """
        
        return self.send_email(subject, html, html=True)
    
    def send_critical_drawdown_alert(self,
                                    drawdown_pct: float,
                                    current_equity: float,
                                    peak_equity: float) -> bool:
        """
        Send critical drawdown alert
        
        Args:
            drawdown_pct: Drawdown percentage
            current_equity: Current equity
            peak_equity: Peak equity
        """
        subject = f"🚨 CRITICAL: Drawdown Alert - {drawdown_pct:.1f}%"
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: red;">🚨 CRITICAL DRAWDOWN ALERT</h2>
            <p><b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <h3 style="color: red;">Drawdown: {drawdown_pct:.2f}%</h3>
            
            <table border="1" cellpadding="5" cellspacing="0">
                <tr>
                    <td><b>Current Equity</b></td>
                    <td>${current_equity:,.2f}</td>
                </tr>
                <tr>
                    <td><b>Peak Equity</b></td>
                    <td>${peak_equity:,.2f}</td>
                </tr>
                <tr style="color: red;">
                    <td><b>Loss</b></td>
                    <td>${peak_equity - current_equity:,.2f}</td>
                </tr>
            </table>
            
            <h3>Recommended Actions:</h3>
            <ul>
                <li>Review open positions immediately</li>
                <li>Consider reducing position sizes</li>
                <li>Check for system anomalies</li>
                <li>Verify strategy performance</li>
            </ul>
            
            <p style="margin-top: 30px; color: #666;">
                <small>This is an automated critical alert from BotV2</small>
            </p>
        </body>
        </html>
        """
        
        return self.send_email(subject, html, html=True)
    
    def get_statistics(self) -> Dict:
        """Get notifier statistics"""
        return {
            'enabled': self.enabled,
            'emails_sent': self.emails_sent,
            'emails_failed': self.emails_failed,
            'success_rate': (self.emails_sent / (self.emails_sent + self.emails_failed) * 100)
                if (self.emails_sent + self.emails_failed) > 0 else 0
        }
