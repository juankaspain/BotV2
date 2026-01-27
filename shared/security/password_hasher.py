"""Password Hashing with Argon2 - SEC-002

Secure password hashing using Argon2id algorithm.
Migration utilities from SHA256 to Argon2.

Dependencies: argon2-cffi
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHash
import hashlib
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Argon2 configuration (production-ready parameters)
ph = PasswordHasher(
    time_cost=3,          # Number of iterations
    memory_cost=65536,    # 64 MB memory usage
    parallelism=4,        # Number of parallel threads
    hash_len=32,          # Output hash length
    salt_len=16           # Salt length
)


class PasswordHasherManager:
    """Manages password hashing and verification with migration support"""
    
    def __init__(self):
        self.argon2_hasher = ph
        self.legacy_algorithm = 'sha256'
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using Argon2id.
        
        Args:
            password: Plain text password
            
        Returns:
            Argon2 hash string
        """
        try:
            return self.argon2_hasher.hash(password)
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    def verify_password(self, password: str, hash_string: str) -> Tuple[bool, bool]:
        """
        Verify a password against a hash (supports both Argon2 and legacy SHA256).
        
        Args:
            password: Plain text password to verify
            hash_string: Hash to verify against
            
        Returns:
            Tuple of (is_valid, needs_rehash)
            - is_valid: True if password matches
            - needs_rehash: True if using legacy algorithm and should be upgraded
        """
        # Try Argon2 verification first
        if hash_string.startswith('$argon2'):
            try:
                self.argon2_hasher.verify(hash_string, password)
                
                # Check if parameters are outdated
                if self.argon2_hasher.check_needs_rehash(hash_string):
                    logger.info("Argon2 hash needs rehashing with updated parameters")
                    return True, True
                
                return True, False
            except (VerifyMismatchError, VerificationError):
                return False, False
            except InvalidHash as e:
                logger.error(f"Invalid Argon2 hash format: {e}")
                return False, False
        
        # Fallback to legacy SHA256 verification
        else:
            return self._verify_legacy_hash(password, hash_string)
    
    def _verify_legacy_hash(self, password: str, hash_string: str) -> Tuple[bool, bool]:
        """
        Verify password against legacy SHA256 hash.
        
        Args:
            password: Plain text password
            hash_string: Legacy SHA256 hash
            
        Returns:
            Tuple of (is_valid, needs_rehash)
        """
        try:
            # Compute SHA256 hash
            computed_hash = hashlib.sha256(password.encode()).hexdigest()
            
            if computed_hash == hash_string:
                logger.warning(f"User authenticated with legacy SHA256 hash - migration recommended")
                return True, True  # Valid but needs migration
            
            return False, False
        except Exception as e:
            logger.error(f"Error verifying legacy hash: {e}")
            return False, False
    
    def migrate_password(self, password: str, old_hash: str) -> Optional[str]:
        """
        Migrate a password from legacy SHA256 to Argon2.
        
        Args:
            password: Plain text password
            old_hash: Old SHA256 hash
            
        Returns:
            New Argon2 hash if migration successful, None otherwise
        """
        is_valid, needs_rehash = self.verify_password(password, old_hash)
        
        if is_valid and needs_rehash:
            try:
                new_hash = self.hash_password(password)
                logger.info("Password successfully migrated to Argon2")
                return new_hash
            except Exception as e:
                logger.error(f"Failed to migrate password: {e}")
                return None
        
        return None
    
    def check_password_strength(self, password: str) -> dict:
        """
        Check password strength metrics.
        
        Args:
            password: Plain text password
            
        Returns:
            Dictionary with strength metrics
        """
        strength = {
            'length': len(password),
            'has_uppercase': any(c.isupper() for c in password),
            'has_lowercase': any(c.islower() for c in password),
            'has_digits': any(c.isdigit() for c in password),
            'has_special': any(not c.isalnum() for c in password),
            'score': 0
        }
        
        # Calculate score
        if strength['length'] >= 8:
            strength['score'] += 1
        if strength['length'] >= 12:
            strength['score'] += 1
        if strength['has_uppercase']:
            strength['score'] += 1
        if strength['has_lowercase']:
            strength['score'] += 1
        if strength['has_digits']:
            strength['score'] += 1
        if strength['has_special']:
            strength['score'] += 1
        
        # Strength level
        if strength['score'] <= 2:
            strength['level'] = 'weak'
        elif strength['score'] <= 4:
            strength['level'] = 'medium'
        else:
            strength['level'] = 'strong'
        
        return strength


# Global instance
password_manager = PasswordHasherManager()


# Helper functions for easy access
def hash_password(password: str) -> str:
    """Hash a password using Argon2"""
    return password_manager.hash_password(password)


def verify_password(password: str, hash_string: str) -> Tuple[bool, bool]:
    """Verify a password against a hash"""
    return password_manager.verify_password(password, hash_string)


def migrate_password(password: str, old_hash: str) -> Optional[str]:
    """Migrate a password from SHA256 to Argon2"""
    return password_manager.migrate_password(password, old_hash)


if __name__ == "__main__":
    # Demo usage
    print("=== Password Hasher Demo ===")
    
    # Test password
    test_password = "SecureP@ssw0rd123"
    
    # Hash password with Argon2
    argon2_hash = hash_password(test_password)
    print(f"\nArgon2 Hash: {argon2_hash[:50]}...")
    
    # Verify Argon2 hash
    is_valid, needs_rehash = verify_password(test_password, argon2_hash)
    print(f"Verification: Valid={is_valid}, Needs Rehash={needs_rehash}")
    
    # Test legacy SHA256 hash
    legacy_hash = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"\nLegacy SHA256: {legacy_hash}")
    
    # Verify legacy hash
    is_valid_legacy, needs_migration = verify_password(test_password, legacy_hash)
    print(f"Legacy Verification: Valid={is_valid_legacy}, Needs Migration={needs_migration}")
    
    # Migrate legacy hash
    if needs_migration:
        new_hash = migrate_password(test_password, legacy_hash)
        print(f"\nMigrated Hash: {new_hash[:50]}...")
    
    # Check password strength
    strength = password_manager.check_password_strength(test_password)
    print(f"\nPassword Strength: {strength['level'].upper()} (score: {strength['score']}/6)")
    print(f"Details: {strength}")
