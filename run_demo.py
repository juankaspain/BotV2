#!/usr/bin/env python3
"""
BotV2 - Demo Mode Launcher
==========================
Script para iniciar el dashboard en modo demo de forma local.
Verifica e instala automáticamente las dependencias necesarias.

Uso:
    python run_demo.py
    python run_demo.py --install  # Fuerza instalación de dependencias
    python run_demo.py --port 8080  # Puerto personalizado

Author: Juan Carlos Garcia
Date: 30-01-2026
Version: 1.0
"""

import subprocess
import sys
import os
import argparse
from datetime import datetime
from pathlib import Path

# Colores para terminal
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    WHITE = '\033[1;37m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'
    BOLD = '\033[1m'

def log_info(msg: str) -> None:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {Colors.BLUE}[INFO]{Colors.NC} {msg}")

def log_success(msg: str) -> None:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {Colors.GREEN}[OK]{Colors.NC} {msg}")

def log_error(msg: str) -> None:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {Colors.RED}[ERROR]{Colors.NC} {msg}", file=sys.stderr)

def log_warning(msg: str) -> None:
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {Colors.YELLOW}[WARN]{Colors.NC} {msg}")

# Dependencias mínimas requeridas para modo demo
DEMO_CORE_PACKAGES = [
    'flask',
    'flask_socketio',
    'flask_cors',
    'yaml',  # PyYAML
    'dotenv',  # python-dotenv
    'psutil',
]

def check_dependencies() -> tuple[bool, list]:
    """Verifica si las dependencias core están instaladas.
    
    Returns:
        Tuple de (all_installed, missing_packages)
    """
    missing = []
    
    for package in DEMO_CORE_PACKAGES:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    return len(missing) == 0, missing

def install_demo_requirements() -> bool:
    """Instala las dependencias desde requirements-demo.txt.
    
    Returns:
        True si la instalación fue exitosa
    """
    project_root = Path(__file__).parent
    requirements_file = project_root / 'requirements-demo.txt'
    
    if not requirements_file.exists():
        # Fallback a requirements.txt
        requirements_file = project_root / 'requirements.txt'
        if not requirements_file.exists():
            log_error("No se encontró requirements-demo.txt ni requirements.txt")
            return False
        log_warning(f"Usando {requirements_file.name} como alternativa")
    
    log_info(f"Instalando dependencias desde {requirements_file.name}...")
    
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos máximo
        )
        
        if result.returncode == 0:
            log_success("Dependencias instaladas correctamente")
            return True
        else:
            log_error(f"Error instalando dependencias: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        log_error("Timeout instalando dependencias (>5 min)")
        return False
    except Exception as e:
        log_error(f"Error inesperado: {e}")
        return False

def launch_demo_dashboard(port: int = 8050) -> int:
    """Lanza el dashboard en modo demo.
    
    Args:
        port: Puerto para el servidor web
        
    Returns:
        Código de salida del proceso
    """
    project_root = Path(__file__).parent
    web_app_path = project_root / 'dashboard' / 'web_app.py'
    
    if not web_app_path.exists():
        log_error(f"No se encontró {web_app_path}")
        return 1
    
    # Configurar variables de entorno para modo demo
    env = os.environ.copy()
    env['DEMO_MODE'] = 'true'
    env['FLASK_ENV'] = 'development'
    env['DASHBOARD_PORT'] = str(port)
    env['PYTHONPATH'] = str(project_root)
    
    log_info(f"Lanzando BotV2 - Dashboard modo demo...")
    log_info(f"Puerto: {port}")
    log_info(f"URL: http://localhost:{port}")
    print()
    
    try:
        # Lanzar el dashboard
        result = subprocess.run(
            [sys.executable, str(web_app_path)],
            env=env,
            cwd=str(project_root)
        )
        return result.returncode
        
    except KeyboardInterrupt:
        log_info("Dashboard detenido por el usuario (Ctrl+C)")
        return 0
    except Exception as e:
        log_error(f"Fallo inesperado en el launcher (línea {sys.exc_info()[2].tb_lineno}, código 1).")
        log_error("Revisa el stacktrace o los mensajes anteriores para más detalle.")
        return 1

def main() -> int:
    """Punto de entrada principal."""
    
    parser = argparse.ArgumentParser(
        description='BotV2 - Demo Mode Launcher',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python run_demo.py              # Iniciar demo en puerto 8050
  python run_demo.py --port 8080  # Iniciar demo en puerto 8080
  python run_demo.py --install    # Forzar instalación de dependencias
        """
    )
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8050,
        help='Puerto para el dashboard (default: 8050)'
    )
    parser.add_argument(
        '--install', '-i',
        action='store_true',
        help='Forzar instalación de dependencias antes de iniciar'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Solo verificar dependencias sin iniciar'
    )
    
    args = parser.parse_args()
    
    # Banner
    print()
    print(f"{Colors.CYAN}{'='*70}{Colors.NC}")
    print(f"{Colors.CYAN}  🚀 BotV2 - Demo Mode Launcher{Colors.NC}")
    print(f"{Colors.CYAN}{'='*70}{Colors.NC}")
    print()
    
    # Verificar dependencias
    all_installed, missing = check_dependencies()
    
    if args.install or not all_installed:
        if missing:
            log_warning(f"Paquetes faltantes: {', '.join(missing)}")
        
        if not install_demo_requirements():
            log_error("No se pudieron instalar las dependencias")
            print()
            print(f"{Colors.YELLOW}Solución manual:{Colors.NC}")
            print(f"  pip install -r requirements-demo.txt")
            print()
            return 1
        
        # Re-verificar después de instalar
        all_installed, missing = check_dependencies()
        if not all_installed:
            log_error(f"Aún faltan paquetes después de instalar: {missing}")
            return 1
    
    if args.check_only:
        if all_installed:
            log_success("Todas las dependencias están instaladas")
            return 0
        else:
            log_error(f"Faltan dependencias: {missing}")
            return 1
    
    log_success("Dependencias verificadas")
    print()
    
    # Lanzar dashboard
    return launch_demo_dashboard(port=args.port)

if __name__ == '__main__':
    sys.exit(main())
