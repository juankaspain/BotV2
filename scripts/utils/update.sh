#!/bin/bash
#
# 🚀 BotV2 UPDATE SCRIPT v4.0 - Professional Update with Force Rebuild
# ============================================================================
# Actualiza servicios con selección de modo Demo/Producción
# - Rebuild forzado sin caché para evitar problemas de imágenes antiguas
# - Limpieza automática de imágenes huérfanas
# - Mejor manejo de errores y diagnóstico
# - Soporte completo para Demo y Producción
#
# Author: Juan Carlos Garcia
# Date: 29-01-2026
# Version: 4.0
#
# Uso:
#   ./update.sh              # Menú interactivo
#   ./update.sh --demo       # Modo demo directo
#   ./update.sh --prod       # Modo producción directo
#   ./update.sh --clean      # Limpieza completa antes de build
#
# ============================================================================

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
MODE=""
FORCE_CLEAN=false
SCRIPT_VERSION="4.0"

# ============================================================================
# PARSEO DE ARGUMENTOS
# ============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        --demo)
            MODE="demo"
            shift
            ;;
        --prod|--production)
            MODE="production"
            shift
            ;;
        --clean|--force)
            FORCE_CLEAN=true
            shift
            ;;
        --help|-h)
            echo "BotV2 Update Script v${SCRIPT_VERSION}"
            echo ""
            echo "Uso: $0 [opciones]"
            echo ""
            echo "Opciones:"
            echo "  --demo        Modo demo (sin DB, datos mock)"
            echo "  --prod        Modo producción (PostgreSQL + Redis)"
            echo "  --clean       Limpieza completa antes de build"
            echo "  --help        Mostrar esta ayuda"
            echo ""
            exit 0
            ;;
        *)
            echo "Opción desconocida: $1"
            echo "Usa --help para ver las opciones disponibles"
            exit 1
            ;;
    esac
done

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
    echo -e "  ${GRAY}# Ver logs de los contenedores${NC}"
    echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE logs botv2-app${NC}"
    echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE logs botv2-dashboard${NC}"
    echo ""
    echo -e "  ${GRAY}# Estado de contenedores${NC}"
    echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE ps -a${NC}"
    echo ""
    echo -e "  ${GRAY}# Rebuild forzado sin caché${NC}"
    echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE build --no-cache${NC}"
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
# FUNCIONES DE DOCKER
# ============================================================================

