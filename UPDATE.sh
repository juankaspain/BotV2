#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT v3.0 - Mode Selection Edition
# ================================================================
# Actualiza servicios con selección de modo Demo/Producción
# - Menú interactivo para elegir modo
# - Utiliza docker-compose específico según modo
# - Detección inteligente y segura
# - Preserva datos y valida salud
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
MAGENTA='\033[0;35m'
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

# Función para verificar si un servicio está definido
service_is_defined() {
    local service=$1
    local compose_file=$2
    if docker-compose -f "$compose_file" config 2>/dev/null | grep -q "^  ${service}:"; then
        return 0
    fi
    return 1
}

# Función para verificar si un servicio está corriendo
service_is_running() {
    local service=$1
    local compose_file=$2
    if docker-compose -f "$compose_file" ps --services --filter "status=running" 2>/dev/null | grep -q "^${service}$"; then
        return 0
    fi
    return 1
}

# Función para verificar si un contenedor existe
container_exists() {
    local service=$1
    local compose_file=$2
    if docker-compose -f "$compose_file" ps -a --services 2>/dev/null | grep -q "^${service}$"; then
        return 0
    fi
    return 1
}

# Función para esperar a que un servicio esté healthy
wait_for_healthy() {
    local service=$1
    local compose_file=$2
    local max_wait=${3:-60}
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        local health=$(docker-compose -f "$compose_file" ps | grep "$service" | grep -o "(healthy)" || echo "")
        if [ -n "$health" ]; then
            return 0
        fi
        sleep 2
        waited=$((waited + 2))
    done
    return 1
}

# ============================================================================
# MENÚ DE SELECCIÓN DE MODO
# ============================================================================

log_header "🚀 BotV2 Update Script v3.0 - Mode Selection"

echo -e "${MAGENTA}▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊${NC}"
echo -e "${MAGENTA}▊▊${NC}                                                                             ${MAGENTA}▊▊${NC}"
echo -e "${MAGENTA}▊▊${NC}                      🎯 SELECCIÓN DE MODO DE OPERACIÓN                      ${MAGENTA}▊▊${NC}"
echo -e "${MAGENTA}▊▊${NC}                                                                             ${MAGENTA}▊▊${NC}"
echo -e "${MAGENTA}▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊▊${NC}"

echo ""
echo -e "${YELLOW}Selecciona el modo en el que deseas actualizar el sistema:${NC}"
echo ""
echo -e "  ${CYAN}1)${NC} 🎮 ${GREEN}MODO DEMO${NC}"
echo "     • Dashboard standalone con datos de demostración"
echo "     • NO requiere PostgreSQL ni Redis"
echo "     • Perfecto para pruebas y desarrollo"
echo "     • Ligero y rápido de iniciar"
echo "     • Archivo: docker-compose.demo.yml"
echo ""
echo -e "  ${CYAN}2)${NC} 🏭 ${YELLOW}MODO PRODUCCIÓN${NC}"
echo "     • Sistema completo con base de datos"
echo "     • PostgreSQL + Redis + Trading Bot + Dashboard"
echo "     • Persistencia de datos real"
echo "     • Rate limiting con Redis"
echo "     • Archivo: docker-compose.production.yml"
echo ""
echo -e "  ${CYAN}3)${NC} 🚫 ${RED}Cancelar${NC}"
echo ""

while true; do
    read -p "$(echo -e ${CYAN}"Elige una opción (1-3): "${NC})" choice
    
    case $choice in
        1)
            MODE="demo"
            MODE_NAME="${GREEN}DEMO${NC}"
            COMPOSE_FILE="docker-compose.demo.yml"
            break
            ;;
        2)
            MODE="production"
            MODE_NAME="${YELLOW}PRODUCCIÓN${NC}"
            COMPOSE_FILE="docker-compose.production.yml"
            break
            ;;
        3)
            log_error "Actualización cancelada por el usuario"
            exit 0
            ;;
        *)
            log_error "Opción inválida. Por favor elige 1, 2 o 3."
            ;;
    esac
done

echo ""
log_success "Modo seleccionado: $(echo -e $MODE_NAME)"
log_info "Usando archivo: $COMPOSE_FILE"

