# 🔒 BotV2 Dashboard Security Guide

## Overview

The BotV2 Dashboard v2.0 implements **enterprise-grade security** with multiple layers of protection to ensure safe operation in production environments.

### Security Philosophy: Defense in Depth

We implement multiple independent security layers:

1. **Authentication** - HTTP Basic Auth with SHA-256 hashing
2. **Rate Limiting** - Prevent brute force and DDoS attacks
3. **HTTPS Enforcement** - Protect data in transit
4. **Security Headers** - Prevent common web vulnerabilities
5. **Audit Logging** - Track security events
6. **Environment Separation** - Dev vs Production configuration

---

## 🔐 Security Features

### 1️⃣ HTTP Basic Authentication

**Implementation**: `DashboardAuth` class

**Features**:
- ✅ SHA-256 password hashing
- ✅ Constant-time comparison (timing attack prevention)
- ✅ Failed login attempt logging with IP tracking
- ✅ Environment variable based credentials
- ✅ Temporary password generation for first run

**Configuration**:
```bash
# .env file
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=your_strong_password_here
```

**Best Practices**:
- Use a strong password (16+ characters, mixed case, numbers, symbols)
- Never commit passwords to version control
- Rotate passwords periodically (every 90 days recommended)
- Use different passwords for dev/staging/prod

**Example Strong Password**:
```
Ak#9mP$xL2nQ@7vR4wT
```

---

### 2️⃣ Rate Limiting

**Implementation**: Flask-Limiter with Redis backend

**Limits**:

| Endpoint Type | Limit | Reason |
|--------------|-------|--------|
| **Global** | 10 req/min per IP | Prevent general abuse |
| **API Endpoints** | 20 req/min per IP | Allow dashboard updates |
| **Export/Reports** | 5 req/min per IP | Resource intensive |
| **Health Check** | Unlimited | Docker healthcheck needs |
| **WebSocket** | Unlimited | Real-time updates need |

**Configuration**:
```bash
# .env file
REDIS_HOST=localhost
REDIS_PORT=6379
```

**Response Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 7
X-RateLimit-Reset: 1642780800
```

**429 Response** (Too Many Requests):
```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please slow down.",
  "retry_after": "42 seconds"
}
```

**Testing Rate Limits**:
```bash
# Test with rapid requests
for i in {1..15}; do
  curl -u admin:password http://localhost:8050/api/overview
  echo "Request $i"
done

# Expected: First 10 succeed, rest return 429
```

**Bypass Rate Limiting** (for testing):
```python
# Temporarily disable in code (DEV ONLY)
self.limiter = Limiter(
    app=self.app,
    key_func=get_remote_address,
    default_limits=[],  # Empty = no limits
    enabled=False  # Disable entirely
)
```

---

### 3️⃣ HTTPS Enforcement

**Implementation**: Flask-Talisman

**Production Mode** (`FLASK_ENV=production`):
- ✅ Automatic HTTP → HTTPS redirect
- ✅ Strict-Transport-Security (HSTS) header (1 year)
- ✅ Force HTTPS on all endpoints

**Development Mode** (`FLASK_ENV=development`):
- ⚠️ HTTPS enforcement DISABLED
- ✅ Allows localhost HTTP testing
- ✅ Self-signed certificates accepted

**Configuration**:
```bash
# Production
export FLASK_ENV=production

# Development
export FLASK_ENV=development
```

**HTTPS Headers** (Production):
```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: no-referrer
```

**Testing HTTPS**:
```bash
# Production: HTTP redirects to HTTPS
curl -I http://your-domain.com:8050
# Expect: 301 Moved Permanently → https://

# Development: HTTP allowed
curl -I http://localhost:8050
# Expect: 200 OK
```

**Self-Signed Certificate** (for testing):
```bash
# Generate certificate
openssl req -x509 -newkey rsa:4096 \
  -keyout key.pem -out cert.pem \
  -days 365 -nodes

