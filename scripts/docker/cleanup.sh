#!/bin/bash
#
# 🧹 BotV2 CLEANUP SCRIPT
# ================================================================
# Limpia contenedores, redes y recursos de Docker para BotV2
# Ejecuta esto si tienes problemas de red o conflictos
# Author: Juan Carlos Garcia
# Date: 22-01-2026
#

set -e  # Exit on error

# ============================================================================
# COLORES
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

# ============================================================================
# BANNER
# ============================================================================

echo ""
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo -e "${BLUE}${BOLD}  🧹 BotV2 Cleanup Script - Fix Network Conflicts${NC}"
echo -e "${BLUE}${BOLD}================================================================================${NC}"
echo ""

echo -e "${WHITE}Este script limpiará:${NC}"
echo -e "  ${YELLOW}•${NC} Contenedores BotV2 (demo y producción)"
echo -e "  ${YELLOW}•${NC} Redes Docker conflictivas"
echo -e "  ${YELLOW}•${NC} Volúmenes no usados (opcional)"
echo -e "  ${YELLOW}•${NC} Imágenes dangling (opcional)"
echo ""

log_warning "${BOLD}IMPORTANTE:${NC}"
log_dim "Los volúmenes con datos (PostgreSQL) se preservarán por defecto"
log_dim "Solo se eliminarán si eliges la opción de limpieza completa"
echo ""

read -p "$(echo -e ${YELLOW}${BOLD}"¿Deseas continuar? (s/n): "${NC})" confirm
echo ""

if [[ ! $confirm =~ ^[SsYy]$ ]]; then
    log_error "Limpieza cancelada"
    exit 0
fi

# ============================================================================
# PASO 1: Detener contenedores BotV2
# ============================================================================

log_header "🛑 Deteniendo contenedores BotV2"

# Detener modo demo
if [ -f "docker-compose.demo.yml" ]; then
    log_step "Deteniendo servicios en modo DEMO..."
    if docker-compose -f docker-compose.demo.yml down 2>/dev/null; then
        log_success "Servicios demo detenidos"
    else
        log_dim "No había servicios demo corriendo"
    fi
fi

# Detener modo producción
if [ -f "docker-compose.production.yml" ]; then
    log_step "Deteniendo servicios en modo PRODUCCIÓN..."
    if docker-compose -f docker-compose.production.yml down 2>/dev/null; then
        log_success "Servicios producción detenidos"
    else
        log_dim "No había servicios producción corriendo"
    fi
fi

# Detener contenedores individuales por si acaso
log_step "Verificando contenedores individuales..."

for container in botv2-app botv2-dashboard botv2-postgres botv2-redis; do
    if docker ps -a --format '{{.Names}}' | grep -q "^${container}$"; then
        log_step "Deteniendo y eliminando $container..."
        docker stop "$container" 2>/dev/null || true
        docker rm "$container" 2>/dev/null || true
        log_success "$container eliminado"
    fi
done

log_success "Todos los contenedores BotV2 detenidos"

# ============================================================================
# PASO 2: Eliminar redes conflictivas
# ============================================================================

log_header "🌐 Eliminando redes conflictivas"

log_step "Buscando redes BotV2..."

# Listar redes que contengan "botv2"
BOTV2_NETWORKS=$(docker network ls --format '{{.Name}}' | grep -i botv2 || true)

if [ -z "$BOTV2_NETWORKS" ]; then
    log_info "No se encontraron redes BotV2"
else
    echo -e "${GRAY}Redes encontradas:${NC}"
    echo "$BOTV2_NETWORKS" | sed 's/^/  - /'
    echo ""
    
    log_step "Eliminando redes..."
    while IFS= read -r network; do
        if [ -n "$network" ]; then
            log_step "Eliminando red: $network"
            if docker network rm "$network" 2>/dev/null; then
                log_success "Red $network eliminada"
            else
                log_warning "No se pudo eliminar $network (puede tener endpoints activos)"
            fi
        fi
    done <<< "$BOTV2_NETWORKS"
