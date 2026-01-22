#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT
# ================================
# Actualiza SOLO la app y dashboard sin perder datos
# Preserva: PostgreSQL, Redis y datos
# Soporta: Modo Demo y Modo Producción
# Author: Juan Carlos Garcia
# Date: 22-01-2026
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

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Función para verificar si un servicio está activo
service_is_active() {
    local service=$1
    # Verifica si el servicio está corriendo
    if docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^${service}$"; then
        return 0
    fi
    # Verifica si el servicio está definido (aunque no esté corriendo)
    if docker-compose config --services 2>/dev/null | grep -q "^${service}$"; then
        return 0
    fi
    return 1
}

# ============================================================================
# PRE-ACTUALIZACIÓN
# ============================================================================

log_header "🚀 BotV2 Update Script"

echo -e "${YELLOW}INFORMACIÓN DE LA ACTUALIZACIÓN${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Este script:"
echo "  ✓ Actualiza servicios activos"
echo "  ✓ Preserva PostgreSQL intacto (si existe)"
echo "  ✓ Preserva Redis intacto (si existe)"
echo "  ✓ Preserva TODOS los datos"
echo "  ✓ Detecta modo Demo/Producción automáticamente"
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
# PASO 2.5: Detectar servicios activos
# ============================================================================

log_header "🔍 Detectando configuración"

log_step "Analizando servicios definidos..."

# Detectar servicios
HAS_APP=false
HAS_DASHBOARD=false
HAS_POSTGRES=false
HAS_REDIS=false

if service_is_active "botv2-app"; then
    HAS_APP=true
    log_info "Trading Bot (botv2-app): ACTIVO"
else
    log_warning "Trading Bot (botv2-app): NO ACTIVO (comentado o no definido)"
fi

if service_is_active "botv2-dashboard"; then
    HAS_DASHBOARD=true
    log_info "Dashboard (botv2-dashboard): ACTIVO"
else
    log_warning "Dashboard (botv2-dashboard): NO ACTIVO"
fi

if service_is_active "botv2-postgres"; then
    HAS_POSTGRES=true
    log_info "PostgreSQL (botv2-postgres): ACTIVO"
else
    log_warning "PostgreSQL (botv2-postgres): NO ACTIVO (modo demo sin base de datos)"
fi

if service_is_active "botv2-redis"; then
    HAS_REDIS=true
    log_info "Redis (botv2-redis): ACTIVO"
else
    log_warning "Redis (botv2-redis): NO ACTIVO"
fi

echo ""
if [ "$HAS_DASHBOARD" = true ] && [ "$HAS_APP" = false ] && [ "$HAS_POSTGRES" = false ]; then
    log_info "🎯 Modo detectado: DEMO (Dashboard standalone con datos demo)"
    MODE="demo"
else
    log_info "🎯 Modo detectado: PRODUCCIÓN (Con base de datos y/o trading bot)"
    MODE="production"
fi

# ============================================================================
# PASO 3: Backup de datos (PREVENTIVO) - Solo si hay PostgreSQL
# ============================================================================

if [ "$HAS_POSTGRES" = true ]; then
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
else
    log_info "📦 Backup omitido: No hay PostgreSQL activo (modo demo)"
fi

# ============================================================================
# PASO 4: Obtener último código
# ============================================================================

log_header "📥 Obteniendo últimas actualizaciones"

log_step "Obteniendo código de Git..."
if git pull origin main &> /dev/null; then
    log_success "Código actualizado desde Git"
else
    log_warning "No se pudo actualizar desde Git (puede estar offline o sin cambios)"
fi

# ============================================================================
# PASO 5: Reconstruir imágenes - SOLO servicios activos
# ============================================================================

log_header "🔨 Reconstruyendo imágenes"

BUILD_ERRORS=false

if [ "$HAS_APP" = true ]; then
    log_step "Compilando imagen botv2-app..."
    if docker-compose build botv2-app 2>&1 | grep -q "service.*not found\|no such service"; then
        log_warning "Servicio botv2-app no encontrado en docker-compose.yml (omitiendo)"
        HAS_APP=false
    elif docker-compose build botv2-app &> /dev/null; then
        log_success "Imagen botv2-app compilada"
    else
        log_error "Error compilando botv2-app"
        BUILD_ERRORS=true
    fi
else
    log_info "Omitiendo botv2-app (no activo)"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Compilando imagen botv2-dashboard..."
    if docker-compose build botv2-dashboard 2>&1 | grep -q "service.*not found\|no such service"; then
        log_error "Servicio botv2-dashboard no encontrado en docker-compose.yml"
        exit 1
    elif docker-compose build botv2-dashboard &> /dev/null; then
        log_success "Imagen botv2-dashboard compilada"
    else
        log_error "Error compilando botv2-dashboard"
        BUILD_ERRORS=true
    fi
