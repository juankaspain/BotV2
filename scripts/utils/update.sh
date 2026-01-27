#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT v3.7 - Professional Error Handling
# ================================================================
# Actualiza servicios con selección de modo Demo/Producción
# - Manejo profesional de errores con información detallada
# - Menú interactivo para elegir modo
# - Comandos con rutas absolutas para fácil copy-paste
# Author: Juan Carlos Garcia
# Date: 27-01-2026
#

set -o pipefail

# ============================================================================
# DETECTAR Y NAVEGAR A LA RAÍZ DEL PROYECTO
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# ============================================================================
# COLORES Y ESTILOS
# ============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
GRAY='\033[0;90m'
NC='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'

# ============================================================================
# VARIABLES GLOBALES
# ============================================================================

CURRENT_STEP=""
CURRENT_COMMAND=""
ERROR_LOG_FILE="/tmp/botv2_update_error_$$.log"
BUILD_LOG_FILE="/tmp/botv2_build_$$.log"
COMPOSE_FILE=""

# ============================================================================
# FUNCIONES DE LOGGING
# ============================================================================

log_header() {
    echo -e "\n${BLUE}${BOLD}================================================================================${NC}"
    echo -e "${BLUE}${BOLD}  $1${NC}"
    echo -e "${BLUE}${BOLD}================================================================================${NC}\n"
}