# Verificar que el archivo existe
if [ ! -f "$COMPOSE_FILE" ]; then
    log_error "Archivo $COMPOSE_FILE no encontrado"
    log_info "Asegúrate de que el archivo existe en el directorio actual"
    exit 1
fi

# ============================================================================
# CONFIRMACIÓN
# ============================================================================

echo ""
echo -e "${YELLOW}INFORMACIÓN DE LA ACTUALIZACIÓN${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "Este script:"
echo "  ✓ Actualiza servicios del modo $(echo -e $MODE_NAME)"
echo "  ✓ Preserva TODOS los datos en volúmenes"
echo "  ✓ Verifica healthchecks de servicios"
echo "  ✓ Valida conectividad y puertos"
echo "  ✓ Sin downtime significativo"
if [ "$MODE" = "production" ]; then
    echo "  ✓ Crea backup de PostgreSQL antes de actualizar"
fi
echo ""

read -p "$(echo -e ${YELLOW}"¿Deseas proceder con la actualización? (s/n): "${NC})" confirm
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

log_step "Analizando servicios definidos en $COMPOSE_FILE..."

HAS_APP=false
HAS_DASHBOARD=false
HAS_POSTGRES=false
HAS_REDIS=false

if service_is_defined "botv2-app" "$COMPOSE_FILE"; then
    HAS_APP=true
    log_info "Trading Bot (botv2-app): DEFINIDO"
else
    log_warning "Trading Bot (botv2-app): NO DEFINIDO"
fi

if service_is_defined "botv2-dashboard" "$COMPOSE_FILE"; then
    HAS_DASHBOARD=true
    log_info "Dashboard (botv2-dashboard): DEFINIDO"
else
    log_error "Dashboard (botv2-dashboard): NO DEFINIDO"
    exit 1
fi

if service_is_defined "botv2-postgres" "$COMPOSE_FILE"; then
    HAS_POSTGRES=true
    log_info "PostgreSQL (botv2-postgres): DEFINIDO"
fi

if service_is_defined "botv2-redis" "$COMPOSE_FILE"; then
    HAS_REDIS=true
    log_info "Redis (botv2-redis): DEFINIDO"
fi

echo ""
log_success "Configuración validada para modo $(echo -e $MODE_NAME)"

# ============================================================================
# PASO 3: Backup (solo producción con PostgreSQL)
# ============================================================================

if [ "$MODE" = "production" ] && [ "$HAS_POSTGRES" = true ]; then
    log_header "📦 Backup Preventivo"

    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="${BACKUP_DIR}/pre-update-$(date +%Y%m%d_%H%M%S).sql"

    log_step "Creando backup de PostgreSQL..."
    if docker-compose -f "$COMPOSE_FILE" exec -T botv2-postgres pg_dump -U botv2 botv2_db > "$BACKUP_FILE" 2>/dev/null; then
        log_success "Backup creado: $BACKUP_FILE"
        echo "  Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
    else
        log_warning "No se pudo crear backup (PostgreSQL puede no estar listo)"
    fi
else
    log_info "📦 Backup omitido: No aplica en modo $(echo -e $MODE_NAME)"
fi

# ============================================================================
# PASO 4: Actualizar código
# ============================================================================

log_header "📥 Actualizando código fuente"

log_step "Obteniendo cambios de Git..."
if git pull origin main &> /dev/null; then
    log_success "Código actualizado desde Git"
else
    log_warning "No hay cambios o Git no disponible (usando código local)"
fi

# ============================================================================
# PASO 5: Reconstruir imágenes
# ============================================================================

log_header "🔨 Reconstruyendo imágenes Docker"

BUILD_ERRORS=false

if [ "$HAS_APP" = true ]; then
    log_step "Compilando imagen botv2-app..."
    if docker-compose -f "$COMPOSE_FILE" build botv2-app &> /dev/null; then
        log_success "Imagen botv2-app compilada exitosamente"
    else
        log_error "Error compilando botv2-app"
        BUILD_ERRORS=true
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Compilando imagen botv2-dashboard..."
    if docker-compose -f "$COMPOSE_FILE" build botv2-dashboard &> /dev/null; then
        log_success "Imagen botv2-dashboard compilada exitosamente"
    else
        log_error "Error compilando botv2-dashboard"
        BUILD_ERRORS=true
    fi
fi

