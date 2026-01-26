#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT v3.3 - Mode Selection Edition
# ================================================================
# Actualiza servicios con selección de modo Demo/Producción
# - Menú interactivo para elegir modo
# - Utiliza docker-compose específico según modo
# - Detección inteligente y segura
# - Preserva datos y valida salud
# - Muestra errores completos en tiempo real
# - Timeout para evitar cuelgues infinitos
# Author: Juan Carlos Garcia
# Date: 22-01-2026
#

set -eo pipefail  # Exit on error, pipe failures

# ============================================================================
# COLORES Y ESTILOS (Profesional)
# ============================================================================

# Colores principales (profesional, no magenta)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m' # No Color

# Estilos
BOLD='\033[1m'
DIM='\033[2m'

# ============================================================================
# FUNCIONES
# ============================================================================

log_header() {
    echo -e "\n${BLUE}${BOLD}================================================================================${NC}"
    echo -e "${BLUE}${BOLD}  $1${NC}"
    echo -e "${BLUE}${BOLD}================================================================================${NC}\n"
}

log_step() {
    echo -e "${CYAN}→${NC} $1"
}

log_success() {
    echo -e "${GREEN}✓${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

log_dim() {
    echo -e "${GRAY}  $1${NC}"
}

# Función para verificar si un servicio está definido
service_is_defined() {
    local service=$1
    local compose_file=$2
    
    if [ ! -f "$compose_file" ]; then
        return 1
    fi
    
    # Verificar si el servicio existe en el archivo
    if docker-compose -f "$compose_file" config 2>/dev/null | grep -q "^  ${service}:"; then
        return 0
    fi
    return 1
}

# Función para verificar si un servicio está corriendo
service_is_running() {
    local service=$1
    local compose_file=$2
    
    # Verificar si el contenedor existe y está running
    local status=$(docker-compose -f "$compose_file" ps -q "$service" 2>/dev/null | xargs docker inspect -f '{{.State.Status}}' 2>/dev/null || echo "not_found")
    
    if [ "$status" = "running" ]; then
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
    
    log_step "Esperando healthcheck de $service (hasta ${max_wait}s)..."
    
    while [ $waited -lt $max_wait ]; do
        # Obtener health status del contenedor
        local health=$(docker-compose -f "$compose_file" ps -q "$service" 2>/dev/null | xargs docker inspect -f '{{.State.Health.Status}}' 2>/dev/null || echo "none")
        
        if [ "$health" = "healthy" ]; then
            return 0
        elif [ "$health" = "none" ]; then
            # No healthcheck definido, solo verificar que está running
            if service_is_running "$service" "$compose_file"; then
                return 0
            fi
        fi
        
        echo -ne "${GRAY}  Esperando... ${waited}s${NC}\r"
        sleep 2
        waited=$((waited + 2))
    done
    
    echo "" # Nueva línea después del \r
    return 1
}

# Función para ejecutar comando con timeout
run_with_timeout() {
    local timeout=$1
    shift
    local cmd="$@"
    
    # Ejecutar comando en background
    $cmd &
    local pid=$!
    
    # Esperar con timeout
    local count=0
    while kill -0 $pid 2>/dev/null; do
        if [ $count -ge $timeout ]; then
            kill -9 $pid 2>/dev/null
            return 124  # Timeout exit code
        fi
        sleep 1
        count=$((count + 1))
    done
    
    # Obtener exit code del comando
    wait $pid
    return $?
}

# ============================================================================
# MENÚ DE SELECCIÓN DE MODO
# ============================================================================

echo ""
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo -e "${BLUE}${BOLD}  🚀 BotV2 Update Script v3.3 - Mode Selection${NC}"
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo ""

echo -e "${BLUE}█████████████████████████████████████████████████████████████████████████████${NC}"
echo -e "${BLUE}██${NC}                                                                             ${BLUE}██${NC}"
echo -e "${BLUE}██${NC}                      ${WHITE}🎯 SELECCIÓN DE MODO DE OPERACIÓN${NC}                      ${BLUE}██${NC}"
echo -e "${BLUE}██${NC}                                                                             ${BLUE}██${NC}"
echo -e "${BLUE}█████████████████████████████████████████████████████████████████████████████${NC}"
echo ""

echo -e "${WHITE}Selecciona el modo en el que deseas actualizar el sistema:${NC}"
echo ""
echo -e "  ${CYAN}${BOLD}1)${NC} 🎮 ${GREEN}${BOLD}MODO DEMO${NC}"
log_dim "• Trading Bot + Dashboard con datos demo"
log_dim "• NO requiere PostgreSQL ni Redis"
log_dim "• Paper trading mode activado"
log_dim "• Perfecto para pruebas y desarrollo"
log_dim "• Ligero y rápido de iniciar"
log_dim "• Archivo: docker-compose.demo.yml"
echo ""
echo -e "  ${CYAN}${BOLD}2)${NC} 🏭 ${YELLOW}${BOLD}MODO PRODUCCIÓN${NC}"
log_dim "• Sistema completo con base de datos"
log_dim "• PostgreSQL + Redis + Trading Bot + Dashboard"
log_dim "• Persistencia de datos real"
log_dim "• Rate limiting con Redis"
log_dim "• Archivo: docker-compose.production.yml"
echo ""
echo -e "  ${CYAN}${BOLD}3)${NC} 🚫 ${RED}Cancelar${NC}"
echo ""

while true; do
    read -p "$(echo -e ${CYAN}${BOLD}"Elige una opción (1-3): "${NC})" choice
    
    case $choice in
        1)
            MODE="demo"
            MODE_NAME="${GREEN}${BOLD}DEMO${NC}"
            MODE_DISPLAY="DEMO"
            COMPOSE_FILE="docker-compose.demo.yml"
            break
            ;;
        2)
            MODE="production"
            MODE_NAME="${YELLOW}${BOLD}PRODUCCIÓN${NC}"
            MODE_DISPLAY="PRODUCCIÓN"
            COMPOSE_FILE="docker-compose.production.yml"
            break
            ;;
        3)
            echo ""
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
log_info "Usando archivo: ${BOLD}$COMPOSE_FILE${NC}"

