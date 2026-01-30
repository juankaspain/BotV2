#!/bin/bash

# ====================================
# BotV2 Startup Script
# ====================================
# Professional startup script with:
# - Development environment auto-configuration
# - Virtual environment detection
# - Clean console output
# - Error handling

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ====================================
# FORCE DEVELOPMENT ENVIRONMENT
# ====================================
# Auto-configure for local development
export ENVIRONMENT="development"
export FLASK_ENV="development"
export FLASK_DEBUG="1"
export FORCE_HTTPS="false"
export TRADING_MODE="paper"

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}🤖 BotV2 Trading System${NC}"
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}✓ Environment: ${ENVIRONMENT}${NC}"
echo -e "${GREEN}✓ Flask mode: ${FLASK_ENV}${NC}"
echo -e "${GREEN}✓ HTTPS: ${FORCE_HTTPS}${NC}"
echo -e "${GREEN}✓ Trading: ${TRADING_MODE}${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Check if virtual environment is activated
if [[ -z "${VIRTUAL_ENV}" ]]; then
    echo -e "${YELLOW}⚠️  No virtual environment detected${NC}"
    
    # Try to activate if exists
    if [ -d "venv" ]; then
        echo -e "${BLUE}Activating venv...${NC}"
        source venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    elif [ -d ".venv" ]; then
        echo -e "${BLUE}Activating .venv...${NC}"
        source .venv/bin/activate
        echo -e "${GREEN}✓ Virtual environment activated${NC}"
    else
        echo -e "${RED}❌ No virtual environment found!${NC}"
        echo -e "${YELLOW}Please create one with: python -m venv venv${NC}"
        exit 1
    fi
    echo ""
else
    echo -e "${GREEN}✓ Virtual environment active: ${VIRTUAL_ENV}${NC}"
    echo ""
fi

# Verify Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${BLUE}Python version: ${PYTHON_VERSION}${NC}"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ main.py not found!${NC}"
    echo -e "${YELLOW}Please run from project root directory${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project structure verified${NC}"
echo ""

# Start the bot
echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}🚀 Starting BotV2...${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Execute main.py
python main.py

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ BotV2 stopped cleanly${NC}"
else
    echo -e "${RED}❌ BotV2 stopped with error code: ${EXIT_CODE}${NC}"
fi

exit $EXIT_CODE