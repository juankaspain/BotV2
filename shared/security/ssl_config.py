# -*- coding: utf-8 -*-
"""
SSL/TLS Configuration Module
Provides SSL/TLS configuration and utilities
"""

import ssl
import os


class SSLConfig:
    """SSL/TLS configuration class"""
    
    def __init__(self, cert_path=None, key_path=None, ca_path=None):
        self.cert_path = cert_path
        self.key_path = key_path
        self.ca_path = ca_path
    
    def create_ssl_context(self, purpose=ssl.Purpose.CLIENT_AUTH):
        """Create SSL context with secure defaults"""
        context = ssl.create_default_context(purpose)
        
        # Set minimum TLS version
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        
        # Disable insecure protocols
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
        context.options |= ssl.OP_NO_TLSv1
        context.options |= ssl.OP_NO_TLSv1_1
        
        # Load certificates if provided
        if self.cert_path and self.key_path:
            context.load_cert_chain(self.cert_path, self.key_path)
        
        if self.ca_path:
            context.load_verify_locations(self.ca_path)
        
        return context
    
    def get_flask_ssl_context(self):
        """Get SSL context tuple for Flask"""
        if self.cert_path and self.key_path:
            return (self.cert_path, self.key_path)
        return None
    
    @staticmethod
    def verify_cert_exists(cert_path, key_path):
        """Verify certificate files exist"""
        return os.path.exists(cert_path) and os.path.exists(key_path)


# Global SSL config
_ssl_config = None


def init_ssl(cert_path=None, key_path=None, ca_path=None):
    """Initialize SSL configuration"""
    global _ssl_config
    _ssl_config = SSLConfig(cert_path, key_path, ca_path)
    return _ssl_config


def get_ssl_context():
    """Get current SSL context"""
    if _ssl_config:
        return _ssl_config.create_ssl_context()
    return None