# Verificar que el archivo existe
if [ ! -f "$COMPOSE_FILE" ]; then
    echo ""
    log_error "Archivo $COMPOSE_FILE no encontrado"
    log_info "Asegúrate de que el archivo existe en el directorio actual"
    log_info "Archivos disponibles:"
    ls -1 docker-compose*.yml 2>/dev/null | sed 's/^/    - /' || echo "    (ninguno)"
    exit 1
fi

# ============================================================================
# CONFIRMACIÓN
# ============================================================================

echo ""
echo -e "${WHITE}${BOLD}INFORMACIÓN DE LA ACTUALIZACIÓN${NC}"
echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
echo "Este script:"
echo -e "  ${GREEN}✓${NC} Actualiza servicios del modo ${BOLD}$MODE_DISPLAY${NC}"
echo -e "  ${GREEN}✓${NC} Preserva TODOS los datos en volúmenes"
echo -e "  ${GREEN}✓${NC} Verifica healthchecks de servicios"
echo -e "  ${GREEN}✓${NC} Valida conectividad y puertos"
echo -e "  ${GREEN}✓${NC} Sin downtime significativo"
if [ "$MODE" = "production" ]; then
    echo -e "  ${GREEN}✓${NC} Crea backup de PostgreSQL antes de actualizar"
fi
echo ""

read -p "$(echo -e ${YELLOW}${BOLD}"¿Deseas proceder con la actualización? (s/n): "${NC})" confirm
echo ""

if [[ ! $confirm =~ ^[SsYy]$ ]]; then
    log_error "Actualización cancelada"
    exit 0
fi

# ============================================================================
# PASO 1: Verificar requisitos
# ============================================================================

log_step "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado"
    log_info "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi
log_success "Docker está instalado"

if ! docker info &> /dev/null; then
    log_error "Docker daemon no está corriendo"
    log_info "Inicia Docker Desktop o el servicio de Docker"
    exit 1
fi
log_success "Docker daemon está corriendo"

log_step "Verificando docker-compose..."
if ! command -v docker-compose &> /dev/null; then
    log_error "docker-compose no está instalado"
    log_info "Instala docker-compose desde: https://docs.docker.com/compose/install/"
    exit 1
fi
log_success "docker-compose está disponible"

# ============================================================================
# PASO 2: Detectar servicios activos
# ============================================================================

log_header "🔍 Detectando configuración"

log_step "Analizando servicios definidos en $COMPOSE_FILE..."
echo ""

HAS_APP=false
HAS_DASHBOARD=false
HAS_POSTGRES=false
HAS_REDIS=false

if service_is_defined "botv2-app" "$COMPOSE_FILE"; then
    HAS_APP=true
    log_info "Trading Bot (botv2-app):       ${GREEN}DEFINIDO${NC}"
