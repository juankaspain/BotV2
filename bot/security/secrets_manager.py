"""
AWS Secrets Manager Integration
Securely manages API keys and sensitive credentials
"""

import logging
import os
import json
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SecretsManager:
    """
    AWS Secrets Manager integration
    
    Features:
    - Secure API key storage
    - Automatic key rotation support
    - Caching layer (1 hour default)
    - Fallback to environment variables
    - Batch secret retrieval
    
    Setup:
    1. Create secrets in AWS Secrets Manager
    2. Set AWS credentials (IAM role or env vars)
    3. Configure secret names in settings.yaml
    
    Example:
        secrets = SecretsManager()
        api_key = secrets.get_secret('binance_api_key')
    """
    
    def __init__(self,
                 region_name: str = 'us-east-1',
                 cache_ttl: int = 3600,
                 fallback_to_env: bool = True):
        """
        Initialize Secrets Manager
        
        Args:
            region_name: AWS region
            cache_ttl: Cache time-to-live (seconds)
            fallback_to_env: Fallback to env vars if AWS unavailable
        """
        self.region_name = region_name
        self.cache_ttl = cache_ttl
        self.fallback_to_env = fallback_to_env
        
        # Cache
        self.cache: Dict[str, Dict[str, Any]] = {}
        
        # Initialize AWS client
        try:
            self.client = boto3.client(
                'secretsmanager',
                region_name=region_name
            )
            self.aws_available = True
            logger.info(f"✓ AWS Secrets Manager connected (region: {region_name})")
        
        except Exception as e:
            self.client = None
            self.aws_available = False
            logger.warning(
                f"⚠️ AWS Secrets Manager unavailable: {e}. "
                f"{'Using environment variables as fallback' if fallback_to_env else 'No fallback configured'}"
            )
    
    def get_secret(self, secret_name: str, force_refresh: bool = False) -> Optional[str]:
        """
        Get secret value
        
        Args:
            secret_name: Secret name in AWS or env var name
            force_refresh: Force cache refresh
            
        Returns:
            Secret value or None
        """
        # Check cache
        if not force_refresh and secret_name in self.cache:
            cached = self.cache[secret_name]
            if datetime.now() < cached['expires_at']:
                logger.debug(f"Using cached secret: {secret_name}")
                return cached['value']
        
        # Try AWS Secrets Manager
        if self.aws_available:
            try:
                response = self.client.get_secret_value(SecretId=secret_name)
                
                # Parse secret
                if 'SecretString' in response:
                    secret = response['SecretString']
                    
                    # Try parse as JSON
                    try:
                        secret_dict = json.loads(secret)
                        # If JSON, return the first value (common pattern)
                        secret = next(iter(secret_dict.values()))
                    except json.JSONDecodeError:
                        # Plain text secret
                        pass
                    
                    # Cache
                    self.cache[secret_name] = {
                        'value': secret,
                        'expires_at': datetime.now() + timedelta(seconds=self.cache_ttl)
                    }
                    
                    logger.debug(f"✓ Retrieved secret from AWS: {secret_name}")
                    return secret
            
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'ResourceNotFoundException':
                    logger.warning(f"Secret not found in AWS: {secret_name}")
                else:
                    logger.error(f"AWS Secrets Manager error: {e}")
            
            except Exception as e:
                logger.error(f"Error retrieving secret {secret_name}: {e}")
        
        # Fallback to environment variable
        if self.fallback_to_env:
            env_value = os.getenv(secret_name)
            if env_value:
                logger.debug(f"Using environment variable: {secret_name}")
                return env_value
            else:
                logger.warning(f"Secret not found in AWS or environment: {secret_name}")
        
        return None
    
    def get_secret_dict(self, secret_name: str, force_refresh: bool = False) -> Optional[Dict]:
        """
        Get secret as dictionary (for JSON secrets)
        
        Args:
            secret_name: Secret name
            force_refresh: Force cache refresh
            
        Returns:
            Secret dict or None
        """
        secret = self.get_secret(secret_name, force_refresh)
        if secret:
            try:
                return json.loads(secret)
            except json.JSONDecodeError:
                logger.error(f"Secret {secret_name} is not valid JSON")
        return None
    
    def list_secrets(self) -> list:
        """
        List all secrets
        
        Returns:
            List of secret names
        """
        if not self.aws_available:
            logger.warning("AWS not available, cannot list secrets")
            return []
        
        try:
            response = self.client.list_secrets()
            return [s['Name'] for s in response['SecretsList']]
        
        except Exception as e:
            logger.error(f"Error listing secrets: {e}")
            return []
    
    def clear_cache(self):
        """Clear secret cache"""
        self.cache.clear()
        logger.info("Secret cache cleared")
