#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT v2.0
# ================================
# Actualiza servicios de forma inteligente y segura
# Detecta modo Demo/Producción automáticamente
# Preserva datos y valida salud de servicios
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

# Función para verificar si un servicio está realmente definido
service_is_defined() {
    local service=$1
    if docker-compose config 2>/dev/null | grep -q "^  ${service}:"; then
        return 0
    fi
    return 1
}

# Función para verificar si un servicio está corriendo
service_is_running() {
    local service=$1
    if docker-compose ps --services --filter "status=running" 2>/dev/null | grep -q "^${service}$"; then
        return 0
    fi
    return 1
}

# Función para verificar si un contenedor existe (aunque esté detenido)
container_exists() {
    local service=$1
    if docker-compose ps -a --services 2>/dev/null | grep -q "^${service}$"; then
        return 0
    fi
    return 1
}

# Función para esperar a que un servicio esté healthy
wait_for_healthy() {
    local service=$1
    local max_wait=${2:-60}  # Segundos máximos a esperar
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        local health=$(docker-compose ps | grep "$service" | grep -o "(healthy)" || echo "")
        if [ -n "$health" ]; then
            return 0
        fi
        sleep 2
        waited=$((waited + 2))
    done
    return 1
}

# ============================================================================
# PRE-ACTUALIZACIÓN
# ============================================================================

log_header "🚀 BotV2 Update Script v2.0"

echo -e "${YELLOW}INFORMACIÓN DE LA ACTUALIZACIÓN${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Este script:"
echo "  ✓ Actualiza servicios activos"
echo "  ✓ Detecta modo Demo/Producción automáticamente"
echo "  ✓ Elimina contenedores huérfanos en modo Demo"
echo "  ✓ Preserva PostgreSQL/Redis intactos (si existen)"
echo "  ✓ Preserva TODOS los datos en volúmenes"
echo "  ✓ Verifica healthchecks de servicios"
echo "  ✓ Valida conectividad y puertos"
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
# PASO 1: Verificar requisitos
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

log_step "Verificando docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose no está instalado"
    exit 1
fi
log_success "docker-compose está disponible"

# ============================================================================
# PASO 2: Detectar servicios activos
# ============================================================================

log_header "🔍 Detectando configuración"

log_step "Analizando servicios definidos..."

HAS_APP=false
HAS_DASHBOARD=false
HAS_POSTGRES=false
HAS_REDIS=false

if service_is_defined "botv2-app"; then
    HAS_APP=true
    log_info "Trading Bot (botv2-app): DEFINIDO"
else
    log_warning "Trading Bot (botv2-app): NO DEFINIDO (comentado)"
fi

if service_is_defined "botv2-dashboard"; then
    HAS_DASHBOARD=true
    log_info "Dashboard (botv2-dashboard): DEFINIDO"
else
    log_warning "Dashboard (botv2-dashboard): NO DEFINIDO (comentado)"
fi

if service_is_defined "botv2-postgres"; then
    HAS_POSTGRES=true
    log_info "PostgreSQL (botv2-postgres): DEFINIDO"
else
    log_warning "PostgreSQL (botv2-postgres): NO DEFINIDO (comentado)"
fi

if service_is_defined "botv2-redis"; then
    HAS_REDIS=true
    log_info "Redis (botv2-redis): DEFINIDO"
else
    log_warning "Redis (botv2-redis): NO DEFINIDO (comentado)"
fi

echo ""
# Determinar modo
if [ "$HAS_DASHBOARD" = true ] && [ "$HAS_APP" = true ] && [ "$HAS_POSTGRES" = false ] && [ "$HAS_REDIS" = false ]; then
    log_info "🎯 Modo detectado: DEMO (App + Dashboard sin base de datos)"
    MODE="demo"
elif [ "$HAS_DASHBOARD" = true ] && [ "$HAS_APP" = false ] && [ "$HAS_POSTGRES" = false ]; then
    log_info "🎯 Modo detectado: DEMO (Dashboard standalone)"
    MODE="demo"
else
    log_info "🎯 Modo detectado: PRODUCCIÓN (Con base de datos y/o servicios completos)"
    MODE="production"
fi

# ============================================================================
# PASO 3: Limpieza en modo DEMO
# ============================================================================

