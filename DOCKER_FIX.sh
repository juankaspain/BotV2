#!/bin/bash
# BotV2 Docker Fix Script - Enhanced
# Resuelve errores de Docker y pip installation
# Uso: bash DOCKER_FIX.sh

set -e

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║         BotV2 Docker Fix - Advanced Edition                 ║"
echo "║         Resolviendo problemas de pip + numpy               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if docker-compose exists
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗${NC} docker-compose no está instalado"
    exit 1
fi

# Step 0: Pre-flight checks
echo -e "${BLUE}[0/4]${NC} Verificaciones previas..."
echo "Verificando Docker daemon..."
if ! docker ps &> /dev/null; then
    echo -e "${RED}✗${NC} Docker daemon no está corriendo"
    echo "Inicia Docker e intenta de nuevo"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker daemon activo"
echo ""

# Step 1: Clean Docker system
echo -e "${YELLOW}[1/5]${NC} Limpiando Docker cache..."
echo "Removiendo imagenes, containers y volúmenes no usados..."
if ! docker system prune -a --volumes -f > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠${NC} Advertencia: Algunos items no pudieron ser removidos (normal)"
else
    echo -e "${GREEN}✓${NC} Docker system limpio"
fi
echo ""

# Step 2: Rebuild images with progress
echo -e "${YELLOW}[2/5]${NC} Rebuilding Docker images sin cache..."
echo "Esto puede tomar 3-5 minutos la primera vez..."
echo "Mostrando progreso de build..."
echo ""

if docker-compose build --no-cache 2>&1 | grep -E "(Successfully|ERROR|failed)"; then
    BUILD_RESULT=$?
    if [ $BUILD_RESULT -eq 0 ] || grep -q "Successfully" <<< "${BUILD_OUTPUT}"; then
        echo -e "${GREEN}✓${NC} Imagenes rebuildeadas exitosamente"
    else
        echo -e "${RED}✗${NC} Error durante el build"
        echo ""
        echo "DEBUG: Intenta esto para más información:"
        echo "  docker-compose build --progress=plain --no-cache 2>&1 | tail -100"
        echo ""
        echo "O build manual:"
        echo "  docker build --progress=plain --no-cache -t botv2:debug ."
        exit 1
    fi
else
    echo -e "${RED}✗${NC} Error durante el build"
    echo "Usa: docker-compose build --progress=plain"
    exit 1
fi
echo ""

# Step 3: Start services
echo -e "${YELLOW}[3/5]${NC} Iniciando servicios Docker..."
if docker-compose up -d 2>&1 | grep -E "(Created|Started|Pulled)"; then
    echo -e "${GREEN}✓${NC} Servicios iniciados"
else
    echo -e "${RED}✗${NC} Error iniciando servicios"
    echo "Ver logs: docker-compose logs"
    exit 1
fi
echo ""

# Step 4: Wait and verify
echo -e "${YELLOW}[4/5]${NC} Esperando inicialización de servicios..."
echo "Esto puede tomar hasta 30 segundos..."
sleep 10

echo "Estado de containers:"
echo ""
docker-compose ps
echo ""

# Step 5: Detailed verification
echo -e "${YELLOW}[5/5]${NC} Verificación exhaustiva de paquetes Python..."
echo ""

VERIFY_SUCCESS=true

# Test each package individually
echo -e "${BLUE}Testing packages:${NC}"

for package in "flask" "dash" "pandas" "numpy" "psycopg2" "redis" "requests" "websockets"; do
    if docker-compose exec -T botv2 python -c "import $package; print('OK')" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} $package - OK"
    else
        echo -e "  ${RED}✗${NC} $package - FALLO"
        VERIFY_SUCCESS=false
    fi
done

echo ""

if [ "$VERIFY_SUCCESS" = true ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              🎉 ¡PROBLEMA RESUELTO! 🎉                           ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Los servicios están corriendo:"
    echo -e "${GREEN}✓${NC} BotV2 API - http://localhost:8000"
    echo -e "${GREEN}✓${NC} Dashboard - http://localhost:8050"
    echo -e "${GREEN}✓${NC} PostgreSQL - localhost:5432"
    echo -e "${GREEN}✓${NC} Redis - localhost:6379"
    echo ""
    echo "Comandos útiles:"
    echo "  Ver logs:     docker-compose logs -f botv2"
    echo "  Entrar shell: docker-compose exec botv2 /bin/sh"
    echo "  Detener:      docker-compose down"
    echo "  Limpiar vol:  docker-compose down -v"
    echo ""
else
    echo -e "${YELLOW}⚠${NC}  Algunos paquetes fallaron"
    echo ""
    echo "Troubleshooting:"
    echo "1. Ver logs completos:"
    echo "   docker-compose logs -f botv2 | tail -50"
    echo ""
    echo "2. Test manual de numpy:"
    echo "   docker-compose exec botv2 python"
    echo "   >>> import numpy"
    echo "   >>> print(numpy.__version__)"
    echo ""
    echo "3. Ver paquetes instalados:"
    echo "   docker-compose exec botv2 pip list | grep -i numpy"
    echo ""
    echo "4. Rebuild completo (desde cero):"
    echo "   docker-compose down -v"
    echo "   docker system prune -a --volumes"
    echo "   bash DOCKER_FIX.sh"
    echo ""
    echo "5. Build con salida detallada:"
    echo "   docker build --progress=plain --no-cache -t botv2:test . 2>&1 | tee build.log"
    echo ""
    exit 1
fi