run_docker_build() {
    local service=$1
    local compose_file=$2
    
    CURRENT_COMMAND="docker-compose -f $compose_file build --no-cache $service"
    
    log_step "Compilando imagen $service (sin caché)..."
    log_dim "Esto puede tardar varios minutos..."
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    
    # Build con --no-cache para evitar problemas de caché
    if docker-compose -f "$compose_file" build --no-cache "$service" 2>&1 | tee "$BUILD_LOG_FILE"; then
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

clean_docker_resources() {
    log_step "Limpiando recursos Docker antiguos..."
    
    # Eliminar contenedores parados
    local stopped=$(docker ps -aq -f status=exited 2>/dev/null | wc -l)
    if [ "$stopped" -gt 0 ]; then
        docker container prune -f > /dev/null 2>&1
        log_dim "Contenedores parados eliminados: $stopped"
    fi
    
    # Eliminar imágenes huérfanas (dangling)
    local dangling=$(docker images -q -f dangling=true 2>/dev/null | wc -l)
    if [ "$dangling" -gt 0 ]; then
        docker image prune -f > /dev/null 2>&1
        log_dim "Imágenes huérfanas eliminadas: $dangling"
    fi
    
    # Limpiar caché de build si se solicitó limpieza completa
    if [ "$FORCE_CLEAN" = true ]; then
        log_dim "Limpiando caché de Docker builder..."
        docker builder prune -f > /dev/null 2>&1 || true
    fi
    
    log_success "Limpieza completada"
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
    local max_wait=${3:-90}
    local waited=0
    
    log_step "Esperando healthcheck de $service (hasta ${max_wait}s)..."
    
    while [ $waited -lt $max_wait ]; do
        local container_id=$(docker-compose -f "$compose_file" ps -q "$service" 2>/dev/null)
        
        if [ -n "$container_id" ]; then
            local status=$(docker inspect -f '{{.State.Status}}' "$container_id" 2>/dev/null || echo "not_found")
            
            # Verificar si el contenedor está corriendo
            if [ "$status" = "running" ]; then
                local health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container_id" 2>/dev/null || echo "none")
                
                if [ "$health" = "healthy" ]; then
                    echo ""
                    return 0
                elif [ "$health" = "none" ]; then
                    # Sin healthcheck definido, verificar solo que está corriendo
                    echo ""
                    return 0
                fi
            elif [ "$status" = "exited" ]; then
                echo ""
                log_error "$service ha terminado inesperadamente"
                log_dim "Últimas líneas del log:"
                docker-compose -f "$compose_file" logs --tail=10 "$service" 2>/dev/null
                return 1
            fi
        fi
        
        printf "${GRAY}  Esperando... %ds${NC}\r" "$waited"
        sleep 3
        waited=$((waited + 3))
    done
    
    echo ""
    return 1
}

check_container_logs_for_errors() {
    local service=$1
    local compose_file=$2
    
    # Buscar errores comunes en los logs
    local errors=$(docker-compose -f "$compose_file" logs --tail=50 "$service" 2>/dev/null | grep -iE "(error|exception|traceback|importerror|modulenotfounderror)" | head -5)
    
    if [ -n "$errors" ]; then
        log_warning "Se detectaron posibles errores en los logs de $service:"
        echo -e "${RED}$errors${NC}"
        return 1
    fi
    return 0
}

# ============================================================================
# INICIO DEL SCRIPT
# ============================================================================

echo ""
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo -e "${BLUE}${BOLD}  🚀 BotV2 Update Script v${SCRIPT_VERSION}${NC}"
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo ""

log_info "Directorio del proyecto: ${BOLD}$PROJECT_ROOT${NC}"
[ "$FORCE_CLEAN" = true ] && log_info "Modo limpieza completa: ${BOLD}ACTIVADO${NC}"
echo ""

# ============================================================================
# MENÚ DE SELECCIÓN DE MODO (si no se especificó por argumento)
# ============================================================================

if [ -z "$MODE" ]; then
    echo -e "${BLUE}█████████████████████████████████████████████████████████████████████████████${NC}"
    echo -e "${BLUE}██${NC}                      ${WHITE}🎯 SELECCIÓN DE MODO DE OPERACIÓN${NC}                      ${BLUE}██${NC}"
    echo -e "${BLUE}█████████████████████████████████████████████████████████████████████████████${NC}"
    echo ""
    echo -e "${WHITE}Selecciona el modo:${NC}"
    echo ""
    echo -e "  ${CYAN}${BOLD}1)${NC} 🎮 ${GREEN}${BOLD}MODO DEMO${NC} - Sin BD, datos mock, inicio rápido"
    echo -e "     ${GRAY}Ideal para pruebas y desarrollo${NC}"
    echo ""
    echo -e "  ${CYAN}${BOLD}2)${NC} 🏭 ${YELLOW}${BOLD}MODO PRODUCCIÓN${NC} - PostgreSQL + Redis completo"
    echo -e "     ${GRAY}Para trading real con persistencia de datos${NC}"
    echo ""
    echo -e "  ${CYAN}${BOLD}3)${NC} 🚫 ${RED}Cancelar${NC}"
    echo ""

    while true; do
        read -p "$(echo -e ${CYAN}${BOLD}"Opción (1-3): "${NC})" choice
        
        case $choice in
            1)
                MODE="demo"
                break
                ;;
            2)
                MODE="production"
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
fi

# Configurar según el modo
if [ "$MODE" = "demo" ]; then
    MODE_NAME="${GREEN}${BOLD}DEMO${NC}"
    MODE_DISPLAY="DEMO"
    COMPOSE_FILE="docker-compose.demo.yml"