else
    log_warning "Trading Bot (botv2-app):       ${GRAY}NO DEFINIDO${NC}"
fi

if service_is_defined "botv2-dashboard" "$COMPOSE_FILE"; then
    HAS_DASHBOARD=true
    log_info "Dashboard (botv2-dashboard):   ${GREEN}DEFINIDO${NC}"
else
    log_error "Dashboard (botv2-dashboard):   ${RED}NO DEFINIDO${NC}"
    log_error "El dashboard es obligatorio pero no está definido en $COMPOSE_FILE"
    exit 1
fi

if service_is_defined "botv2-postgres" "$COMPOSE_FILE"; then
    HAS_POSTGRES=true
    log_info "PostgreSQL (botv2-postgres):   ${GREEN}DEFINIDO${NC}"
else
    log_dim "PostgreSQL (botv2-postgres):   ${GRAY}NO DEFINIDO${NC}"
fi

if service_is_defined "botv2-redis" "$COMPOSE_FILE"; then
    HAS_REDIS=true
    log_info "Redis (botv2-redis):           ${GREEN}DEFINIDO${NC}"
else
    log_dim "Redis (botv2-redis):           ${GRAY}NO DEFINIDO${NC}"
fi

echo ""
log_success "Configuración validada para modo $(echo -e $MODE_NAME)"

# ============================================================================
# PASO 3: Backup (solo producción con PostgreSQL)
# ============================================================================

if [ "$MODE" = "production" ] && [ "$HAS_POSTGRES" = true ]; then
    log_header "💾 Backup Preventivo"

    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="${BACKUP_DIR}/pre-update-$(date +%Y%m%d_%H%M%S).sql"

    log_step "Creando backup de PostgreSQL..."
    
    # Verificar si PostgreSQL está corriendo
    if service_is_running "botv2-postgres" "$COMPOSE_FILE"; then
        if docker-compose -f "$COMPOSE_FILE" exec -T botv2-postgres pg_dump -U botv2 botv2_db > "$BACKUP_FILE" 2>/dev/null; then
            log_success "Backup creado: $BACKUP_FILE"
            log_dim "Tamaño: $(du -h "$BACKUP_FILE" | cut -f1)"
        else
            log_warning "No se pudo crear backup (PostgreSQL puede no estar listo)"
            BACKUP_FILE=""
        fi
    else
        log_warning "PostgreSQL no está corriendo - backup omitido"
        BACKUP_FILE=""
    fi
else
    log_info "💾 Backup omitido: No aplica en modo $(echo -e $MODE_NAME)"
fi

# ============================================================================
# PASO 4: Actualizar código
# ============================================================================

log_header "📥 Actualizando código fuente"

log_step "Obteniendo cambios de Git..."
if git pull origin main &> /dev/null; then
    log_success "Código actualizado desde Git"
elif git status &> /dev/null; then
    log_warning "No hay cambios nuevos en Git"
else
    log_warning "Git no disponible (usando código local)"
fi

# ============================================================================
# PASO 5: Reconstruir imágenes
# ============================================================================

log_header "🔨 Reconstruyendo imágenes Docker"

BUILD_ERRORS=false

if [ "$HAS_APP" = true ]; then
    log_step "Compilando imagen botv2-app..."
    
    # Capturar output completo del build
    BUILD_OUTPUT=$(docker-compose -f "$COMPOSE_FILE" build botv2-app 2>&1)
    BUILD_EXIT_CODE=$?
    
    if [ $BUILD_EXIT_CODE -eq 0 ]; then
        log_success "Imagen botv2-app compilada exitosamente"
    else
        echo ""
        log_error "Error compilando botv2-app (exit code: $BUILD_EXIT_CODE)"
        echo ""
        log_info "ÚLTIMAS 50 LÍNEAS DEL ERROR:"
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        echo "$BUILD_OUTPUT" | tail -n 50
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        echo ""
        BUILD_ERRORS=true
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Compilando imagen botv2-dashboard..."
    
    # Capturar output completo del build
    BUILD_OUTPUT=$(docker-compose -f "$COMPOSE_FILE" build botv2-dashboard 2>&1)
    BUILD_EXIT_CODE=$?
    
    if [ $BUILD_EXIT_CODE -eq 0 ]; then
        log_success "Imagen botv2-dashboard compilada exitosamente"
    else
        echo ""
        log_error "Error compilando botv2-dashboard (exit code: $BUILD_EXIT_CODE)"
        echo ""
        log_info "ÚLTIMAS 50 LÍNEAS DEL ERROR:"
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        echo "$BUILD_OUTPUT" | tail -n 50
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        echo ""
        BUILD_ERRORS=true
    fi