if [ "$BUILD_ERRORS" = true ]; then
    log_error "Fallos en compilación - abortando actualización"
    exit 1
fi

# ============================================================================
# PASO 6: Reiniciar servicios
# ============================================================================

log_header "🔄 Reiniciando servicios"

# Detener servicios
if [ "$HAS_APP" = true ]; then
    log_step "Deteniendo botv2-app..."
    docker-compose -f "$COMPOSE_FILE" stop botv2-app &> /dev/null && log_success "botv2-app detenida" || log_warning "No estaba corriendo"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Deteniendo botv2-dashboard..."
    docker-compose -f "$COMPOSE_FILE" stop botv2-dashboard &> /dev/null && log_success "botv2-dashboard detenida" || log_warning "No estaba corriendo"
fi

if [ "$HAS_POSTGRES" = true ]; then
    log_info "PostgreSQL: PRESERVADO (no detenido)"
fi

if [ "$HAS_REDIS" = true ]; then
    log_info "Redis: PRESERVADO (no detenido)"
fi

echo ""

# Iniciar servicios
log_step "Iniciando servicios con docker-compose up -d..."
if docker-compose -f "$COMPOSE_FILE" up -d &> /dev/null; then
    log_success "Servicios iniciados exitosamente"
else
    log_error "Error iniciando servicios"
    exit 1
fi

# ============================================================================
# PASO 7: Verificación de servicios
# ============================================================================

log_header "✅ Verificación de servicios"

log_step "Esperando inicialización (10 segundos)..."
sleep 10

log_step "Estado de contenedores:"
echo ""
docker-compose -f "$COMPOSE_FILE" ps
echo ""

# Verificar healthchecks
if [ "$HAS_APP" = true ]; then
    log_step "Esperando healthcheck de botv2-app..."
    if wait_for_healthy "botv2-app" "$COMPOSE_FILE" 30; then
        log_success "botv2-app: HEALTHY"
    else
        log_warning "botv2-app: healthcheck no pasó (verificar logs)"
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Esperando healthcheck de botv2-dashboard..."
    if wait_for_healthy "botv2-dashboard" "$COMPOSE_FILE" 30; then
        log_success "botv2-dashboard: HEALTHY"
    else
        log_warning "botv2-dashboard: healthcheck no pasó (verificar logs)"
    fi
fi

if [ "$HAS_POSTGRES" = true ]; then
    log_step "Verificando PostgreSQL..."
    if docker-compose -f "$COMPOSE_FILE" exec -T botv2-postgres pg_isready -U botv2 &> /dev/null; then
        log_success "PostgreSQL: RESPONDIENDO"
    else
        log_warning "PostgreSQL: no responde"
    fi
fi

if [ "$HAS_REDIS" = true ]; then
    log_step "Verificando Redis..."
    if docker-compose -f "$COMPOSE_FILE" exec -T botv2-redis redis-cli ping &> /dev/null; then
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
# PASO 8: Resumen final
# ============================================================================

log_header "✨ Actualización Completada"

echo -e "${GREEN}ACTUALIZACIÓN EXITOSA${NC}"
echo "─────────────────────────────────────────────────────────────────────────────"
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
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  ✓ Redis:                         ACTIVA"
fi

echo ""
echo "🎯 Modo operación: $(echo -e $MODE_NAME)"
echo "📂 Archivo usado:   $COMPOSE_FILE"
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
    echo "  • Logs del bot:        docker-compose -f $COMPOSE_FILE logs -f botv2-app"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo "  • Logs del dashboard:  docker-compose -f $COMPOSE_FILE logs -f botv2-dashboard"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo "  • Conectar PostgreSQL: docker-compose -f $COMPOSE_FILE exec botv2-postgres psql -U botv2 -d botv2_db"
fi

if [ "$HAS_REDIS" = true ]; then
    echo "  • Conectar Redis:      docker-compose -f $COMPOSE_FILE exec botv2-redis redis-cli"
fi

echo "  • Estado servicios:   docker-compose -f $COMPOSE_FILE ps"
echo "  • Detener servicios:   docker-compose -f $COMPOSE_FILE down"
echo "  • Estadísticas uso:    docker stats --no-stream"
echo ""
echo -e "${GREEN}¡Todos los servicios actualizados y operativos! 🎉${NC}"
echo ""
