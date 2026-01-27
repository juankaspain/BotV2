"""JWT Token Manager with Rotation - SEC-003

Secure JWT token generation, validation, and automatic rotation.
Blacklist support for revoked tokens.

Dependencies: PyJWT, Redis (optional for token blacklist)
"""

import jwt
import datetime
import secrets
import logging
from typing import Dict, Optional, Tuple, Any
import hashlib
import json

logger = logging.getLogger(__name__)

# Configuration
JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Short-lived access tokens
REFRESH_TOKEN_EXPIRE_DAYS = 7     # Longer refresh tokens
TOKEN_ROTATION_THRESHOLD = 0.5    # Rotate when 50% of lifetime passed


class TokenBlacklist:
    """In-memory token blacklist (production should use Redis)"""
    
    def __init__(self):
        self._blacklist = set()
        self._jti_expiry = {}  # JWT ID -> expiry timestamp
    
    def add(self, jti: str, exp: datetime.datetime):
        """Add token to blacklist"""
        self._blacklist.add(jti)
        self._jti_expiry[jti] = exp
        logger.info(f"Token {jti[:8]}... added to blacklist")
    
    def is_blacklisted(self, jti: str) -> bool:
        """Check if token is blacklisted"""
        return jti in self._blacklist
    
    def cleanup_expired(self):
        """Remove expired tokens from blacklist"""
        now = datetime.datetime.utcnow()
        expired_jtis = [
            jti for jti, exp in self._jti_expiry.items()
            if exp < now
        ]
        
        for jti in expired_jtis:
            self._blacklist.discard(jti)
            del self._jti_expiry[jti]
        
        if expired_jtis:
            logger.info(f"Cleaned up {len(expired_jtis)} expired tokens from blacklist")