log_step() {
    CURRENT_STEP="$1"
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

# ============================================================================
# FUNCIÓN DE MANEJO DE ERRORES
# ============================================================================

show_error_banner() {
    local exit_code=$1
    local line_number=$2
    local command="$3"
    local step="$4"
    
    echo ""
    echo -e "${RED}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}${BOLD}║                           ❌ ERROR DURANTE LA EJECUCIÓN                       ║${NC}"
    echo -e "${RED}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${WHITE}${BOLD}📋 Detalles del error:${NC}"
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "  ${CYAN}Paso actual:${NC}      $step"
    echo -e "  ${CYAN}Código de salida:${NC} $exit_code"
    echo -e "  ${CYAN}Comando:${NC}          ${DIM}$command${NC}"
    echo -e "  ${CYAN}Directorio:${NC}       $PROJECT_ROOT"
    echo ""
    
    if [ -f "$BUILD_LOG_FILE" ] && [ -s "$BUILD_LOG_FILE" ]; then
        echo -e "${WHITE}${BOLD}📜 Últimas 30 líneas del log:${NC}"
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        tail -n 30 "$BUILD_LOG_FILE"
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        echo ""
    fi
    
    echo -e "${WHITE}${BOLD}🔧 Comandos de diagnóstico (copy-paste):${NC}"
    echo ""
    echo -e "  ${DIM}cd $PROJECT_ROOT${NC}"
    echo -e "  ${DIM}docker-compose -f $COMPOSE_FILE logs${NC}"
    echo -e "  ${DIM}docker-compose -f $COMPOSE_FILE ps -a${NC}"
    echo ""
}

cleanup() {
    rm -f "$ERROR_LOG_FILE" 2>/dev/null
    rm -f "$BUILD_LOG_FILE" 2>/dev/null
}

error_handler() {
    local exit_code=$?
    local line_number=$1
    
    if [ $exit_code -eq 130 ]; then
        echo ""
        echo -e "${YELLOW}${BOLD}⚠ Actualización cancelada por el usuario (Ctrl+C)${NC}"
        cleanup
        exit 130
    fi
    
    show_error_banner "$exit_code" "$line_number" "$CURRENT_COMMAND" "$CURRENT_STEP"
    cleanup
    exit $exit_code
}

interrupt_handler() {
    echo ""
    echo -e "\n${YELLOW}${BOLD}⚠ Operación interrumpida por el usuario${NC}"
    cleanup
    exit 130
}

trap 'error_handler $LINENO' ERR
trap 'interrupt_handler' SIGINT SIGTERM

# ============================================================================
# FUNCIONES DE DOCKER BUILD
# ============================================================================

run_docker_build() {
    local service=$1
    local compose_file=$2
    
    CURRENT_COMMAND="docker-compose -f $compose_file build $service"
    
    log_step "Compilando imagen $service..."
    log_dim "Mostrando progreso en tiempo real..."
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    
    if docker-compose -f "$compose_file" build "$service" 2>&1 | tee "$BUILD_LOG_FILE"; then
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        log_success "Imagen $service compilada exitosamente"
        return 0
    else
        local exit_code=${PIPESTATUS[0]}
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        log_error "Error compilando $service (exit code: $exit_code)"
        return $exit_code
    fi
}

# ============================================================================
# FUNCIONES DE SERVICIO
# ============================================================================

service_is_defined() {
    local service=$1
    local compose_file=$2
    
    [ -f "$compose_file" ] && docker-compose -f "$compose_file" config --services 2>/dev/null | grep -qx "$service"
}

service_is_running() {
    local service=$1
    local compose_file=$2
    
    local container_id=$(docker-compose -f "$compose_file" ps -q "$service" 2>/dev/null)
    [ -n "$container_id" ] && [ "$(docker inspect -f '{{.State.Status}}' "$container_id" 2>/dev/null)" = "running" ]
}

wait_for_healthy() {
    local service=$1
    local compose_file=$2
    local max_wait=${3:-60}
    local waited=0
    
    log_step "Esperando healthcheck de $service (hasta ${max_wait}s)..."
    
    while [ $waited -lt $max_wait ]; do
        local container_id=$(docker-compose -f "$compose_file" ps -q "$service" 2>/dev/null)
        
        if [ -n "$container_id" ]; then
            local health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container_id" 2>/dev/null || echo "none")
            
            if [ "$health" = "healthy" ]; then
                return 0
            elif [ "$health" = "none" ]; then
                local status=$(docker inspect -f '{{.State.Status}}' "$container_id" 2>/dev/null || echo "not_found")
                [ "$status" = "running" ] && return 0
            fi
        fi
        
        printf "${GRAY}  Esperando... %ds${NC}\r" "$waited"
        sleep 2
        waited=$((waited + 2))
    done
    
    echo ""
    return 1
}

# ============================================================================
# INICIO DEL SCRIPT
# ============================================================================

echo ""
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo -e "${BLUE}${BOLD}  🚀 BotV2 Update Script v3.7${NC}"
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo ""

log_info "Directorio del proyecto: ${BOLD}$PROJECT_ROOT${NC}"
echo ""

# ============================================================================
# MENÚ DE SELECCIÓN DE MODO
# ============================================================================

echo -e "${BLUE}█████████████████████████████████████████████████████████████████████████████${NC}"
echo -e "${BLUE}██${NC}                      ${WHITE}🎯 SELECCIÓN DE MODO DE OPERACIÓN${NC}                      ${BLUE}██${NC}"
echo -e "${BLUE}█████████████████████████████████████████████████████████████████████████████${NC}"
echo ""
echo -e "${WHITE}Selecciona el modo:${NC}"
echo ""
echo -e "  ${CYAN}${BOLD}1)${NC} 🎮 ${GREEN}${BOLD}MODO DEMO${NC} - Sin BD, datos mock, rápido"
echo -e "  ${CYAN}${BOLD}2)${NC} 🏭 ${YELLOW}${BOLD}MODO PRODUCCIÓN${NC} - PostgreSQL + Redis completo"
echo -e "  ${CYAN}${BOLD}3)${NC} 🚫 ${RED}Cancelar${NC}"
echo ""

while true; do
    read -p "$(echo -e ${CYAN}${BOLD}"Opción (1-3): "${NC})" choice
    
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
            log_info "Cancelado"
            cleanup
            exit 0
            ;;
        *)
            log_error "Opción inválida"
            ;;
    esac