else
    log_error "Dashboard no está activo - no se puede actualizar"
    exit 1
fi

if [ "$BUILD_ERRORS" = true ]; then
    log_error "Errores durante la compilación - abortando"
    exit 1
fi

# ============================================================================
# PASO 6: Parar solo servicios activos
# ============================================================================

log_header "🛑 Deteniendo servicios (preservando datos)"

if [ "$HAS_APP" = true ]; then
    log_step "Deteniendo botv2-app..."
    if docker-compose stop botv2-app &> /dev/null; then
        log_success "botv2-app detenida"
    else
        log_warning "botv2-app no estaba corriendo"
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Deteniendo botv2-dashboard..."
    if docker-compose stop botv2-dashboard &> /dev/null; then
        log_success "botv2-dashboard detenida"
    else
        log_warning "botv2-dashboard no estaba corriendo"
    fi
fi

if [ "$HAS_POSTGRES" = true ]; then
    log_step "PostgreSQL: ✓ PRESERVADO (no detenido)"
fi

if [ "$HAS_REDIS" = true ]; then
    log_step "Redis: ✓ PRESERVADO (no detenido)"
fi

# ============================================================================
# PASO 7: Iniciar los nuevos contenedores
# ============================================================================

log_header "🚀 Iniciando nuevas versiones"

if [ "$HAS_APP" = true ]; then
    log_step "Iniciando botv2-app con nuevo código..."
    if docker-compose up -d botv2-app &> /dev/null; then
        log_success "botv2-app iniciada"
    else
        log_error "Error iniciando botv2-app"
        exit 1
    fi
    
    log_step "Esperando 3 segundos..."
    sleep 3
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Iniciando botv2-dashboard con nuevo código..."
    if docker-compose up -d botv2-dashboard &> /dev/null; then
        log_success "botv2-dashboard iniciada"
    else
        log_error "Error iniciando botv2-dashboard"
        exit 1
    fi
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

if [ "$HAS_POSTGRES" = true ]; then
    log_step "Verificando PostgreSQL..."
    if docker-compose exec -T botv2-postgres pg_isready -U botv2 &> /dev/null; then
        log_success "PostgreSQL responde"
    else
        log_warning "PostgreSQL no responde (puede estar inicializando)"
    fi
fi

if [ "$HAS_REDIS" = true ]; then
    log_step "Verificando Redis..."
    if docker-compose exec -T botv2-redis redis-cli ping &> /dev/null; then
        log_success "Redis responde"
    else
        log_warning "Redis no responde (puede estar inicializando)"
    fi
fi

log_step "Esperando 10 segundos para que aplicaciones arranquen..."
sleep 10

if [ "$HAS_APP" = true ]; then
    log_step "Verificando API..."
    if curl -s http://localhost:8000/health &> /dev/null; then
        log_success "API está respondiendo"
    else
        log_warning "API no responde aún (puede estar inicializando)"
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Verificando Dashboard..."
    if curl -s http://localhost:8050/health &> /dev/null; then
        log_success "Dashboard está respondiendo"
    else
        log_warning "Dashboard no responde aún (puede estar inicializando)"
    fi
fi

# ============================================================================
# PASO 10: Resumen final
# ============================================================================

log_header "✨ Actualización Completada"

echo -e "${GREEN}ACTUALIZACIÓN EXITOSA${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Estado:"

if [ "$HAS_APP" = true ]; then
    echo "  ✓ App (botv2-app):     ACTUALIZADA"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo "  ✓ Dashboard:           ACTUALIZADA"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo "  ✓ PostgreSQL:          INTACTO (datos preservados)"
    if [ -n "$BACKUP_FILE" ]; then
        echo ""
        echo "📁 Backup:"
        echo "  ✓ Ubicación: $BACKUP_FILE"
    fi
else
    echo "  ℹ PostgreSQL:          NO ACTIVO (modo demo)"
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  ✓ Redis:               INTACTO"
fi

echo ""
echo "🎯 Modo: $MODE"
echo ""
echo "🌐 Acceso:"

if [ "$HAS_APP" = true ]; then
    echo "  • API:       http://localhost:8000"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo "  • Dashboard: http://localhost:8050"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo "  • Base datos: localhost:5432"
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  • Cache:      localhost:6379"
fi

echo ""
echo "📋 Comandos útiles:"

if [ "$HAS_APP" = true ]; then
    echo "  • Ver logs app:   docker-compose logs -f botv2-app"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo "  • Ver logs dash:  docker-compose logs -f botv2-dashboard"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo "  • Conectar BD:    docker-compose exec botv2-postgres psql -U botv2 -d botv2_db"
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  • Conectar Cache: docker-compose exec botv2-redis redis-cli"
fi

echo "  • Ver estado:     docker-compose ps"
echo ""
echo -e "${GREEN}¡Actualización completada exitosamente! 🎉${NC}"
echo ""
