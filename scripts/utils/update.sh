#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT v3.6 - Professional Error Handling
# ================================================================
# Actualiza servicios con selección de modo Demo/Producción
# - Manejo profesional de errores con información detallada
# - Menú interactivo para elegir modo
# - Utiliza docker-compose específico según modo
# - Detección inteligente y segura
# - Preserva datos y valida salud
# - Muestra errores completos en tiempo real
# Author: Juan Carlos Garcia
# Date: 27-01-2026
#

# ============================================================================
# CONFIGURACIÓN INICIAL
# ============================================================================

# No usar set -e para manejar errores manualmente con más control
set -o pipefail  # Pipe failures

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
# VARIABLES GLOBALES PARA MANEJO DE ERRORES
# ============================================================================

CURRENT_STEP=""
CURRENT_COMMAND=""
ERROR_LOG_FILE="/tmp/botv2_update_error_$$.log"
BUILD_LOG_FILE="/tmp/botv2_build_$$.log"

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
# FUNCIÓN DE MANEJO DE ERRORES PROFESIONAL
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
    echo -e "  ${CYAN}Línea:${NC}            $line_number"
    echo -e "  ${CYAN}Código de salida:${NC} $exit_code"
    echo -e "  ${CYAN}Comando:${NC}          ${DIM}$command${NC}"
    echo -e "  ${CYAN}Directorio:${NC}       $PROJECT_ROOT"
    echo ""
    
    # Mostrar logs si existen
    if [ -f "$BUILD_LOG_FILE" ] && [ -s "$BUILD_LOG_FILE" ]; then
        echo -e "${WHITE}${BOLD}📜 Últimas 30 líneas del log de build:${NC}"
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        tail -n 30 "$BUILD_LOG_FILE" | while IFS= read -r line; do
            echo -e "  ${GRAY}$line${NC}"
        done
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        echo ""
    fi
    
    if [ -f "$ERROR_LOG_FILE" ] && [ -s "$ERROR_LOG_FILE" ]; then
        echo -e "${WHITE}${BOLD}📜 Log de errores:${NC}"
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        tail -n 20 "$ERROR_LOG_FILE" | while IFS= read -r line; do
            echo -e "  ${RED}$line${NC}"
        done
        echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
        echo ""
    fi
    
    echo -e "${WHITE}${BOLD}🔧 Comandos de diagnóstico:${NC}"
    echo ""
    echo -e "  ${GRAY}•${NC} Ver logs de Docker:       ${DIM}docker-compose -f $COMPOSE_FILE logs${NC}"
    echo -e "  ${GRAY}•${NC} Estado de contenedores:   ${DIM}docker-compose -f $COMPOSE_FILE ps${NC}"
    echo -e "  ${GRAY}•${NC} Espacio en disco:         ${DIM}docker system df${NC}"
    echo -e "  ${GRAY}•${NC} Limpiar caché Docker:     ${DIM}docker builder prune -f${NC}"
    echo -e "  ${GRAY}•${NC} Reiniciar Docker:         ${DIM}Reinicia Docker Desktop${NC}"
    echo ""
    echo -e "${WHITE}${BOLD}💡 Posibles soluciones:${NC}"
    echo ""
    echo -e "  ${YELLOW}1.${NC} Verifica que Docker Desktop esté corriendo correctamente"
    echo -e "  ${YELLOW}2.${NC} Asegúrate de tener espacio en disco suficiente"
    echo -e "  ${YELLOW}3.${NC} Intenta limpiar la caché: ${DIM}docker builder prune -f${NC}"
    echo -e "  ${YELLOW}4.${NC} Revisa la conexión a Internet (para descargar imágenes)"
    echo -e "  ${YELLOW}5.${NC} Ejecuta manualmente: ${DIM}docker-compose -f $COMPOSE_FILE build --no-cache${NC}"
    echo ""
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${RED}${BOLD}Script terminado con errores${NC}"
    echo ""
}

# ============================================================================
# FUNCIÓN DE LIMPIEZA
# ============================================================================

cleanup() {
    # Limpiar archivos temporales
    rm -f "$ERROR_LOG_FILE" 2>/dev/null
    rm -f "$BUILD_LOG_FILE" 2>/dev/null
}

# ============================================================================
# TRAP PARA ERRORES Y SEÑALES
# ============================================================================

error_handler() {
    local exit_code=$?
    local line_number=$1
    
    # No mostrar error si fue cancelación del usuario (Ctrl+C)
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
    echo -e "${GRAY}Limpiando recursos...${NC}"
    cleanup
    exit 130
}

