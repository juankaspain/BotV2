"""
SSL/HTTPS Configuration Helper
Helps configure HTTPS with Let's Encrypt
"""

import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SSLConfig:
    """
    SSL/HTTPS configuration helper
    
    Features:
    - Let's Encrypt certificate generation
    - Certificate renewal automation
    - NGINX configuration generator
    - Certificate validation
    - Development SSL support
    
    Example:
        ssl = SSLConfig(
            domain='bot.example.com',
            email='admin@example.com'
        )
        ssl.generate_certificate()
        ssl.generate_nginx_config()
    """
    
    def __init__(self,
                 domain: Optional[str] = None,
                 email: Optional[str] = None,
                 cert_dir: str = '/etc/letsencrypt'):
        """
        Initialize SSL config
        
        Args:
            domain: Domain name
            email: Email for Let's Encrypt
            cert_dir: Certificate directory
        """
        self.domain = domain or os.getenv('SSL_DOMAIN')
        self.email = email or os.getenv('SSL_EMAIL')
        self.cert_dir = Path(cert_dir)
        
        self.enabled = bool(self.domain and self.email)
        
        if not self.enabled:
            logger.warning("⚠️ SSL config disabled: Missing domain or email")
        else:
            logger.info(f"✓ SSL config initialized (domain: {self.domain})")
    
    def generate_certificate(self, staging: bool = False) -> bool:
        """
        Generate Let's Encrypt certificate using certbot
        
        Args:
            staging: Use staging server (for testing)
            
        Returns:
            True if successful
        """
        if not self.enabled:
            logger.error("SSL config not enabled")
            return False
        
        try:
            cmd = [
                'certbot',
                'certonly',
                '--standalone',
                '-d', self.domain,
                '--email', self.email,
                '--agree-tos',
                '--non-interactive'
            ]
            
            if staging:
                cmd.append('--staging')
            
            logger.info(f"Generating SSL certificate for {self.domain}...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✓ SSL certificate generated for {self.domain}")
                return True
            else:
                logger.error(f"Certificate generation failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error generating certificate: {e}")
            return False
    
    def renew_certificate(self) -> bool:
        """
        Renew Let's Encrypt certificate
        
        Returns:
            True if successful
        """
        try:
            cmd = ['certbot', 'renew', '--quiet']
            
            logger.info("Renewing SSL certificates...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✓ SSL certificates renewed")
                return True
            else:
                logger.error(f"Certificate renewal failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error renewing certificate: {e}")
            return False
    
    def check_certificate_expiry(self) -> Optional[datetime]:
        """
        Check certificate expiration date
        
        Returns:
            Expiration datetime or None
        """
        cert_path = self.cert_dir / 'live' / self.domain / 'fullchain.pem'
        
        if not cert_path.exists():
            logger.warning(f"Certificate not found: {cert_path}")
            return None
        
        try:
            cmd = [
                'openssl', 'x509',
                '-enddate',
                '-noout',
                '-in', str(cert_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse: notAfter=Jan  1 00:00:00 2025 GMT
                date_str = result.stdout.split('=')[1].strip()
                expiry = datetime.strptime(date_str, '%b %d %H:%M:%S %Y %Z')
                
                days_left = (expiry - datetime.now()).days
                logger.info(f"Certificate expires in {days_left} days")
                
                return expiry
        
        except Exception as e:
            logger.error(f"Error checking certificate expiry: {e}")
        
        return None
    
    def generate_nginx_config(self, port: int = 8050) -> str:
        """
        Generate NGINX configuration for HTTPS
        
        Args:
            port: Application port
            
        Returns:
            NGINX configuration string
        """
        config = f"""
# BotV2 Dashboard - HTTPS Configuration
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

server {{
    listen 80;
    server_name {self.domain};
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {self.domain};
    
    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/{self.domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{self.domain}/privkey.pem;
    
    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    
    # Proxy to Flask app
    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
    
    # Logs
    access_log /var/log/nginx/{self.domain}_access.log;
    error_log /var/log/nginx/{self.domain}_error.log;
}}
"""
        return config
    
    def save_nginx_config(self, output_path: str = '/etc/nginx/sites-available/botv2') -> bool:
        """
        Save NGINX configuration to file
        
        Args:
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            config = self.generate_nginx_config()
            
            with open(output_path, 'w') as f:
                f.write(config)
            
            logger.info(f"✓ NGINX config saved to {output_path}")
            logger.info("Next steps:")
            logger.info("1. sudo ln -s /etc/nginx/sites-available/botv2 /etc/nginx/sites-enabled/")
            logger.info("2. sudo nginx -t")
            logger.info("3. sudo systemctl reload nginx")
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving NGINX config: {e}")
            return False