done

echo ""
log_success "Modo: $(echo -e $MODE_NAME)"
log_info "Archivo: ${BOLD}$COMPOSE_FILE${NC}"

CURRENT_STEP="Verificación de archivo"
[ ! -f "$COMPOSE_FILE" ] && log_error "Archivo $COMPOSE_FILE no encontrado" && exit 1
log_success "Archivo encontrado"

# ============================================================================
# CONFIRMACIÓN
# ============================================================================

echo ""
read -p "$(echo -e ${YELLOW}${BOLD}"¿Proceder con la actualización? (s/n): "${NC})" confirm
echo ""

[[ ! $confirm =~ ^[SsYy]$ ]] && log_info "Cancelado" && cleanup && exit 0

# ============================================================================
# VERIFICAR REQUISITOS
# ============================================================================

CURRENT_STEP="Verificación de requisitos"

log_step "Verificando Docker..."
command -v docker &> /dev/null || { log_error "Docker no instalado"; exit 1; }
docker info &> /dev/null || { log_error "Docker no está corriendo"; exit 1; }
log_success "Docker OK"

command -v docker-compose &> /dev/null || { log_error "docker-compose no instalado"; exit 1; }
log_success "docker-compose OK"

# ============================================================================
# DETECTAR SERVICIOS
# ============================================================================

log_header "🔍 Detectando servicios"

CURRENT_STEP="Detección de servicios"

HAS_APP=false
HAS_DASHBOARD=false
HAS_POSTGRES=false
HAS_REDIS=false

service_is_defined "botv2-app" "$COMPOSE_FILE" && HAS_APP=true && log_info "botv2-app: ${GREEN}DEFINIDO${NC}"
service_is_defined "botv2-dashboard" "$COMPOSE_FILE" && HAS_DASHBOARD=true && log_info "botv2-dashboard: ${GREEN}DEFINIDO${NC}"
service_is_defined "botv2-postgres" "$COMPOSE_FILE" && HAS_POSTGRES=true && log_info "botv2-postgres: ${GREEN}DEFINIDO${NC}"
service_is_defined "botv2-redis" "$COMPOSE_FILE" && HAS_REDIS=true && log_info "botv2-redis: ${GREEN}DEFINIDO${NC}"

[ "$HAS_DASHBOARD" = false ] && log_error "Dashboard no definido" && exit 1

log_success "Servicios validados"

# ============================================================================
# BACKUP (Producción)
# ============================================================================

BACKUP_FILE=""
if [ "$MODE" = "production" ] && [ "$HAS_POSTGRES" = true ] && service_is_running "botv2-postgres" "$COMPOSE_FILE"; then
    log_header "💾 Backup"
    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="${BACKUP_DIR}/pre-update-$(date +%Y%m%d_%H%M%S).sql"
    
    if docker-compose -f "$COMPOSE_FILE" exec -T botv2-postgres pg_dump -U botv2 botv2_db > "$BACKUP_FILE" 2>/dev/null; then
        log_success "Backup: $BACKUP_FILE"
    else
        log_warning "Backup fallido"
        BACKUP_FILE=""
    fi
fi

# ============================================================================
# GIT PULL
# ============================================================================

log_header "📥 Actualizando código"

CURRENT_STEP="Git pull"
git pull origin main 2>&1 | head -5 || log_warning "Git: sin cambios o error"

# ============================================================================
# BUILD
# ============================================================================

log_header "🔨 Compilando imágenes"

CURRENT_STEP="Docker build"
BUILD_ERRORS=false

[ "$HAS_APP" = true ] && { run_docker_build "botv2-app" "$COMPOSE_FILE" || BUILD_ERRORS=true; }
echo ""
[ "$HAS_DASHBOARD" = true ] && { run_docker_build "botv2-dashboard" "$COMPOSE_FILE" || BUILD_ERRORS=true; }

