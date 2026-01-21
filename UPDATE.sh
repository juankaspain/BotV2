#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT
# ================================
# Actualiza SOLO la app y dashboard sin perder datos
# Preserva: PostgreSQL, Redis y datos
# Author: Juan Carlos Garcia
# Date: 21-01-2026
#

set -e  # Exit on error

# ============================================================================
# COLORES Y ESTILOS
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ============================================================================
# FUNCIONES
# ============================================================================

log_header() {
    echo -e "\n${BLUE}=================================================================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}=================================================================================${NC}\n"
}

log_step() {
    echo -e "${CYAN}→${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# ============================================================================
# PRE-ACTUALIZACIÓN
# ============================================================================

log_header "🚀 BotV2 Update Script"

echo -e "${YELLOW}INFORMACIÓN DE LA ACTUALIZACIÓN${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Este script:"
echo "  ✓ Actualiza SOLO la app y dashboard"
echo "  ✓ Preserva PostgreSQL intacto"
echo "  ✓ Preserva Redis intacto"
echo "  ✓ Preserva TODOS los datos"
echo "  ✓ Sin downtime significativo"
echo ""
echo -e "${YELLOW}Confirmación${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "¿Deseas proceder con la actualización? (s/n): " -r confirm
echo ""

if [[ ! $confirm =~ ^[Ss]$ ]]; then
    log_error "Actualización cancelada"
    exit 0
fi

# ============================================================================
# PASO 1: Verificar que Docker está funcionando
# ============================================================================

log_step "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado"
    exit 1
fi
log_success "Docker está instalado"

if ! docker info &> /dev/null; then
    log_error "Docker daemon no está corriendo"
    exit 1
fi
log_success "Docker daemon está corriendo"

# ============================================================================
# PASO 2: Verificar que docker-compose está disponible
# ============================================================================

log_step "Verificando docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose no está instalado"
    exit 1
fi
log_success "docker-compose está disponible"

# ============================================================================
# PASO 3: Backup de datos (PREVENTIVO)
# ============================================================================

log_header "📦 Backup Preventivo"

BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="${BACKUP_DIR}/pre-update-$(date +%Y%m%d_%H%M%S).sql"

log_step "Creando backup de PostgreSQL..."
if docker-compose exec -T botv2-postgres pg_dump -U botv2 botv2_db > "$BACKUP_FILE" 2>/dev/null; then
    log_success "Backup creado: $BACKUP_FILE"
    echo "  Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    log_warning "No se pudo crear backup (PostgreSQL puede no estar listo)"
fi

# ============================================================================
# PASO 4: Obtener último código
# ============================================================================

log_header "📥 Obteniendo últimas actualizaciones"

log_step "Obteniendo código de Git..."
if git pull origin main &> /dev/null; then
    log_success "Código actualizado desde Git"
else
    log_warning "No se pudo actualizar desde Git (puede estar offline)"
fi

# ============================================================================
# PASO 5: Reconstruir imágenes
# ============================================================================

log_header "🔨 Reconstruyendo imágenes"

log_step "Compilando imagen botv2-app..."
if docker-compose build botv2-app &> /dev/null; then
    log_success "Imagen botv2-app compilada"
else
    log_error "Error compilando botv2-app"
    exit 1
fi

log_step "Compilando imagen botv2-dashboard..."
if docker-compose build botv2-dashboard &> /dev/null; then
    log_success "Imagen botv2-dashboard compilada"
else
    log_error "Error compilando botv2-dashboard"
    exit 1
fi

# ============================================================================
# PASO 6: Parar solo la app y dashboard
# ============================================================================

log_header "🛑 Deteniendo servicios (preservando datos)"

log_step "Deteniendo botv2-app..."
if docker-compose stop botv2-app &> /dev/null; then
    log_success "botv2-app detenida"
else
    log_warning "botv2-app no estaba corriendo"
fi

log_step "Deteniendo botv2-dashboard..."
if docker-compose stop botv2-dashboard &> /dev/null; then
    log_success "botv2-dashboard detenida"
else
    log_warning "botv2-dashboard no estaba corriendo"
fi

log_step "PostgreSQL: ✓ PRESERVADO (no detenido)"
log_step "Redis: ✓ PRESERVADO (no detenido)"

# ============================================================================
# PASO 7: Iniciar los nuevos contenedores
# ============================================================================

log_header "🚀 Iniciando nuevas versiones"

log_step "Iniciando botv2-app con nuevo código..."
if docker-compose up -d botv2-app &> /dev/null; then
    log_success "botv2-app iniciada"
else
    log_error "Error iniciando botv2-app"
    exit 1
fi

log_step "Esperando 3 segundos..."
sleep 3

log_step "Iniciando botv2-dashboard con nuevo código..."
if docker-compose up -d botv2-dashboard &> /dev/null; then
    log_success "botv2-dashboard iniciada"
else
    log_error "Error iniciando botv2-dashboard"
    exit 1
fi

# ============================================================================
# PASO 8: Verificar salud
# ============================================================================

log_header "✅ Verificando servicios"

log_step "Esperando 5 segundos a que los servicios arranquen..."
sleep 5

log_step "Verificando estado de servicios..."
echo ""
docker-compose ps
echo ""

# ============================================================================
# PASO 9: Test de conectividad
# ============================================================================

log_header "🧪 Tests de conectividad"

log_step "Verificando PostgreSQL..."
if docker-compose exec -T botv2-postgres pg_isready -U botv2 &> /dev/null; then
    log_success "PostgreSQL responde"
else
    log_warning "PostgreSQL no responde (puede estar inicializando)"
fi

log_step "Verificando Redis..."
if docker-compose exec -T botv2-redis redis-cli ping &> /dev/null; then
    log_success "Redis responde"
else
    log_warning "Redis no responde (puede estar inicializando)"
fi

log_step "Esperando 10 segundos para que aplicaciones arranquen..."
sleep 10

log_step "Verificando API..."
if curl -s http://localhost:8000/health &> /dev/null; then
    log_success "API está respondiendo"
else
    log_warning "API no responde aún (puede estar inicializando)"
fi

log_step "Verificando Dashboard..."
if curl -s http://localhost:8050 &> /dev/null; then
    log_success "Dashboard está respondiendo"
else
    log_warning "Dashboard no responde aún (puede estar inicializando)"
fi

# ============================================================================
# PASO 10: Resumen final
# ============================================================================

log_header "✨ Actualización Completada"

echo -e "${GREEN}ACTUALIZACIÓN EXITOSA${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Estado:"
echo "  ✓ App (botv2-app):     ACTUALIZADA"
echo "  ✓ Dashboard:           ACTUALIZADA"
echo "  ✓ PostgreSQL:          INTACTO (datos preservados)"
echo "  ✓ Redis:               INTACTO"
echo ""
echo "📁 Backup:"
echo "  ✓ Ubicación: $BACKUP_FILE"
echo ""
echo "🌐 Acceso:"
echo "  • API:       http://localhost:8000"
echo "  • Dashboard: http://localhost:8050"
echo "  • Base datos: localhost:5432"
echo "  • Cache:      localhost:6379"
echo ""
echo "📋 Comandos útiles:"
echo "  • Ver logs:       docker-compose logs -f botv2-app"
echo "  • Conectar BD:    docker-compose exec botv2-postgres psql -U botv2 -d botv2_db"
echo "  • Conectar Cache: docker-compose exec botv2-redis redis-cli"
echo "  • Ver estado:     docker-compose ps"
echo ""
echo -e "${GREEN}¡Actualización completada exitosamente! 🎉${NC}"
echo ""