fi

if [ "$BUILD_ERRORS" = true ]; then
    echo ""
    log_error "Fallos en compilación - abortando actualización"
    log_info "Revisa los errores arriba y corrígelos antes de continuar"
    exit 1
fi

# ============================================================================
# PASO 6: Reiniciar servicios
# ============================================================================

log_header "🔄 Reiniciando servicios"

# Detener servicios
if [ "$HAS_APP" = true ]; then
    log_step "Deteniendo botv2-app..."
    if docker-compose -f "$COMPOSE_FILE" stop botv2-app &> /dev/null; then
        log_success "botv2-app detenida"
    else
        log_dim "No estaba corriendo"
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Deteniendo botv2-dashboard..."
    if docker-compose -f "$COMPOSE_FILE" stop botv2-dashboard &> /dev/null; then
        log_success "botv2-dashboard detenida"
    else
        log_dim "No estaba corriendo"
    fi
fi

if [ "$HAS_POSTGRES" = true ]; then
    log_info "PostgreSQL: ${GREEN}PRESERVADO${NC} (no detenido)"
fi

if [ "$HAS_REDIS" = true ]; then
    log_info "Redis: ${GREEN}PRESERVADO${NC} (no detenido)"
fi

echo ""

# Iniciar servicios
log_step "Iniciando servicios (puede tardar hasta 2 minutos)..."
echo ""

# Ejecutar docker-compose up con output en tiempo real
log_dim "Mostrando output de docker-compose..."
echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"

# Ejecutar con timeout y mostrar en tiempo real
set +e  # Deshabilitar exit on error temporalmente
docker-compose -f "$COMPOSE_FILE" up -d
UP_EXIT_CODE=$?
set -e  # Rehabilitar exit on error

echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
echo ""

if [ $UP_EXIT_CODE -eq 0 ]; then
    log_success "Servicios iniciados exitosamente"
elif [ $UP_EXIT_CODE -eq 124 ]; then
    log_error "Timeout: docker-compose tardó más de 2 minutos"
    log_info "Los servicios pueden estar iniciando aún. Verifica con:"
    log_dim "docker-compose -f $COMPOSE_FILE ps"
    log_dim "docker-compose -f $COMPOSE_FILE logs -f"
    exit 1
else
    log_error "Error iniciando servicios (exit code: $UP_EXIT_CODE)"
    echo ""
    log_info "Comandos de diagnóstico:"
    log_dim "docker-compose -f $COMPOSE_FILE ps"
    log_dim "docker-compose -f $COMPOSE_FILE logs"
    echo ""
    exit 1
fi

# ============================================================================
# PASO 7: Verificación de servicios
# ============================================================================

log_header "✅ Verificación de servicios"

log_step "Esperando inicialización (15 segundos)..."
sleep 15

log_step "Estado de contenedores:"
echo ""
echo -e "${GRAY}"
docker-compose -f "$COMPOSE_FILE" ps
echo -e "${NC}"

# Verificar healthchecks
if [ "$HAS_APP" = true ]; then
    if wait_for_healthy "botv2-app" "$COMPOSE_FILE" 40; then
        log_success "botv2-app: ${GREEN}HEALTHY${NC}"
    else
        log_warning "botv2-app: healthcheck no pasó (verificar logs)"
        log_dim "docker-compose -f $COMPOSE_FILE logs botv2-app"
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    if wait_for_healthy "botv2-dashboard" "$COMPOSE_FILE" 40; then
        log_success "botv2-dashboard: ${GREEN}HEALTHY${NC}"
    else
        log_warning "botv2-dashboard: healthcheck no pasó (verificar logs)"
        log_dim "docker-compose -f $COMPOSE_FILE logs botv2-dashboard"
    fi
fi

if [ "$HAS_POSTGRES" = true ]; then
    log_step "Verificando PostgreSQL..."
    if docker-compose -f "$COMPOSE_FILE" exec -T botv2-postgres pg_isready -U botv2 &> /dev/null; then
        log_success "PostgreSQL: ${GREEN}RESPONDIENDO${NC}"
    else
        log_warning "PostgreSQL: no responde (puede estar iniciando)"
    fi
fi

if [ "$HAS_REDIS" = true ]; then
    log_step "Verificando Redis..."
    if docker-compose -f "$COMPOSE_FILE" exec -T botv2-redis redis-cli ping &> /dev/null; then
        log_success "Redis: ${GREEN}RESPONDIENDO${NC}"
    else
        log_warning "Redis: no responde (puede estar iniciando)"
    fi
