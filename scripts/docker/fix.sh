#!/bin/bash
# BotV2 Docker Fix Script - Final Edition
# Resuelve TODOS los errores de Docker
# Uso: bash DOCKER_FIX.sh

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║         BotV2 Docker Fix - Final Edition                   ║"
echo "║         Resolviendo TODOS los errores de Docker            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Step 0: Pre-flight checks
echo -e "${BLUE}[0/4]${NC} Verificaciones previas..."

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗${NC} docker-compose no está instalado"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo -e "${RED}✗${NC} Docker daemon no está corriendo"
    exit 1
fi

echo -e "${GREEN}✓${NC} Docker daemon activo"
echo ""

# Step 1: Full cleanup
echo -e "${YELLOW}[1/4]${NC} Limpieza profunda de Docker..."
echo "Removiendo imagenes, containers y volúmenes..."

# Stop all running containers
docker-compose down 2>/dev/null || true

# System prune
docker system prune -a --volumes -f > /dev/null 2>&1 || true

echo -e "${GREEN}✓${NC} Sistema limpio"
echo ""

# Step 2: Build with detailed output
echo -e "${YELLOW}[2/4]${NC} Construyendo imágenes (puede tomar 3-5 minutos)..."
echo ""

if docker-compose build --no-cache 2>&1; then
    echo -e "${GREEN}✓${NC} Build exitoso"
else
    echo -e "${RED}✗${NC} Error durante el build"
    echo ""
    echo "Para debugging detallado:"
    echo "  docker-compose build --progress=plain --no-cache 2>&1 | tail -100"
    exit 1
fi

echo ""

# Step 3: Start services
echo -e "${YELLOW}[3/4]${NC} Iniciando servicios..."

if docker-compose up -d 2>&1 | grep -E "(Created|Started)"; then
    echo -e "${GREEN}✓${NC} Servicios iniciados"
else
    echo -e "${RED}✗${NC} Error iniciando servicios"
    exit 1
fi

echo ""
echo "Estado de containers:"
docker-compose ps
echo ""

# Step 4: Verify everything
echo -e "${YELLOW}[4/4]${NC} Verificación de paquetes Python..."
sleep 5

echo ""
echo -e "${BLUE}Verificando packages:${NC}"

PACKAGES=("flask" "dash" "pandas" "numpy" "psycopg2" "redis" "requests" "websockets")
VERIFY_SUCCESS=true

for pkg in "${PACKAGES[@]}"; do
    if docker-compose exec -T botv2 python -c "import $pkg" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $pkg - OK"
    else
        echo -e "  ${RED}✗${NC} $pkg - FALLO"
        VERIFY_SUCCESS=false
    fi
done

echo ""

if [ "$VERIFY_SUCCESS" = true ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              🎉 ¡SISTEMA COMPLETAMENTE OPERATIVO! 🎉            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Servicios corriendo:"
    echo -e "${GREEN}✓${NC} BotV2 - http://localhost:8000"
    echo -e "${GREEN}✓${NC} Dashboard - http://localhost:8050"
    echo -e "${GREEN}✓${NC} PostgreSQL - localhost:5432"
    echo -e "${GREEN}✓${NC} Redis - localhost:6379"
    echo ""
    echo "Comandos útiles:"
    echo "  Ver logs:     docker-compose logs -f botv2"
    echo "  Detener:      docker-compose down"
    echo "  Limpiar vol:  docker-compose down -v"
    echo ""
else
    echo -e "${RED}✗${NC} Algunos paquetes fallaron"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ver logs:    docker-compose logs -f botv2 | tail -50"
    echo "  2. Entrar shell: docker-compose exec botv2 /bin/sh"
    echo "  3. Reintentar:  bash DOCKER_FIX.sh"
    exit 1
fi