fi

# Limpiar redes no usadas
log_step "Limpiando redes no usadas..."
if docker network prune -f &> /dev/null; then
    log_success "Redes no usadas eliminadas"
fi

# ============================================================================
# PASO 3: Limpiar recursos adicionales (OPCIONAL)
# ============================================================================

log_header "🗑️ Limpieza adicional (opcional)"

echo -e "${WHITE}¿Deseas realizar limpieza adicional?${NC}"
echo ""
echo -e "  ${CYAN}1)${NC} ${GREEN}Sí${NC} - Limpiar imágenes dangling y contenedores detenidos"
echo -e "  ${CYAN}2)${NC} ${YELLOW}Sí (completa)${NC} - Incluir volúmenes no usados ${RED}(eliminará datos)${NC}"
echo -e "  ${CYAN}3)${NC} ${BLUE}No${NC} - Solo lo que ya se hizo"
echo ""

read -p "$(echo -e ${CYAN}${BOLD}"Elige una opción (1-3): "${NC})" cleanup_choice
echo ""

case $cleanup_choice in
    1)
        log_step "Limpiando contenedores detenidos..."
        docker container prune -f &> /dev/null
        log_success "Contenedores detenidos eliminados"
        
        log_step "Limpiando imágenes dangling..."
        docker image prune -f &> /dev/null
        log_success "Imágenes dangling eliminadas"
        ;;
    2)
        log_warning "${BOLD}¡ADVERTENCIA!${NC} Esto eliminará volúmenes con datos de PostgreSQL"
        read -p "$(echo -e ${RED}${BOLD}"¿Estás seguro? (escribe 'SI' para confirmar): "${NC})" confirm_volumes
        
        if [ "$confirm_volumes" = "SI" ]; then
            log_step "Limpiando contenedores detenidos..."
            docker container prune -f &> /dev/null
            log_success "Contenedores detenidos eliminados"
            
            log_step "Limpiando imágenes dangling..."
            docker image prune -f &> /dev/null
            log_success "Imágenes dangling eliminadas"
            
            log_step "Limpiando volúmenes no usados..."
            docker volume prune -f &> /dev/null
            log_success "Volúmenes no usados eliminados"
        else
            log_info "Limpieza de volúmenes cancelada"
        fi
        ;;
    3)
        log_info "Limpieza adicional omitida"
        ;;
    *)
        log_warning "Opción inválida, omitiendo limpieza adicional"
        ;;
esac

# ============================================================================
# PASO 4: Verificación final
# ============================================================================

log_header "✅ Verificación final"

log_step "Estado actual de Docker..."
echo ""

echo -e "${WHITE}Contenedores BotV2 activos:${NC}"
BOTV2_CONTAINERS=$(docker ps --format '{{.Names}}' | grep -i botv2 || true)
if [ -z "$BOTV2_CONTAINERS" ]; then
    log_success "Ninguno (correcto)"
else
    echo -e "${RED}$BOTV2_CONTAINERS${NC}"
    log_warning "Aún hay contenedores activos"
fi

echo ""
echo -e "${WHITE}Redes BotV2:${NC}"
BOTV2_NETWORKS_FINAL=$(docker network ls --format '{{.Name}}' | grep -i botv2 || true)
if [ -z "$BOTV2_NETWORKS_FINAL" ]; then
    log_success "Ninguna (correcto)"
else
    echo -e "${YELLOW}$BOTV2_NETWORKS_FINAL${NC}"
    log_warning "Aún hay redes BotV2"
fi

echo ""
log_success "${GREEN}${BOLD}Limpieza completada${NC}"
echo ""

log_info "${WHITE}${BOLD}Siguiente paso:${NC}"
echo -e "  ${CYAN}→${NC} Ejecuta ${BOLD}bash UPDATE.sh${NC} para actualizar y levantar los servicios"
echo ""