# Run with SSL
python -m src.dashboard.web_app --ssl-context=(cert.pem,key.pem)
```

---

### 4️⃣ Security Headers

**Content Security Policy (CSP)**:
```
default-src 'self';
script-src 'self' 'unsafe-inline' https://cdn.socket.io https://cdn.plot.ly;
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
connect-src 'self' wss: ws:;
font-src 'self';
frame-ancestors 'none';
```

**Purpose**: Prevents XSS attacks by restricting resource loading

**Other Headers**:

| Header | Value | Purpose |
|--------|-------|--------|
| `X-Frame-Options` | DENY | Prevent clickjacking |
| `X-Content-Type-Options` | nosniff | Prevent MIME sniffing |
| `X-XSS-Protection` | 1; mode=block | Enable browser XSS filter |
| `Referrer-Policy` | no-referrer | Don't leak referer |
| `Permissions-Policy` | (restrictive) | Disable dangerous features |

**Testing Headers**:
```bash
curl -I -u admin:password http://localhost:8050/ | grep "X-"
```

---

### 5️⃣ Audit Logging

**Security Events Logged**:

1. **Successful Login**:
   ```
   ✅ Authenticated user: admin from 192.168.1.100
   ```

2. **Failed Login**:
   ```
   🚫 Failed login attempt from 192.168.1.100 (username: admin) on /api/overview
   ```

3. **Rate Limit Exceeded**:
   ```
   ⚠️ Rate limit exceeded from 192.168.1.100 on /api/overview
   ```

4. **WebSocket Connection**:
   ```
   🔗 WebSocket client connected: abc123 from 192.168.1.100
   ❌ WebSocket client disconnected: abc123
   ```

**Log Location**:
```
logs/dashboard.log         # Application logs
logs/security.log          # Security-specific logs (if configured)
```

**Log Rotation** (Recommended):
```python
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/dashboard.log',
    maxBytes=10_000_000,  # 10MB
    backupCount=10
)
```

---

## 🛡️ Security Vulnerabilities Addressed

### ✅ Brute Force Attacks
**Mitigation**: Rate limiting (5 login attempts/min per IP)

### ✅ Man-in-the-Middle (MITM)
**Mitigation**: HTTPS enforcement + HSTS

### ✅ Clickjacking
**Mitigation**: X-Frame-Options: DENY

### ✅ Cross-Site Scripting (XSS)
**Mitigation**: CSP headers + X-XSS-Protection

### ✅ MIME Type Sniffing
**Mitigation**: X-Content-Type-Options: nosniff

### ✅ Timing Attacks
**Mitigation**: Constant-time password comparison

### ✅ Session Hijacking
**Mitigation**: HTTPS + secure cookies

### ✅ DDoS Attacks
**Mitigation**: Rate limiting + Redis backend

---

## 📝 Production Deployment Checklist

### Pre-Deployment

- [ ] Set strong `DASHBOARD_PASSWORD` (16+ characters)
- [ ] Set `FLASK_ENV=production`
- [ ] Configure Redis for rate limiting
- [ ] Set up SSL certificates (Let's Encrypt recommended)
- [ ] Configure firewall rules (allow 443, block 80 or redirect)
- [ ] Set up log rotation
- [ ] Configure monitoring/alerting

### Environment Variables

```bash
# Required
export FLASK_ENV=production
export DASHBOARD_PASSWORD="your_strong_password"
export SECRET_KEY="$(openssl rand -hex 32)"

# Optional
export DASHBOARD_USERNAME=admin
export REDIS_HOST=localhost
export REDIS_PORT=6379
```

### Docker Deployment

```yaml
# docker-compose.yml
services:
  botv2-dashboard:
    environment:
      - FLASK_ENV=production
      - DASHBOARD_PASSWORD=${DASHBOARD_PASSWORD}
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_HOST=botv2-redis
    ports:
      - "443:8050"  # HTTPS
    depends_on:
      - botv2-redis
```

### SSL Certificate Setup

**Let's Encrypt (Recommended)**:
```bash
# Install certbot
sudo apt install certbot

# Get certificate
sudo certbot certonly --standalone -d your-domain.com