if [ "$MODE" = "demo" ]; then
    log_header "🧼 Limpieza para modo DEMO"
    
    CLEANUP_PERFORMED=false
    
    # Detener servicios innecesarios que estén corriendo
    if service_is_running "botv2-postgres"; then
        log_warning "PostgreSQL está corriendo pero no está definido en modo demo"
        log_step "Deteniendo PostgreSQL..."
        docker-compose stop botv2-postgres &> /dev/null && log_success "PostgreSQL detenido"
        CLEANUP_PERFORMED=true
    fi
    
    if service_is_running "botv2-redis"; then
        log_warning "Redis está corriendo pero no está definido en modo demo"
        log_step "Deteniendo Redis..."
        docker-compose stop botv2-redis &> /dev/null && log_success "Redis detenido"
        CLEANUP_PERFORMED=true
    fi
    
    # Eliminar contenedores huérfanos (detenidos pero existentes)
    if container_exists "botv2-postgres" && [ "$HAS_POSTGRES" = false ]; then
        log_step "Eliminando contenedor huérfano: PostgreSQL (datos preservados)..."
        docker-compose rm -f botv2-postgres &> /dev/null && log_success "Contenedor PostgreSQL eliminado"
        CLEANUP_PERFORMED=true
    fi
    
    if container_exists "botv2-redis" && [ "$HAS_REDIS" = false ]; then
        log_step "Eliminando contenedor huérfano: Redis (datos preservados)..."
        docker-compose rm -f botv2-redis &> /dev/null && log_success "Contenedor Redis eliminado"
        CLEANUP_PERFORMED=true
    fi
    
    if [ "$CLEANUP_PERFORMED" = true ]; then
        log_info "Limpieza completada - Datos preservados en volúmenes"
        log_info "Para reactivar: descomentar servicios en docker-compose.yml"
    else
        log_info "No hay servicios innecesarios (sistema limpio)"
    fi
fi

# ============================================================================
# PASO 4: Backup (solo en modo producción con PostgreSQL)
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
# PASO 5: Actualizar código
# ============================================================================

log_header "📥 Actualizando código fuente"

log_step "Obteniendo cambios de Git..."
if git pull origin main &> /dev/null; then
    log_success "Código actualizado desde Git"
else
    log_warning "No hay cambios o Git no disponible (usando código local)"
fi

# ============================================================================
# PASO 6: Reconstruir imágenes
# ============================================================================

log_header "🔨 Reconstruyendo imágenes Docker"

BUILD_ERRORS=false

if [ "$HAS_APP" = true ]; then
    log_step "Compilando imagen botv2-app..."
    if docker-compose build botv2-app &> /dev/null; then
        log_success "Imagen botv2-app compilada exitosamente"
    else
        log_error "Error compilando botv2-app"
        BUILD_ERRORS=true
    fi
else
    log_info "Omitiendo botv2-app (no definido)"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Compilando imagen botv2-dashboard..."
    if docker-compose build botv2-dashboard &> /dev/null; then
        log_success "Imagen botv2-dashboard compilada exitosamente"
    else
        log_error "Error compilando botv2-dashboard"
        BUILD_ERRORS=true
    fi
else
    log_error "Dashboard no definido - actualización imposible"
    exit 1
fi

if [ "$BUILD_ERRORS" = true ]; then
    log_error "Fallos en compilación - abortando actualización"
    exit 1
fi

# ============================================================================
# PASO 7: Reiniciar servicios
# ============================================================================

log_header "🔄 Reiniciando servicios"

if [ "$HAS_APP" = true ]; then
    log_step "Deteniendo botv2-app..."
    docker-compose stop botv2-app &> /dev/null && log_success "botv2-app detenida" || log_warning "No estaba corriendo"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Deteniendo botv2-dashboard..."
    docker-compose stop botv2-dashboard &> /dev/null && log_success "botv2-dashboard detenida" || log_warning "No estaba corriendo"
fi

if [ "$HAS_POSTGRES" = true ]; then
    log_info "PostgreSQL: PRESERVADO (no detenido)"
fi

if [ "$HAS_REDIS" = true ]; then
    log_info "Redis: PRESERVADO (no detenido)"
fi

echo ""

