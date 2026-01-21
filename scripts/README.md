# 🛠️ BotV2 Scripts

## Available Scripts

### 1. `verify_system.sh` ✅

**Purpose:** Comprehensive system verification

**Checks:**
- ✅ Docker Compose running
- ✅ PostgreSQL connection and health
- ✅ Redis connection and authentication
- ✅ Trading Bot process status
- ✅ Dashboard HTTP endpoint
- ✅ Container health status

**Usage:**
```bash
chmod +x scripts/verify_system.sh
./scripts/verify_system.sh
```

**Output:**
- Green ✓ = OK
- Yellow ⚠ = Warning
- Red ✗ = Error

**Exit Codes:**
- `0` = All systems operational
- `1` = Issues detected

**Example:**
```bash
$ ./scripts/verify_system.sh

═══════════════════════════════════════════════════════════════════
  🔍 BotV2 System Verification
═══════════════════════════════════════════════════════════════════

→ Checking Docker Compose...
✓ Docker Compose is running

→ Checking PostgreSQL...
✓ PostgreSQL is healthy and accepting connections
✓ Database queries working

→ Checking Redis...
✓ Redis is healthy (authenticated)

→ Checking Trading Bot...
✓ Trading Bot container is running
✓ Trading Bot is active (check logs for details)

→ Checking Dashboard...
✓ Dashboard container is running
✓ Dashboard HTTP server responding on port 8050
✓ Access at: http://localhost:8050

═══════════════════════════════════════════════════════════════════
  ✅ ALL SYSTEMS OPERATIONAL
═══════════════════════════════════════════════════════════════════
```

---

### 2. `verify_security.py` 🔒

**Purpose:** Security audit and verification

**Checks:**
- API key validation
- Environment variable security
- Secrets management
- Sensitive data exposure

**Usage:**
```bash
python scripts/verify_security.py
```

---

### 3. `init-db.sql` 🗄️

**Purpose:** Database initialization

**Contains:**
- Table schemas
- Initial data
- Indexes
- Constraints

**Usage:**
```bash
# Run manually if needed
docker exec -i botv2-postgres psql -U botv2_user -d botv2_user < scripts/init-db.sql
```

---

## 🚀 Quick Start

### First time setup:
```bash
# 1. Make scripts executable
chmod +x scripts/*.sh

# 2. Start services
docker compose up -d

# 3. Wait 30 seconds for initialization
sleep 30

# 4. Verify everything is working
./scripts/verify_system.sh
```

### Daily verification:
```bash
./scripts/verify_system.sh
```

### If issues detected:
```bash
# View specific service logs
docker compose logs -f botv2-app        # Trading bot
docker compose logs -f botv2-dashboard  # Dashboard
docker compose logs -f botv2-postgres   # Database
docker compose logs -f botv2-redis      # Cache

# Restart specific service
docker compose restart botv2-app

# Restart all
docker compose restart
```

---

## 📊 Monitoring

### Check service status:
```bash
docker compose ps
```

### View resource usage:
```bash
docker stats botv2-app botv2-dashboard botv2-postgres botv2-redis
```

### Follow all logs:
```bash
docker compose logs -f
```

---

## 🐛 Troubleshooting

### Service not starting:
```bash
# Check why service failed
docker compose logs <service-name>

# Example:
docker compose logs botv2-dashboard --tail=50
```

### Database connection issues:
```bash
# Test PostgreSQL directly
docker exec botv2-postgres pg_isready -U botv2_user

# Connect to database
docker exec -it botv2-postgres psql -U botv2_user -d botv2_user
```

### Redis connection issues:
```bash
# Test Redis
docker exec botv2-redis redis-cli -a <password> ping

# Connect to Redis
docker exec -it botv2-redis redis-cli -a <password>
```

### Dashboard not loading:
```bash
# Check if port 8050 is open
curl http://localhost:8050

# Check dashboard logs
docker compose logs botv2-dashboard --tail=100

# Restart dashboard
docker compose restart botv2-dashboard
```

---

## 🔧 Maintenance Scripts

### Backup database:
```bash
# Create backup
docker exec botv2-postgres pg_dump -U botv2_user botv2_user > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore database:
```bash
# Restore from backup
docker exec -i botv2-postgres psql -U botv2_user -d botv2_user < backup_20260121_040000.sql
```

### Clean up:
```bash
# Remove stopped containers
docker compose down

# Remove volumes (CAUTION: deletes data!)
docker compose down -v

# Rebuild everything
docker compose up -d --build --force-recreate
```

---

## ❓ FAQ

### Q: Why is there no API check?
**A:** The trading bot (`botv2-app`) is an async process, not an HTTP server. It doesn't expose a REST API. The dashboard connects directly to PostgreSQL.

### Q: How do I check if trading bot is working?
**A:** 
```bash
# View recent logs
docker compose logs botv2-app --tail=50

# Look for "iteration" or "trade executed"
docker compose logs botv2-app | grep -i "iteration\|trade"
```

### Q: What if verify_system.sh shows warnings?
**A:** Yellow warnings (⚠) are usually temporary. Wait 30 seconds and run again. Red errors (✗) require investigation via logs.

---

**Last Updated:** January 21, 2026  
**Maintained by:** BotV2 Team