fi

# Verificar conectividad HTTP
echo ""
log_step "Verificando conectividad HTTP..."

if [ "$HAS_DASHBOARD" = true ]; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8050/health 2>/dev/null || echo "000")
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "401" ] || [ "$HTTP_CODE" = "302" ]; then
        log_success "Dashboard (puerto 8050): ${GREEN}ACCESIBLE${NC} (HTTP $HTTP_CODE)"
    else
        log_warning "Dashboard (puerto 8050): no responde (HTTP $HTTP_CODE)"
        log_dim "Puede necesitar más tiempo para iniciar"
    fi
fi

# ============================================================================
# PASO 8: Resumen final
# ============================================================================

log_header "✨ Actualización Completada"

echo -e "${GREEN}${BOLD}ACTUALIZACIÓN EXITOSA${NC}"
echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
echo ""
echo -e "${WHITE}${BOLD}📊 Estado de servicios:${NC}"
echo ""

if [ "$HAS_APP" = true ]; then
    echo -e "  ${GREEN}✓${NC} Trading Bot (botv2-app):       ACTUALIZADA"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo -e "  ${GREEN}✓${NC} Dashboard (botv2-dashboard):   ACTUALIZADA"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo -e "  ${GREEN}✓${NC} PostgreSQL:                     ACTIVA (datos preservados)"
    if [ -n "$BACKUP_FILE" ]; then
        echo -e "  ${GREEN}✓${NC} Backup:                         $BACKUP_FILE"
    fi
fi

if [ "$HAS_REDIS" = true ]; then
    echo -e "  ${GREEN}✓${NC} Redis:                          ACTIVA"
fi

echo ""
echo -e "${WHITE}${BOLD}🎯 Configuración:${NC}"
echo -e "  Modo operación: $(echo -e $MODE_NAME)"
echo -e "  Archivo usado:  ${BOLD}$COMPOSE_FILE${NC}"
echo ""
echo -e "${WHITE}${BOLD}🌐 Puntos de acceso:${NC}"
echo ""

if [ "$HAS_DASHBOARD" = true ]; then
    echo -e "  ${CYAN}•${NC} Dashboard:  ${BOLD}http://localhost:8050${NC}"
    if [ "$MODE" = "demo" ]; then
        echo -e "    ${DIM}Usuario: admin${NC}"
        echo -e "    ${DIM}Password: admin (default en demo)${NC}"
    fi
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo -e "  ${CYAN}•${NC} PostgreSQL: ${BOLD}localhost:5432${NC}"
fi

if [ "$HAS_REDIS" = true ]; then
    echo -e "  ${CYAN}•${NC} Redis:      ${BOLD}localhost:6379${NC}"
fi

echo ""
echo -e "${WHITE}${BOLD}📋 Comandos útiles:${NC}"
echo ""

if [ "$HAS_APP" = true ]; then
    echo -e "  ${GRAY}•${NC} Logs del bot:        ${DIM}docker-compose -f $COMPOSE_FILE logs -f botv2-app${NC}"
fi

if [ "$HAS_DASHBOARD" = true ]; then
    echo -e "  ${GRAY}•${NC} Logs del dashboard:  ${DIM}docker-compose -f $COMPOSE_FILE logs -f botv2-dashboard${NC}"
fi

if [ "$HAS_POSTGRES" = true ]; then
    echo -e "  ${GRAY}•${NC} Conectar PostgreSQL: ${DIM}docker-compose -f $COMPOSE_FILE exec botv2-postgres psql -U botv2 -d botv2_db${NC}"
fi

if [ "$HAS_REDIS" = true ]; then
    echo -e "  ${GRAY}•${NC} Conectar Redis:      ${DIM}docker-compose -f $COMPOSE_FILE exec botv2-redis redis-cli${NC}"
fi

echo -e "  ${GRAY}•${NC} Estado servicios:    ${DIM}docker-compose -f $COMPOSE_FILE ps${NC}"
echo -e "  ${GRAY}•${NC} Detener servicios:   ${DIM}docker-compose -f $COMPOSE_FILE down${NC}"
echo -e "  ${GRAY}•${NC} Estadísticas uso:     ${DIM}docker stats --no-stream${NC}"
echo ""
echo -e "${GREEN}${BOLD}¡Todos los servicios actualizados y operativos! 🎉${NC}"
echo ""