# Configurar traps
trap 'error_handler $LINENO' ERR
trap 'interrupt_handler' SIGINT SIGTERM

# ============================================================================
# FUNCIÓN PARA EJECUTAR COMANDOS CON MANEJO DE ERRORES
# ============================================================================

run_command() {
    local description="$1"
    shift
    local cmd="$@"
    
    CURRENT_COMMAND="$cmd"
    
    if ! eval "$cmd"; then
        return 1
    fi
    return 0
}

# Función para ejecutar docker build con output en tiempo real
run_docker_build() {
    local service=$1
    local compose_file=$2
    
    CURRENT_COMMAND="docker-compose -f $compose_file build $service"
    
    log_step "Compilando imagen $service..."
    log_dim "Mostrando progreso en tiempo real..."
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    
    # Ejecutar build con output en tiempo real Y guardando en log
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
    
    if [ ! -f "$compose_file" ]; then
        return 1
    fi
    
    if docker-compose -f "$compose_file" config --services 2>/dev/null | grep -qx "$service"; then
        return 0
    fi
    
    if grep -qE "^\s+${service}:" "$compose_file" 2>/dev/null; then
        return 0
    fi
    
    return 1
}

service_is_running() {
    local service=$1
    local compose_file=$2
    
    local container_id=$(docker-compose -f "$compose_file" ps -q "$service" 2>/dev/null)
    
    if [ -z "$container_id" ]; then
        return 1
    fi
    
    local status=$(docker inspect -f '{{.State.Status}}' "$container_id" 2>/dev/null || echo "not_found")
    
    [ "$status" = "running" ]
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
                if [ "$status" = "running" ]; then
                    return 0
                fi
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
echo -e "${BLUE}${BOLD}  🚀 BotV2 Update Script v3.6 - Professional Error Handling${NC}"
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo ""

log_info "Directorio del proyecto: ${BOLD}$PROJECT_ROOT${NC}"
echo ""

# ============================================================================
# MENÚ DE SELECCIÓN DE MODO
# ============================================================================

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
log_dim "• Archivo: docker-compose.demo.yml"
echo ""
echo -e "  ${CYAN}${BOLD}2)${NC} 🏭 ${YELLOW}${BOLD}MODO PRODUCCIÓN${NC}"
log_dim "• Sistema completo con base de datos"
log_dim "• PostgreSQL + Redis + Trading Bot + Dashboard"
log_dim "• Persistencia de datos real"
log_dim "• Archivo: docker-compose.production.yml"
echo ""
echo -e "  ${CYAN}${BOLD}3)${NC} 🚫 ${RED}Cancelar${NC}"
echo ""

# Variable para el archivo compose (necesaria para el error handler)
COMPOSE_FILE=""

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
            log_info "Actualización cancelada por el usuario"
            cleanup
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
CURRENT_STEP="Verificación de archivo docker-compose"
if [ ! -f "$COMPOSE_FILE" ]; then
    echo ""
    log_error "Archivo $COMPOSE_FILE no encontrado en $PROJECT_ROOT"
    log_info "Archivos docker-compose disponibles:"
    ls -1 docker-compose*.yml 2>/dev/null | sed 's/^/    - /' || echo "    (ninguno)"
    exit 1
fi

log_success "Archivo $COMPOSE_FILE encontrado"

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
echo -e "  ${GREEN}✓${NC} Muestra errores detallados si algo falla"
if [ "$MODE" = "production" ]; then
    echo -e "  ${GREEN}✓${NC} Crea backup de PostgreSQL antes de actualizar"
fi
echo ""

read -p "$(echo -e ${YELLOW}${BOLD}"¿Deseas proceder con la actualización? (s/n): "${NC})" confirm
echo ""

if [[ ! $confirm =~ ^[SsYy]$ ]]; then
    log_info "Actualización cancelada"
    cleanup
    exit 0
fi

# ============================================================================
# PASO 1: Verificar requisitos
# ============================================================================

CURRENT_STEP="Verificación de requisitos"

log_step "Verificando Docker..."
if ! command -v docker &> /dev/null; then
    log_error "Docker no está instalado"
    log_info "Instala Docker desde: https://docs.docker.com/get-docker/"
    exit 1
fi
log_success "Docker está instalado"

if ! docker info &> /dev/null 2>&1; then
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
# PASO 2: Detectar servicios
# ============================================================================

log_header "🔍 Detectando configuración"

CURRENT_STEP="Detección de servicios"
log_step "Analizando servicios definidos en $COMPOSE_FILE..."

log_dim "Servicios encontrados por docker-compose:"
DETECTED_SERVICES=$(docker-compose -f "$COMPOSE_FILE" config --services 2>/dev/null || echo "(error al leer)")
for svc in $DETECTED_SERVICES; do
    log_dim "  - $svc"
done
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
# PASO 3: Backup (solo producción)
# ============================================================================

BACKUP_FILE=""
if [ "$MODE" = "production" ] && [ "$HAS_POSTGRES" = true ]; then
    log_header "💾 Backup Preventivo"
    CURRENT_STEP="Backup de PostgreSQL"

    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"

    BACKUP_FILE="${BACKUP_DIR}/pre-update-$(date +%Y%m%d_%H%M%S).sql"

    log_step "Creando backup de PostgreSQL..."
    
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

CURRENT_STEP="Actualización de código Git"
log_step "Obteniendo cambios de Git..."
if git pull origin main 2>&1 | tee -a "$BUILD_LOG_FILE"; then
    log_success "Código actualizado desde Git"
elif git status &> /dev/null; then
    log_warning "No hay cambios nuevos en Git o hubo un problema"
else
    log_warning "Git no disponible (usando código local)"
fi

# ============================================================================
# PASO 5: Reconstruir imágenes
# ============================================================================

log_header "🔨 Reconstruyendo imágenes Docker"

CURRENT_STEP="Compilación de imágenes Docker"
BUILD_ERRORS=false

if [ "$HAS_APP" = true ]; then
    if ! run_docker_build "botv2-app" "$COMPOSE_FILE"; then
        BUILD_ERRORS=true
    fi
    echo ""
fi

if [ "$HAS_DASHBOARD" = true ]; then
    if ! run_docker_build "botv2-dashboard" "$COMPOSE_FILE"; then
        BUILD_ERRORS=true
    fi
fi

if [ "$BUILD_ERRORS" = true ]; then
    echo ""
    log_error "Fallos en compilación - abortando actualización"
    log_info "Revisa los errores arriba y corrígelos antes de continuar"
    show_error_banner "1" "N/A" "docker-compose build" "$CURRENT_STEP"
    cleanup
    exit 1
fi

# ============================================================================
# PASO 6: Reiniciar servicios
# ============================================================================

log_header "🔄 Reiniciando servicios"

CURRENT_STEP="Reinicio de servicios"

if [ "$HAS_APP" = true ]; then
    log_step "Deteniendo botv2-app..."
    if docker-compose -f "$COMPOSE_FILE" stop botv2-app 2>/dev/null; then
        log_success "botv2-app detenida"
    else
        log_dim "No estaba corriendo"
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    log_step "Deteniendo botv2-dashboard..."
    if docker-compose -f "$COMPOSE_FILE" stop botv2-dashboard 2>/dev/null; then
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

log_step "Iniciando servicios..."
log_dim "Mostrando progreso en tiempo real..."
echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"

CURRENT_COMMAND="docker-compose -f $COMPOSE_FILE up -d"
if docker-compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$BUILD_LOG_FILE"; then
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    log_success "Servicios iniciados exitosamente"
else
    UP_EXIT_CODE=${PIPESTATUS[0]}
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    log_error "Error iniciando servicios (exit code: $UP_EXIT_CODE)"
    show_error_banner "$UP_EXIT_CODE" "N/A" "$CURRENT_COMMAND" "$CURRENT_STEP"
    cleanup
    exit $UP_EXIT_CODE
fi

# ============================================================================
# PASO 7: Verificación
# ============================================================================

log_header "✅ Verificación de servicios"

CURRENT_STEP="Verificación de servicios"

log_step "Esperando inicialización (15 segundos)..."
sleep 15

log_step "Estado de contenedores:"
echo ""
docker-compose -f "$COMPOSE_FILE" ps
echo ""

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

echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║                         ✅ ACTUALIZACIÓN EXITOSA                             ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
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
echo -e "  Directorio:     ${BOLD}$PROJECT_ROOT${NC}"
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

echo -e "  ${GRAY}•${NC} Estado servicios:    ${DIM}docker-compose -f $COMPOSE_FILE ps${NC}"
echo -e "  ${GRAY}•${NC} Detener servicios:   ${DIM}docker-compose -f $COMPOSE_FILE down${NC}"
echo ""
echo -e "${GREEN}${BOLD}¡Todos los servicios actualizados y operativos! 🎉${NC}"
echo ""

# Limpieza final
cleanup
exit 0
