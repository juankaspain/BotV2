# -*- coding: utf-8 -*-
"""
Secrets Manager Module
Provides secure secrets management
"""

import os
import json
import base64
from cryptography.fernet import Fernet
from functools import lru_cache


class SecretsManager:
    """Secrets manager for secure credential storage"""
    
    def __init__(self, encryption_key=None):
        self._secrets = {}
        self._encryption_key = encryption_key or os.environ.get('SECRETS_KEY')
        self._fernet = None
        
        if self._encryption_key:
            self._fernet = Fernet(self._encryption_key.encode())
    
    def set_secret(self, key, value):
        """Store a secret"""
        if self._fernet:
            encrypted = self._fernet.encrypt(value.encode())
            self._secrets[key] = encrypted.decode()
        else:
            self._secrets[key] = value
    
    def get_secret(self, key, default=None):
        """Retrieve a secret"""
        value = self._secrets.get(key)
        
        if value is None:
            # Try environment variable
            value = os.environ.get(key)
            if value:
                return value
            return default
        
        if self._fernet:
            try:
                decrypted = self._fernet.decrypt(value.encode())
                return decrypted.decode()
            except Exception:
                return default
        
        return value
    
    def delete_secret(self, key):
        """Delete a secret"""
        if key in self._secrets:
            del self._secrets[key]
    
    def load_from_file(self, filepath):
        """Load secrets from encrypted file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self._secrets.update(data)
    
    def save_to_file(self, filepath):
        """Save secrets to encrypted file"""
        with open(filepath, 'w') as f:
            json.dump(self._secrets, f)
    
    @staticmethod
    def generate_key():
        """Generate a new encryption key"""
        return Fernet.generate_key().decode()


# Global secrets manager
_secrets_manager = None


def get_secrets_manager():
    """Get or create secrets manager"""
    global _secrets_manager
    if _secrets_manager is None:
        _secrets_manager = SecretsManager()
    return _secrets_manager


@lru_cache(maxsize=128)
def get_secret(key, default=None):
    """Get a secret value"""
    return get_secrets_manager().get_secret(key, default)