else
    MODE_NAME="${YELLOW}${BOLD}PRODUCCIÓN${NC}"
    MODE_DISPLAY="PRODUCCIÓN"
    COMPOSE_FILE="docker-compose.production.yml"
fi

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
echo -e "${WHITE}${BOLD}Se realizarán las siguientes acciones:${NC}"
echo -e "  ${CYAN}1.${NC} Actualizar código desde GitHub (git pull)"
echo -e "  ${CYAN}2.${NC} Limpiar recursos Docker antiguos"
echo -e "  ${CYAN}3.${NC} Reconstruir imágenes ${BOLD}sin caché${NC}"
echo -e "  ${CYAN}4.${NC} Reiniciar todos los servicios"
echo -e "  ${CYAN}5.${NC} Verificar estado de los contenedores"
echo ""

read -p "$(echo -e ${YELLOW}${BOLD}"¿Proceder con la actualización? (s/n): "${NC})" confirm
echo ""

[[ ! $confirm =~ ^[SsYy]$ ]] && log_info "Cancelado" && cleanup && exit 0

# ============================================================================
# VERIFICAR REQUISITOS
# ============================================================================

log_header "🔧 Verificando requisitos"

CURRENT_STEP="Verificación de requisitos"

log_step "Verificando Docker..."
command -v docker &> /dev/null || { log_error "Docker no instalado"; exit 1; }
docker info &> /dev/null || { log_error "Docker no está corriendo"; exit 1; }
log_success "Docker OK"

command -v docker-compose &> /dev/null || { log_error "docker-compose no instalado"; exit 1; }
log_success "docker-compose OK"

command -v git &> /dev/null || { log_warning "git no instalado - saltando actualización de código"; }

# ============================================================================
# GIT PULL (PRIMERO - antes de cualquier build)
# ============================================================================

log_header "📥 Actualizando código fuente"

CURRENT_STEP="Git pull"

if command -v git &> /dev/null && [ -d ".git" ]; then
    log_step "Obteniendo cambios de GitHub..."
    
    # Guardar estado actual
    CURRENT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    log_dim "Commit actual: $CURRENT_COMMIT"
    
    # Hacer pull
    if git pull origin main 2>&1 | head -10; then
        NEW_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
        if [ "$CURRENT_COMMIT" != "$NEW_COMMIT" ]; then
            log_success "Código actualizado: $CURRENT_COMMIT → $NEW_COMMIT"
        else
            log_success "Código ya está actualizado"
        fi
    else
        log_warning "Git pull falló - continuando con código local"
    fi
else
    log_warning "No es un repositorio git - saltando actualización"
fi

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

[ "$HAS_DASHBOARD" = false ] && log_error "Dashboard no definido en $COMPOSE_FILE" && exit 1

log_success "Servicios validados"

# ============================================================================
# BACKUP (Solo Producción)
# ============================================================================

BACKUP_FILE=""
if [ "$MODE" = "production" ] && [ "$HAS_POSTGRES" = true ] && service_is_running "botv2-postgres" "$COMPOSE_FILE"; then
    log_header "💾 Backup de base de datos"
    
    BACKUP_DIR="./backups"
    mkdir -p "$BACKUP_DIR"
    BACKUP_FILE="${BACKUP_DIR}/pre-update-$(date +%Y%m%d_%H%M%S).sql"
    
    log_step "Creando backup de PostgreSQL..."
    if docker-compose -f "$COMPOSE_FILE" exec -T botv2-postgres pg_dump -U botv2 botv2_db > "$BACKUP_FILE" 2>/dev/null; then
        BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log_success "Backup creado: $BACKUP_FILE ($BACKUP_SIZE)"
    else
        log_warning "Backup fallido - continuando sin backup"
        BACKUP_FILE=""
    fi
fi

# ============================================================================
# LIMPIEZA DE DOCKER
# ============================================================================