# Certificates at:
/etc/letsencrypt/live/your-domain.com/fullchain.pem
/etc/letsencrypt/live/your-domain.com/privkey.pem
```

**Configure Nginx Reverse Proxy**:
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:8050;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /socket.io/ {
        proxy_pass http://localhost:8050;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🛠️ Troubleshooting

### Issue: "Rate limit exceeded" immediately

**Cause**: Redis not accessible

**Solution**:
```bash
# Check Redis is running
docker compose ps botv2-redis

# Test Redis connection
redis-cli -h localhost -p 6379 ping
# Expected: PONG

# Check Flask-Limiter logs
docker compose logs botv2-dashboard | grep -i limiter
```

### Issue: "HTTPS required" on localhost

**Cause**: `FLASK_ENV=production` in development

**Solution**:
```bash
# Development
export FLASK_ENV=development

# Or in .env
FLASK_ENV=development
```

### Issue: WebSocket not connecting

**Cause**: CSP blocking WebSocket

**Solution**: Already configured, but check:
```javascript
// Browser console
// Should see: WebSocket connection to 'ws://localhost:8050/socket.io/...' 
```

### Issue: Health check failing

**Cause**: Rate limiting health check (shouldn't happen)

**Solution**: Health check is exempt, but verify:
```bash
curl http://localhost:8050/health
# Should always work, no auth needed
```

---

## 📊 Security Monitoring

### Key Metrics to Monitor

1. **Failed Login Attempts**
   - Threshold: > 10 per hour from single IP
   - Action: Block IP temporarily

2. **Rate Limit Hits**
   - Threshold: > 100 per hour total
   - Action: Investigate potential attack

3. **WebSocket Connections**
   - Threshold: > 50 concurrent
   - Action: Check for resource exhaustion

4. **API Response Times**
   - Threshold: > 2 seconds average
   - Action: Investigate performance issue

### Alerting (Example with Prometheus)

```yaml
groups:
  - name: dashboard_security
    rules:
      - alert: HighFailedLoginRate
        expr: rate(dashboard_failed_logins[5m]) > 0.1
        annotations:
          summary: "High rate of failed login attempts"
      
      - alert: RateLimitExceeded
        expr: rate(dashboard_rate_limits[5m]) > 1
        annotations:
          summary: "Rate limiting triggered frequently"
```

---

## 📜 Compliance Considerations

### GDPR
- ✅ No PII stored in logs (only IP addresses)
- ✅ Data encrypted in transit (HTTPS)
- ✅ Access logs for audit trail

### PCI-DSS (if applicable)
- ✅ Strong authentication
- ✅ Encrypted communications
- ✅ Access logging
- ✅ Rate limiting (prevent enumeration)

### SOC 2
- ✅ Security controls documented
- ✅ Audit logging enabled
- ✅ Access controls implemented

---

## 🔐 Future Security Enhancements

**Planned for v3.0**:

1. **Flask-Login** - Session-based authentication
2. **OAuth2** - Integration with external identity providers
3. **2FA/MFA** - Two-factor authentication support
4. **API Keys** - Alternative to Basic Auth
5. **IP Whitelisting** - Restrict access by IP range
6. **Geo-blocking** - Block requests from specific countries
7. **WAF Integration** - Web Application Firewall support
8. **SIEM Integration** - Security Information and Event Management

**Vote on priorities**: [GitHub Discussions](https://github.com/juankaspain/BotV2/discussions)

---

## 📧 Security Contact

To report security vulnerabilities:

- **Email**: juanka755@hotmail.com
- **Subject**: [SECURITY] BotV2 Dashboard Vulnerability
- **Response Time**: 24-48 hours

**Please do NOT** open public GitHub issues for security vulnerabilities.

---

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security Best Practices](https://flask.palletsprojects.com/en/stable/security/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Redis Security](https://redis.io/docs/manual/security/)

---

**Last Updated**: January 21, 2026  
**Version**: 2.0-secure  
**Status**: Production Ready ✅