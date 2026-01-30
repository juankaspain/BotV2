#!/usr/bin/env bash
# =======================================================================================
# BotV2 Runtime Launcher
# - Levanta BOT en modo paper
# - Levanta Dashboard en modo demo
# - O ambos a la vez
# Pensado para desarrollo rápido local (sin Docker), con logs en tiempo real.
# =======================================================================================

set -Eeo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# ------------------------- CONFIGURACIÓN DE COMANDOS ----------------------------------

# Comando para el BOT en modo paper (ajusta flags si tu main lo requiere)
BOT_CMD=("python" "bot/main.py" "--mode" "paper")

# Comando para el Dashboard en modo demo (usa el __main__ de web_app.py)
DASHBOARD_CMD=("python" "dashboard/web_app.py")

# Nombre legible para logs
BOT_NAME="BotV2 - Bot modo paper"
DASHBOARD_NAME="BotV2 - Dashboard modo demo"

# --------------------------- VIRTUALENV OPCIONAL --------------------------------------

activate_venv() {
  if [[ -d "${PROJECT_ROOT}/.venv" ]]; then
    # shellcheck disable=SC1091
    source "${PROJECT_ROOT}/.venv/bin/activate"
  elif [[ -d "${PROJECT_ROOT}/venv" ]]; then
    # shellcheck disable=SC1091
    source "${PROJECT_ROOT}/venv/bin/activate"
  fi
}

# ---------------------------- UTILIDADES DE LOG ---------------------------------------

log() {
  local level="$1"; shift
  local msg="$*"
  local ts
  ts="$(date +"%Y-%m-%d %H:%M:%S")"
  echo "[$ts] [$level] $msg"
}

log_info()  { log "INFO"  "$*"; }
log_warn()  { log "WARN"  "$*"; }
log_error() { log "ERROR" "$*"; }

# ---------------------------- GESTIÓN DE ERRORES --------------------------------------

on_error() {
  local exit_code=$?
  local line_no=$1
  log_error "Fallo inesperado en el launcher (línea ${line_no}, código ${exit_code})."
  log_error "Revisa el stacktrace o los mensajes anteriores para más detalle."
  exit "${exit_code}"
}
trap 'on_error ${LINENO}' ERR

# ------------------------- LANZADORES INDIVIDUALES ------------------------------------

start_bot() {
  log_info "Lanzando ${BOT_NAME}..."
  cd "${PROJECT_ROOT}" || exit 1
  activate_venv
  "${BOT_CMD[@]}"
}

start_dashboard() {
  log_info "Lanzando ${DASHBOARD_NAME}..."
  cd "${PROJECT_ROOT}" || exit 1
  activate_venv
  "${DASHBOARD_CMD[@]}"
}

start_both() {
  log_info "Lanzando ${BOT_NAME} + ${DASHBOARD_NAME}..."

  cd "${PROJECT_ROOT}" || exit 1
  activate_venv

  {
    log_info "[BOT] Proceso iniciado."
    "${BOT_CMD[@]}"
    log_warn "[BOT] Proceso finalizado."
  } 2>&1 &

  BOT_PID=$!
  log_info "[BOT] PID = ${BOT_PID}"

  {
    log_info "[DASHBOARD] Proceso iniciado."
    "${DASHBOARD_CMD[@]}"
    log_warn "[DASHBOARD] Proceso finalizado."
  } 2>&1 &

  DASHBOARD_PID=$!
  log_info "[DASHBOARD] PID = ${DASHBOARD_PID}"

  log_info "Ambos servicios están levantados."
  log_info "Para detenerlos manualmente puedes usar:"
  log_info "  kill ${BOT_PID} ${DASHBOARD_PID}"
  log_info "o Ctrl+C si estás en esta misma sesión."

  wait "${BOT_PID}" "${DASHBOARD_PID}"
}

# ------------------------------ MENÚ INTERACTIVO --------------------------------------

show_menu() {
  clear
  echo "==================================================================================="
  echo "  BotV2 Runtime Launcher - Bot paper / Dashboard demo"
  echo "==================================================================================="
  echo "  1) Levantar solo BOT en modo paper"
  echo "  2) Levantar solo DASHBOARD en modo demo"
  echo "  3) Levantar BOT (paper) + DASHBOARD demo"
  echo "  4) Salir"
  echo "-----------------------------------------------------------------------------------"
}

main() {
  cd "${PROJECT_ROOT}" || exit 1

  while true; do
    show_menu
    read -r -p "Selecciona una opción [1-4]: " opt

    case "${opt}" in
      1)
        start_bot
        break
        ;;
      2)
        start_dashboard
        b