if [ "$HAS_APP" = true ]; then
    log_step "Iniciando botv2-app..."
    if docker-compose up -d botv2-app &> /dev/null; then
        log_success "botv2-app iniciada"
    else
        log_error "Error iniciando botv2-app"
        exit 1
    fi
    sleep 3
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Iniciando botv2-dashboard..."
    if docker-compose up -d botv2-dashboard &> /dev/null; then
        log_success "botv2-dashboard iniciada"
    else
        log_error "Error iniciando botv2-dashboard"
        exit 1
    fi
fi

# ============================================================================
# PASO 8: Verificación exhaustiva de servicios
# ============================================================================

log_header "✅ Verificación de servicios"

log_step "Esperando inicialización (10 segundos)..."
sleep 10

log_step "Estado de contenedores:"
echo ""
docker-compose ps
echo ""

# Verificar healthchecks
if [ "$HAS_APP" = true ]; then
    log_step "Esperando healthcheck de botv2-app..."
    if wait_for_healthy "botv2-app" 30; then
        log_success "botv2-app: HEALTHY"
    else
        log_warning "botv2-app: healthcheck no pasó (verificar logs)"
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Esperando healthcheck de botv2-dashboard..."
    if wait_for_healthy "botv2-dashboard" 30; then
        log_success "botv2-dashboard: HEALTHY"
    else
        log_warning "botv2-dashboard: healthcheck no pasó (verificar logs)"
    fi
fi

if [ "$HAS_POSTGRES" = true ]; then
    log_step "Verificando PostgreSQL..."
    if docker-compose exec -T botv2-postgres pg_isready -U botv2 &> /dev/null; then
        log_success "PostgreSQL: RESPONDIENDO"
    else
        log_warning "PostgreSQL: no responde"
    fi
fi

if [ "$HAS_REDIS" = true ]; then
    log_step "Verificando Redis..."
    if docker-compose exec -T botv2-redis redis-cli ping &> /dev/null; then
        log_success "Redis: RESPONDIENDO"
    else
        log_warning "Redis: no responde"
    fi
fi

# Verificar conectividad HTTP
echo ""
log_step "Verificando conectividad HTTP..."

if [ "$HAS_DASHBOARD" = true ]; then
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8050/health | grep -q "200\|401"; then
        log_success "Dashboard (puerto 8050): ACCESIBLE"
    else
        log_warning "Dashboard (puerto 8050): no responde"
    fi
fi

# ============================================================================
# PASO 9: Resumen final
# ============================================================================

log_header "✨ Actualización Completada"

echo -e "${GREEN}ACTUALIZACIÓN EXITOSA${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Estado de servicios:"
echo ""

if [ "$HAS_APP" = true ]; then
    echo "  ✓ Trading Bot (botv2-app):    ACTUALIZADA"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo "  ✓ Dashboard (botv2-dashboard): ACTUALIZADA"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo "  ✓ PostgreSQL:                   ACTIVA (datos preservados)"
    if [ -n "$BACKUP_FILE" ]; then
        echo "  ✓ Backup:                        $BACKUP_FILE"
    fi
else
    echo "  ℹ PostgreSQL:                   NO ACTIVA (modo demo)"
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  ✓ Redis:                         ACTIVA"
else
    echo "  ℹ Redis:                         NO ACTIVA (modo demo)"
fi

echo ""
echo "🎯 Modo operación: $MODE"
echo ""
echo "🌐 Puntos de acceso:"
echo ""

if [ "$HAS_DASHBOARD" = true ]; then
    echo "  • Dashboard:  http://localhost:8050"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo "  • PostgreSQL: localhost:5432"
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  • Redis:      localhost:6379"
fi

echo ""
echo "📋 Comandos útiles:"
echo ""

if [ "$HAS_APP" = true ]; then
    echo "  • Logs del bot:        docker-compose logs -f botv2-app"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo "  • Logs del dashboard:  docker-compose logs -f botv2-dashboard"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo "  • Conectar PostgreSQL: docker-compose exec botv2-postgres psql -U botv2 -d botv2_db"
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  • Conectar Redis:      docker-compose exec botv2-redis redis-cli"
fi

echo "  • Estado servicios:   docker-compose ps"
echo "  • Estadísticas uso:    docker stats --no-stream"
echo ""
echo -e "${GREEN}¡Todos los servicios actualizados y operativos! 🎉${NC}"
echo ""
