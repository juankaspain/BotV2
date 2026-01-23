#!/bin/bash
# Dashboard Cleanup Script
# Removes obsolete files after refactoring
# Run from project root: bash src/dashboard/CLEANUP_SCRIPT.sh

set -e  # Exit on error

echo "========================================"
echo "  BotV2 Dashboard Cleanup Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check we're in project root
if [ ! -d "src/dashboard" ]; then
    echo -e "${RED}Error: Must run from project root${NC}"
    echo "Usage: bash src/dashboard/CLEANUP_SCRIPT.sh"
    exit 1
fi

echo -e "${YELLOW}This script will remove the following obsolete files:${NC}"
echo ""
echo "  1. src/dashboard/api.py (21.8 KB)"
echo "     - Duplicate Flask instance"
echo "     - All endpoints moved to web_app.py"
echo ""
echo "  2. src/dashboard/dashboard_standalone.py (11.2 KB)"
echo "     - Old standalone version"
echo "     - Replaced by web_app.py"
echo ""
echo "  3. src/dashboard/web_app_control_integration.py (416 bytes)"
echo "     - Temporary integration patch"
echo "     - Already integrated"
echo ""

# Ask for confirmation
read -p "Create backup before deletion? (recommended) [Y/n]: " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo -e "${GREEN}Creating backup...${NC}"
    mkdir -p backups/dashboard_$(date +%Y%m%d_%H%M%S)
    
    if [ -f "src/dashboard/api.py" ]; then
        cp src/dashboard/api.py backups/dashboard_$(date +%Y%m%d_%H%M%S)/
        echo "  ✓ Backed up api.py"
    fi
    
    if [ -f "src/dashboard/dashboard_standalone.py" ]; then
        cp src/dashboard/dashboard_standalone.py backups/dashboard_$(date +%Y%m%d_%H%M%S)/
        echo "  ✓ Backed up dashboard_standalone.py"
    fi
    
    if [ -f "src/dashboard/web_app_control_integration.py" ]; then
        cp src/dashboard/web_app_control_integration.py backups/dashboard_$(date +%Y%m%d_%H%M%S)/
        echo "  ✓ Backed up web_app_control_integration.py"
    fi
    
    echo -e "${GREEN}Backup complete!${NC}"
    echo ""
fi

read -p "Proceed with deletion? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Removing files...${NC}"
    
    # Remove api.py
    if [ -f "src/dashboard/api.py" ]; then
        rm src/dashboard/api.py
        echo -e "  ${GREEN}✓${NC} Removed api.py"
    else
        echo -e "  ${YELLOW}•${NC} api.py already removed"
    fi
    
    # Remove dashboard_standalone.py
    if [ -f "src/dashboard/dashboard_standalone.py" ]; then
        rm src/dashboard/dashboard_standalone.py
        echo -e "  ${GREEN}✓${NC} Removed dashboard_standalone.py"
    else
        echo -e "  ${YELLOW}•${NC} dashboard_standalone.py already removed"
    fi
    
    # Remove web_app_control_integration.py
    if [ -f "src/dashboard/web_app_control_integration.py" ]; then
        rm src/dashboard/web_app_control_integration.py
        echo -e "  ${GREEN}✓${NC} Removed web_app_control_integration.py"
    else
        echo -e "  ${YELLOW}•${NC} web_app_control_integration.py already removed"
    fi
    
    echo ""
    echo -e "${GREEN}Cleanup complete!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "  1. Review REFACTORING_SUMMARY.md for integration requirements"
    echo "  2. Test dashboard: python -m src.dashboard.web_app"
    echo "  3. Commit changes: git add -A && git commit -m 'refactor: Complete dashboard cleanup'"
    echo ""
else
    echo -e "${YELLOW}Cleanup cancelled${NC}"
    exit 0
fi

echo "========================================"
echo "  Cleanup Script Complete"
echo "========================================"
