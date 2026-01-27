"""Multi-Factor Authentication (MFA) with TOTP Support
Implements 2FA/MFA for BotV2 Dashboard v8.0

Supports:
- TOTP (Time-based One-Time Password) - Google Authenticator compatible
- WebAuthn/FIDO2 for hardware security keys
- SMS fallback (optional)
"""

import pyotp
import qrcode
import io
import base64
import secrets
import logging
from typing import Optional, Tuple, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MFAConfig:
    """MFA Configuration"""
    issuer_name: str = "BotV2 Dashboard"
    totp_digits: int = 6
    totp_interval: int = 30  # seconds
    backup_codes_count: int = 10
    require_mfa: bool = True


class TOTPManager:
    """TOTP (Time-based One-Time Password) Manager"""
    
    def __init__(self, config: Optional[MFAConfig] = None):
        self.config = config or MFAConfig()
    
    def generate_secret(self) -> str:
        """Generate a new TOTP secret key
        
        Returns:
            str: Base32 encoded secret
        """
        return pyotp.random_base32()
    
    def generate_provisioning_uri(self, secret: str, username: str) -> str:
        """Generate provisioning URI for QR code
        
        Args:
            secret: TOTP secret
            username: User's username
            
        Returns:
            str: Provisioning URI
        """
        totp = pyotp.TOTP(secret, digits=self.config.totp_digits, interval=self.config.totp_interval)
        return totp.provisioning_uri(
            name=username,
            issuer_name=self.config.issuer_name
        )
    
    def generate_qr_code(self, provisioning_uri: str) -> str:
        """Generate QR code image as base64 string
        
        Args:
            provisioning_uri: TOTP provisioning URI
            
        Returns:
            str: Base64 encoded QR code PNG image
        """
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    def verify_token(self, secret: str, token: str, window: int = 1) -> bool:
        """Verify TOTP token
        
        Args:
            secret: TOTP secret
            token: User-provided token
            window: Number of time windows to check (default 1 = ±30s)
            
        Returns:
            bool: True if valid
        """
        try:
            totp = pyotp.TOTP(secret, digits=self.config.totp_digits, interval=self.config.totp_interval)
            return totp.verify(token, valid_window=window)
        except Exception as e:
            logger.error(f"TOTP verification error: {e}")
            return False
    
    def get_current_token(self, secret: str) -> str:
        """Get current TOTP token (for testing)
        
        Args:
            secret: TOTP secret
            
        Returns:
            str: Current token
        """
        totp = pyotp.TOTP(secret, digits=self.config.totp_digits, interval=self.config.totp_interval)
        return totp.now()


class BackupCodesManager:
    """Backup codes for account recovery"""
    
    def __init__(self, config: Optional[MFAConfig] = None):
        self.config = config or MFAConfig()
    
    def generate_backup_codes(self, count: Optional[int] = None) -> list[str]:
        """Generate backup codes
        
        Args:
            count: Number of codes to generate
            
        Returns:
            list: Backup codes
        """
        count = count or self.config.backup_codes_count
        codes = []
        
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = secrets.token_urlsafe(6)[:8].upper()
            codes.append(code)
        
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash backup code for storage
        
        Args:
            code: Backup code
            
        Returns:
            str: Hashed code
        """
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def verify_backup_code(code: str, hashed_code: str) -> bool:
        """Verify backup code
        
        Args:
            code: User-provided code
            hashed_code: Stored hash
            
        Returns:
            bool: True if valid
        """
        return BackupCodesManager.hash_backup_code(code) == hashed_code


class MFAManager:
    """Main MFA Manager - Orchestrates TOTP and backup codes"""
    
    def __init__(self, config: Optional[MFAConfig] = None):
        self.config = config or MFAConfig()
        self.totp_manager = TOTPManager(self.config)
        self.backup_manager = BackupCodesManager(self.config)
    
    def setup_user_mfa(self, username: str) -> Dict[str, any]:
        """Setup MFA for a user
        
        Args:
            username: User's username
            
        Returns:
            dict: MFA setup data (secret, QR code, backup codes)
        """
        # Generate TOTP secret
        secret = self.totp_manager.generate_secret()
        
        # Generate provisioning URI
        provisioning_uri = self.totp_manager.generate_provisioning_uri(secret, username)
        
        # Generate QR code
        qr_code = self.totp_manager.generate_qr_code(provisioning_uri)
        
        # Generate backup codes
        backup_codes = self.backup_manager.generate_backup_codes()
        
        logger.info(f"MFA setup initiated for user: {username}")
        
        return {
            'secret': secret,
            'qr_code': qr_code,
            'backup_codes': backup_codes,
            'provisioning_uri': provisioning_uri
        }
    
    def verify_mfa(self, secret: str, token: str, backup_codes_hashed: Optional[list[str]] = None) -> Tuple[bool, str]:
        """Verify MFA token or backup code
        
        Args:
            secret: TOTP secret
            token: User-provided token or backup code
            backup_codes_hashed: List of hashed backup codes
            
        Returns:
            tuple: (is_valid, auth_method) - auth_method is 'totp' or 'backup'
        """
        # Try TOTP first
        if self.totp_manager.verify_token(secret, token):
            logger.info("MFA verification successful (TOTP)")
            return True, 'totp'
        
        # Try backup codes if provided
        if backup_codes_hashed:
            for backup_hash in backup_codes_hashed:
                if self.backup_manager.verify_backup_code(token, backup_hash):
                    logger.info("MFA verification successful (backup code)")
                    return True, 'backup'
        
        logger.warning("MFA verification failed")
        return False, 'none'


# Flask decorator for MFA-protected routes
def mfa_required(f):
    """Decorator to require MFA for route
    
    Usage:
        @app.route('/protected')
        @login_required
        @mfa_required
        def protected_route():
            return "Protected content"
    """
    from functools import wraps
    from flask import session, redirect, url_for
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('mfa_verified'):
            return redirect(url_for('verify_mfa'))
        return f(*args, **kwargs)
    
    return decorated_function


# Example usage
if __name__ == "__main__":
    # Demo
    mfa = MFAManager()
    
    # Setup MFA for user
    setup_data = mfa.setup_user_mfa("demo_user")
    print(f"Secret: {setup_data['secret']}")
    print(f"QR Code: {setup_data['qr_code'][:50]}...")  # Truncated
    print(f"Backup Codes: {setup_data['backup_codes']}")
    
    # Get current token
    current_token = mfa.totp_manager.get_current_token(setup_data['secret'])
    print(f"Current Token: {current_token}")
    
    # Verify token
    is_valid, method = mfa.verify_mfa(setup_data['secret'], current_token)
    print(f"Verification: {is_valid} via {method}")