class JWTTokenManager:
    """Manages JWT tokens with rotation and security features"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or self._generate_secret_key()
        self.blacklist = TokenBlacklist()
        self.algorithm = JWT_ALGORITHM
    
    @staticmethod
    def _generate_secret_key() -> str:
        """Generate a secure random secret key"""
        return secrets.token_urlsafe(64)
    
    @staticmethod
    def _generate_jti() -> str:
        """Generate unique JWT ID"""
        return secrets.token_urlsafe(32)
    
    def create_access_token(
        self,
        user_id: str,
        additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a short-lived access token.
        
        Args:
            user_id: User identifier
            additional_claims: Extra claims to include in token
            
        Returns:
            Encoded JWT token string
        """
        now = datetime.datetime.utcnow()
        exp = now + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            'sub': user_id,
            'type': 'access',
            'iat': now,
            'exp': exp,
            'jti': self._generate_jti(),
            'nbf': now  # Not before
        }
        
        if additional_claims:
            payload.update(additional_claims)
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Created access token for user {user_id}")
        
        return token
    
    def create_refresh_token(self, user_id: str) -> str:
        """
        Create a long-lived refresh token.
        
        Args:
            user_id: User identifier
            
        Returns:
            Encoded JWT refresh token
        """
        now = datetime.datetime.utcnow()
        exp = now + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        payload = {
            'sub': user_id,
            'type': 'refresh',
            'iat': now,
            'exp': exp,
            'jti': self._generate_jti()
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Created refresh token for user {user_id}")
        
        return token
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (is_valid, payload, error_message)
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={'verify_exp': True}
            )
            
            # Check if token is blacklisted
            jti = payload.get('jti')
            if jti and self.blacklist.is_blacklisted(jti):
                logger.warning(f"Attempted to use blacklisted token {jti[:8]}...")
                return False, None, "Token has been revoked"
            
            return True, payload, None
            
        except jwt.ExpiredSignatureError:
            return False, None, "Token has expired"
        except jwt.InvalidTokenError as e:
            return False, None, f"Invalid token: {str(e)}"
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return False, None, "Token verification failed"
    
    def should_rotate_token(self, token: str) -> bool:
        """
        Check if token should be rotated based on age.
        
        Args:
            token: JWT token string
            
        Returns:
            True if token should be rotated
        """
        is_valid, payload, _ = self.verify_token(token)
        
        if not is_valid or not payload:
            return False
        
        # Only rotate access tokens
        if payload.get('type') != 'access':
            return False
        
        try:
            iat = datetime.datetime.fromtimestamp(payload['iat'])
            exp = datetime.datetime.fromtimestamp(payload['exp'])
            now = datetime.datetime.utcnow()
            
            total_lifetime = (exp - iat).total_seconds()
            elapsed_time = (now - iat).total_seconds()
            
            # Rotate if more than threshold of lifetime has passed
            return (elapsed_time / total_lifetime) >= TOKEN_ROTATION_THRESHOLD
            
        except (KeyError, ValueError) as e:
            logger.error(f"Error checking token rotation: {e}")
            return False
    
    def rotate_token(self, old_token: str) -> Optional[str]:
        """
        Rotate an access token by creating a new one.
        
        Args:
            old_token: Current access token
            
        Returns:
            New access token or None if rotation failed
        """
        is_valid, payload, error = self.verify_token(old_token)
        
        if not is_valid or not payload:
            logger.warning(f"Cannot rotate invalid token: {error}")
            return None
        
        if payload.get('type') != 'access':
            logger.warning("Cannot rotate non-access token")
            return None
        
        # Create new token with same user and claims
        user_id = payload['sub']
        additional_claims = {
            k: v for k, v in payload.items()
            if k not in ['sub', 'type', 'iat', 'exp', 'jti', 'nbf']
        }
        
        new_token = self.create_access_token(user_id, additional_claims)
        logger.info(f"Rotated token for user {user_id}")
        
        return new_token
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a token by adding it to blacklist.
        
        Args:
            token: JWT token to revoke
            
        Returns:
            True if successfully revoked
        """
        is_valid, payload, _ = self.verify_token(token)
        
        if not payload:
            logger.warning("Cannot revoke invalid token")
            return False
        
        jti = payload.get('jti')
        exp = datetime.datetime.fromtimestamp(payload['exp'])
        
        if jti:
            self.blacklist.add(jti, exp)
            return True
        
        return False
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """
        Use a refresh token to generate a new access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token or None if failed
        """
        is_valid, payload, error = self.verify_token(refresh_token)
        
        if not is_valid or not payload:
            logger.warning(f"Invalid refresh token: {error}")
            return None
        
        if payload.get('type') != 'refresh':
            logger.warning("Token is not a refresh token")
            return None
        
        user_id = payload['sub']
        new_access_token = self.create_access_token(user_id)
        
        logger.info(f"Generated new access token from refresh token for user {user_id}")
        return new_access_token
    
    def get_token_info(self, token: str) -> Dict[str, Any]:
        """
        Get information about a token without full verification.
        
        Args:
            token: JWT token
            
        Returns:
            Dictionary with token information
        """
        try:
            # Decode without verification to get claims
            payload = jwt.decode(
                token,
                options={'verify_signature': False, 'verify_exp': False}
            )
            
            info = {
                'user_id': payload.get('sub'),
                'type': payload.get('type'),
                'issued_at': datetime.datetime.fromtimestamp(payload.get('iat', 0)).isoformat(),
                'expires_at': datetime.datetime.fromtimestamp(payload.get('exp', 0)).isoformat(),
                'jti': payload.get('jti'),
                'is_expired': datetime.datetime.fromtimestamp(payload.get('exp', 0)) < datetime.datetime.utcnow()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting token info: {e}")
            return {}


# Global instance (initialize with proper secret in production)
token_manager = JWTTokenManager()


# Helper functions
def create_tokens(user_id: str) -> Dict[str, str]:
    """Create both access and refresh tokens"""
    return {
        'access_token': token_manager.create_access_token(user_id),
        'refresh_token': token_manager.create_refresh_token(user_id),
        'token_type': 'Bearer'
    }


def verify_access_token(token: str) -> Tuple[bool, Optional[str]]:
    """Verify an access token and return (is_valid, user_id)"""
    is_valid, payload, _ = token_manager.verify_token(token)
    
    if is_valid and payload and payload.get('type') == 'access':
        return True, payload.get('sub')
    
    return False, None


if __name__ == "__main__":
    # Demo usage
    print("=== JWT Token Manager Demo ===")
    
    # Create tokens
    user_id = "user_12345"
    tokens = create_tokens(user_id)
    
    print(f"\nAccess Token: {tokens['access_token'][:50]}...")
    print(f"Refresh Token: {tokens['refresh_token'][:50]}...")
    
    # Verify access token
    is_valid, extracted_user_id = verify_access_token(tokens['access_token'])
    print(f"\nAccess Token Valid: {is_valid}")
    print(f"Extracted User ID: {extracted_user_id}")
    
    # Get token info
    info = token_manager.get_token_info(tokens['access_token'])
    print(f"\nToken Info: {json.dumps(info, indent=2)}")
    
    # Check if rotation needed
    should_rotate = token_manager.should_rotate_token(tokens['access_token'])
    print(f"\nShould Rotate: {should_rotate}")
    
    # Revoke token
    revoked = token_manager.revoke_token(tokens['access_token'])
    print(f"\nToken Revoked: {revoked}")
    
    # Try to use revoked token
    is_valid_after_revoke, _ = verify_access_token(tokens['access_token'])
    print(f"Valid After Revoke: {is_valid_after_revoke}")