log_header "🧹 Limpieza de recursos"

CURRENT_STEP="Limpieza Docker"

# Detener servicios existentes
log_step "Deteniendo servicios existentes..."
docker-compose -f "$COMPOSE_FILE" down --remove-orphans 2>/dev/null || true
log_success "Servicios detenidos"

# Limpiar recursos
clean_docker_resources

# Si es limpieza forzada, eliminar las imágenes del proyecto
if [ "$FORCE_CLEAN" = true ]; then
    log_step "Eliminando imágenes anteriores del proyecto..."
    docker rmi botv2-app:latest botv2-dashboard:latest 2>/dev/null || true
    log_success "Imágenes anteriores eliminadas"
fi

# ============================================================================
# BUILD (SIN CACHÉ)
# ============================================================================

log_header "🔨 Compilando imágenes (sin caché)"

CURRENT_STEP="Docker build"
BUILD_ERRORS=false

# Build de botv2-app
if [ "$HAS_APP" = true ]; then
    run_docker_build "botv2-app" "$COMPOSE_FILE" || BUILD_ERRORS=true
    echo ""
fi

# Build de botv2-dashboard
if [ "$HAS_DASHBOARD" = true ]; then
    run_docker_build "botv2-dashboard" "$COMPOSE_FILE" || BUILD_ERRORS=true
fi

if [ "$BUILD_ERRORS" = true ]; then
    log_error "Error durante la compilación"
    echo ""
    echo -e "${YELLOW}${BOLD}💡 Sugerencia:${NC} Revisa los errores arriba y verifica:"
    echo -e "  • Que el Dockerfile es correcto"
    echo -e "  • Que requirements.txt no tiene dependencias rotas"
    echo -e "  • Que tienes conexión a Internet para descargar paquetes"
    echo ""
    cleanup
    exit 1
fi

log_success "Todas las imágenes compiladas correctamente"

# ============================================================================
# INICIAR SERVICIOS
# ============================================================================

log_header "🚀 Iniciando servicios"

CURRENT_STEP="Inicio de servicios"

log_step "Iniciando contenedores..."
echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"

CURRENT_COMMAND="docker-compose -f $COMPOSE_FILE up -d"
if docker-compose -f "$COMPOSE_FILE" up -d 2>&1 | tee -a "$BUILD_LOG_FILE"; then
    echo -e "${GRAY}─────────────────────────────────────────────────────────────────────────────${NC}"
    log_success "Contenedores iniciados"
else
    log_error "Error iniciando servicios"
    show_error_banner "$?" "N/A" "$CURRENT_COMMAND" "$CURRENT_STEP"
    cleanup
    exit 1
fi

# ============================================================================
# VERIFICACIÓN
# ============================================================================

log_header "✅ Verificación de servicios"

CURRENT_STEP="Verificación"

log_step "Esperando inicialización (30s)..."
sleep 30

# Mostrar estado de contenedores
log_step "Estado de contenedores:"
echo ""
docker-compose -f "$COMPOSE_FILE" ps -a
echo ""

# Verificar cada servicio
VERIFICATION_OK=true

if [ "$HAS_POSTGRES" = true ]; then
    if wait_for_healthy "botv2-postgres" "$COMPOSE_FILE" 60; then
        log_success "botv2-postgres: ${GREEN}HEALTHY${NC}"
    else
        log_warning "botv2-postgres: verificar logs"
        VERIFICATION_OK=false
    fi
fi

if [ "$HAS_REDIS" = true ]; then
    if wait_for_healthy "botv2-redis" "$COMPOSE_FILE" 30; then
        log_success "botv2-redis: ${GREEN}HEALTHY${NC}"
    else
        log_warning "botv2-redis: verificar logs"
        VERIFICATION_OK=false
    fi
fi