if [ "$BUILD_ERRORS" = true ]; then
    log_error "Build fallido"
    show_error_banner "1" "N/A" "docker-compose build" "$CURRENT_STEP"
    cleanup
    exit 1
fi

# ============================================================================
# REINICIAR SERVICIOS
# ============================================================================

log_header "🔄 Reiniciando servicios"

CURRENT_STEP="Reinicio"

[ "$HAS_APP" = true ] && docker-compose -f "$COMPOSE_FILE" stop botv2-app 2>/dev/null && log_success "botv2-app detenida"
[ "$HAS_DASHBOARD" = true ] && docker-compose -f "$COMPOSE_FILE" stop botv2-dashboard 2>/dev/null && log_success "botv2-dashboard detenida"

echo ""
log_step "Iniciando servicios..."
echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"

CURRENT_COMMAND="docker-compose -f $COMPOSE_FILE up -d"
if docker-compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$BUILD_LOG_FILE"; then
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    log_success "Servicios iniciados"
else
    log_error "Error iniciando servicios"
    show_error_banner "$?" "N/A" "$CURRENT_COMMAND" "$CURRENT_STEP"
    cleanup
    exit 1
fi

# ============================================================================
# VERIFICACIÓN
# ============================================================================

log_header "✅ Verificación"

CURRENT_STEP="Verificación"

log_step "Esperando inicialización (20s)..."
sleep 20

log_step "Estado de contenedores:"
echo ""
docker-compose -f "$COMPOSE_FILE" ps -a
echo ""

[ "$HAS_APP" = true ] && { wait_for_healthy "botv2-app" "$COMPOSE_FILE" 60 && log_success "botv2-app: HEALTHY" || log_warning "botv2-app: verificar logs"; }
[ "$HAS_DASHBOARD" = true ] && { wait_for_healthy "botv2-dashboard" "$COMPOSE_FILE" 60 && log_success "botv2-dashboard: HEALTHY" || log_warning "botv2-dashboard: verificar logs"; }

echo ""
log_step "Verificando HTTP..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8050/health 2>/dev/null || echo "000")
[[ "$HTTP_CODE" =~ ^(200|401|302)$ ]] && log_success "Dashboard accesible (HTTP $HTTP_CODE)" || log_warning "Dashboard no responde (HTTP $HTTP_CODE)"

# ============================================================================
# RESUMEN FINAL
# ============================================================================

log_header "✨ Completado"

echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║                         ✅ ACTUALIZACIÓN EXITOSA                             ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${WHITE}${BOLD}🎯 Configuración:${NC}"
echo -e "  Modo:       $(echo -e $MODE_NAME)"
echo -e "  Directorio: ${BOLD}$PROJECT_ROOT${NC}"
echo ""
echo -e "${WHITE}${BOLD}🌐 Acceso:${NC}"
echo -e "  Dashboard: ${BOLD}http://localhost:8050${NC}"
[ "$MODE" = "demo" ] && echo -e "  Login:     ${DIM}admin / admin${NC}"
echo ""
echo -e "${WHITE}${BOLD}📋 Comandos útiles (copy-paste desde cualquier directorio):${NC}"
echo ""
echo -e "  ${GRAY}# Ir al proyecto${NC}"
echo -e "  ${DIM}cd $PROJECT_ROOT${NC}"
echo ""
echo -e "  ${GRAY}# Ver logs${NC}"
[ "$HAS_APP" = true ] && echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE logs -f botv2-app${NC}"
[ "$HAS_DASHBOARD" = true ] && echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE logs -f botv2-dashboard${NC}"
echo ""
echo -e "  ${GRAY}# Estado y control${NC}"
echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE ps -a${NC}"
echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE down${NC}"
echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE restart${NC}"
echo ""
echo -e "${GREEN}${BOLD}¡Listo! 🎉${NC}"
echo ""

cleanup
exit 0
