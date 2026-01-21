#!/bin/bash

################################################################################
# BotV2 System Verification Script
# 
# Verifies all services are running correctly:
# - PostgreSQL (database)
# - Redis (cache)
# - Trading Bot (async process)
# - Dashboard (web interface)
#
# NOTE: There is NO REST API on port 8000 - this is correct!
#       The trading bot is an async process, not an HTTP server.
#
# Usage:
#   chmod +x scripts/verify_system.sh
#   ./scripts/verify_system.sh
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Header
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  🔍 BotV2 System Verification"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Exit code tracker
ALL_OK=0

################################################################################
# 1. Check Docker Compose is running
################################################################################
echo -e "${BLUE}→ Checking Docker Compose...${NC}"
if ! docker compose ps > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker Compose not running or not installed${NC}"
    echo "  Run: docker compose up -d"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose is running${NC}"
echo ""

################################################################################
# 2. PostgreSQL
################################################################################
echo -e "${BLUE}→ Checking PostgreSQL...${NC}"
if docker exec botv2-postgres pg_isready -U botv2_user > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PostgreSQL is healthy and accepting connections${NC}"
    
    # Try to query database
    if docker exec botv2-postgres psql -U botv2_user -d botv2_user -c "SELECT version();" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Database queries working${NC}"
    else
        echo -e "${YELLOW}⚠ Database exists but queries failing${NC}"
        ALL_OK=1
    fi
else
    echo -e "${RED}✗ PostgreSQL not responding${NC}"
    echo "  Check logs: docker compose logs botv2-postgres"
    ALL_OK=1
fi
echo ""

################################################################################
# 3. Redis
################################################################################
echo -e "${BLUE}→ Checking Redis...${NC}"
REDIS_PASSWORD=$(grep REDIS_PASSWORD .env 2>/dev/null | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "")

if [ -z "$REDIS_PASSWORD" ]; then
    # No password
    if docker exec botv2-redis redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is healthy (no password)${NC}"
    else
        echo -e "${RED}✗ Redis not responding${NC}"
        ALL_OK=1
    fi
else
    # With password
    if docker exec botv2-redis redis-cli -a "$REDIS_PASSWORD" --no-auth-warning ping > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Redis is healthy (authenticated)${NC}"
    else
        echo -e "${RED}✗ Redis not responding${NC}"
        ALL_OK=1
    fi
fi
echo ""

################################################################################
# 4. Trading Bot (Process Check - NO HTTP)
################################################################################
echo -e "${BLUE}→ Checking Trading Bot...${NC}"

# Check container is running
if docker compose ps botv2-app | grep -q "Up"; then
    echo -e "${GREEN}✓ Trading Bot container is running${NC}"
    
    # Check for recent activity in logs
    RECENT_LOGS=$(docker compose logs botv2-app --tail=50 2>/dev/null || echo "")
    
    if echo "$RECENT_LOGS" | grep -qi "initialization\|initializing\|initialized\|running\|loop\|iteration"; then
        echo -e "${GREEN}✓ Trading Bot is active (check logs for details)${NC}"
    else
        echo -e "${YELLOW}⚠ Trading Bot may not be running properly${NC}"
        echo "  Check logs: docker compose logs botv2-app --tail=50"
        ALL_OK=1
    fi
    
    # Check for errors
    if echo "$RECENT_LOGS" | grep -qi "error\|critical\|exception" | head -1; then
        echo -e "${YELLOW}⚠ Recent errors detected in logs${NC}"
        echo "  Run: docker compose logs botv2-app | grep -i error"
    fi
else
    echo -e "${RED}✗ Trading Bot container not running${NC}"
    echo "  Check logs: docker compose logs botv2-app"
    ALL_OK=1
fi
echo ""

################################################################################
# 5. Dashboard (HTTP Server)
################################################################################
echo -e "${BLUE}→ Checking Dashboard...${NC}"

# Check container is running
if docker compose ps botv2-dashboard | grep -q "Up"; then
    echo -e "${GREEN}✓ Dashboard container is running${NC}"
    
    # Check HTTP endpoint
    if curl -s -f http://localhost:8050 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Dashboard HTTP server responding on port 8050${NC}"
        echo -e "${GREEN}✓ Access at: http://localhost:8050${NC}"
    else
        echo -e "${YELLOW}⚠ Dashboard not responding yet (may still be starting)${NC}"
        echo "  Wait 30 seconds and try: curl http://localhost:8050"
        echo "  Check logs: docker compose logs botv2-dashboard"
        ALL_OK=1
    fi
else
    echo -e "${RED}✗ Dashboard container not running${NC}"
    echo "  Check logs: docker compose logs botv2-dashboard"
    ALL_OK=1
fi
echo ""

################################################################################
# Summary
################################################################################
echo "═══════════════════════════════════════════════════════════════════"
if [ $ALL_OK -eq 0 ]; then
    echo -e "  ${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
else
    echo -e "  ${YELLOW}⚠️  SOME ISSUES DETECTED${NC}"
    echo "  Check logs above for details"
fi
echo "═══════════════════════════════════════════════════════════════════"
echo ""

################################################################################
# Container Status Table
################################################################################
echo -e "${BLUE}📊 Container Status:${NC}"
echo ""
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
echo ""

################################################################################
# Access Information
################################################################################
echo "═══════════════════════════════════════════════════════════════════"
echo -e "  ${BLUE}🌐 Access Information${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Dashboard:       http://localhost:8050"
echo "  Username:      admin"
echo "  Password:      admin (or check DASHBOARD_PASSWORD in .env)"
echo ""
echo "PostgreSQL:      localhost:5432"
echo "  Database:      botv2_user"
echo "  Username:      botv2_user"
echo "  Connect:       docker exec -it botv2-postgres psql -U botv2_user -d botv2_user"
echo ""
echo "Redis:           localhost:6379"
echo "  Connect:       docker exec -it botv2-redis redis-cli -a <password>"
echo ""
echo "Trading Bot:     (background process, no HTTP endpoint)"
echo "  View logs:     docker compose logs -f botv2-app"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""

################################################################################
# Quick Commands
################################################################################
echo -e "${BLUE}📋 Useful Commands:${NC}"
echo ""
echo "  View all logs:           docker compose logs -f"
echo "  View bot logs:           docker compose logs -f botv2-app"
echo "  View dashboard logs:     docker compose logs -f botv2-dashboard"
echo "  Restart all:             docker compose restart"
echo "  Stop all:                docker compose down"
echo "  Rebuild and start:       docker compose up -d --build"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Exit with appropriate code
exit $ALL_OK