if [ "$HAS_APP" = true ]; then
    if wait_for_healthy "botv2-app" "$COMPOSE_FILE" 90; then
        log_success "botv2-app: ${GREEN}HEALTHY${NC}"
        check_container_logs_for_errors "botv2-app" "$COMPOSE_FILE" || VERIFICATION_OK=false
    else
        log_warning "botv2-app: verificar logs"
        check_container_logs_for_errors "botv2-app" "$COMPOSE_FILE"
        VERIFICATION_OK=false
    fi
fi

if [ "$HAS_DASHBOARD" = true ]; then
    if wait_for_healthy "botv2-dashboard" "$COMPOSE_FILE" 90; then
        log_success "botv2-dashboard: ${GREEN}HEALTHY${NC}"
        check_container_logs_for_errors "botv2-dashboard" "$COMPOSE_FILE" || VERIFICATION_OK=false
    else
        log_warning "botv2-dashboard: verificar logs"
        check_container_logs_for_errors "botv2-dashboard" "$COMPOSE_FILE"
        VERIFICATION_OK=false
    fi
fi

# Verificar HTTP del dashboard
echo ""
log_step "Verificando acceso HTTP al dashboard..."
sleep 5

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8050/health 2>/dev/null || echo "000")

if [[ "$HTTP_CODE" =~ ^(200|401|302)$ ]]; then
    log_success "Dashboard accesible: HTTP $HTTP_CODE"
else
    log_warning "Dashboard no responde correctamente (HTTP $HTTP_CODE)"
    log_dim "Puede tardar unos segundos más en estar disponible"
    VERIFICATION_OK=false
fi

# ============================================================================
# RESUMEN FINAL
# ============================================================================

if [ "$VERIFICATION_OK" = true ]; then
    log_header "✨ Actualización completada exitosamente"
    
    echo -e "${GREEN}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}${BOLD}║                         ✅ ACTUALIZACIÓN EXITOSA                             ║${NC}"
    echo -e "${GREEN}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
else
    log_header "⚠️ Actualización completada con advertencias"
    
    echo -e "${YELLOW}${BOLD}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${YELLOW}${BOLD}║                    ⚠️ COMPLETADO CON ADVERTENCIAS                            ║${NC}"
    echo -e "${YELLOW}${BOLD}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
fi

echo ""
echo -e "${WHITE}${BOLD}🎯 Configuración:${NC}"
echo -e "  Modo:       $(echo -e $MODE_NAME)"
echo -e "  Directorio: ${BOLD}$PROJECT_ROOT${NC}"
[ -n "$BACKUP_FILE" ] && echo -e "  Backup:     ${BOLD}$BACKUP_FILE${NC}"
echo ""
echo -e "${WHITE}${BOLD}🌐 Acceso:${NC}"
echo -e "  Dashboard: ${BOLD}http://localhost:8050${NC}"
if [ "$MODE" = "demo" ]; then
    echo -e "  Login:     ${DIM}admin / admin${NC}"
else
    echo -e "  Login:     ${DIM}Configurado en .env${NC}"
fi
echo ""
echo -e "${WHITE}${BOLD}📋 Comandos útiles:${NC}"
echo ""
echo -e "  ${GRAY}# Ver logs en tiempo real${NC}"
echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE logs -f --tail=50${NC}"
echo ""
echo -e "  ${GRAY}# Ver logs de un servicio específico${NC}"
[ "$HAS_APP" = true ] && echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE logs -f botv2-app${NC}"
[ "$HAS_DASHBOARD" = true ] && echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE logs -f botv2-dashboard${NC}"
echo ""
echo -e "  ${GRAY}# Estado y control${NC}"
echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE ps -a${NC}"
echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE restart${NC}"
echo -e "  ${DIM}docker-compose -f $PROJECT_ROOT/$COMPOSE_FILE down${NC}"
echo ""

if [ "$VERIFICATION_OK" = false ]; then
    echo -e "${YELLOW}${BOLD}⚠️ Revisa los logs para más detalles sobre las advertencias${NC}"
    echo ""
fi

echo -e "${GREEN}${BOLD}¡Listo! 🎉${NC}"
echo ""

cleanup
exit 0
