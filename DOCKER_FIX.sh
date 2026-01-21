#!/bin/bash
# BotV2 Docker Fix Script
# Resuelve el error: "pip install failed with exit code 1"
# Uso: bash DOCKER_FIX.sh

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║         BotV2 Docker Fix - pip Installation Error               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Clean Docker system
echo -e "${YELLOW}[1/4]${NC} Limpiando Docker cache..."
echo "Removiendo imagenes, containers y volúmenes no usados..."
docker system prune -a --volumes -f > /dev/null 2>&1
echo -e "${GREEN}✓${NC} Docker system limpio"
echo ""

# Step 2: Rebuild images
echo -e "${YELLOW}[2/4]${NC} Rebuilding Docker images sin cache..."
echo "Esto puede tomar 3-5 minutos la primera vez..."
if docker-compose build --no-cache; then
    echo -e "${GREEN}✓${NC} Imagenes rebuildeadas exitosamente"
else
    echo -e "${RED}✗${NC} Error durante el build"
    echo "Ejecuta: docker-compose build --progress=plain"
    exit 1
fi
echo ""

# Step 3: Start services
echo -e "${YELLOW}[3/4]${NC} Iniciando servicios Docker..."
if docker-compose up -d; then
    echo -e "${GREEN}✓${NC} Servicios iniciados"
else
    echo -e "${RED}✗${NC} Error iniciando servicios"
    exit 1
fi
echo ""

# Step 4: Verify
echo -e "${YELLOW}[4/4]${NC} Verificando instalación..."
echo ""
echo "Estado de containers:"
docker-compose ps
echo ""

# Check if botv2 container is healthy
echo "Esperando health check (30 segundos)..."
sleep 5

if docker-compose exec -T botv2 python -c "import numpy, pandas, flask, dash; print('OK')" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Todos los paquetes importados correctamente"
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              🎉 ¡PROBLEMA RESUELTO! 🎉                           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Los servicios están corriendo correctamente:"
    echo -e "${GREEN}✓${NC} BotV2 - http://localhost:8000 (API)"
    echo -e "${GREEN}✓${NC} Dashboard - http://localhost:8050 (Web UI)"
    echo -e "${GREEN}✓${NC} PostgreSQL - localhost:5432 (Database)"
    echo -e "${GREEN}✓${NC} Redis - localhost:6379 (Cache)"
    echo ""
    echo "Ver logs:"
    echo "  docker-compose logs -f botv2"
    echo ""
    echo "Detener servicios:"
    echo "  docker-compose down"
    echo ""
else
    echo -e "${YELLOW}⚠${NC}  Health check en progreso..."
    echo "Esperando 20 segundos más..."
    sleep 20
    
    if docker-compose exec -T botv2 python -c "import numpy, pandas, flask, dash; print('OK')" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Sistema listo"
    else
        echo -e "${RED}✗${NC} Error verificando paquetes"
        echo ""
        echo "Troubleshooting:"
        echo "1. Ver logs detallados:"
        echo "   docker-compose logs -f botv2"
        echo ""
        echo "2. Entrar al contenedor:"
        echo "   docker-compose exec botv2 /bin/sh"
        echo ""
        echo "3. Test manual de paquetes:"
        echo "   docker-compose run --rm botv2 python -c 'import numpy; print(numpy.__version__)'"
        echo ""
        exit 1
    fi
fi
