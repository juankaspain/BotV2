#!/usr/bin/env python3
"""
================================================================================
BotV2 Repository Reorganization Script
================================================================================
Version: 1.0.0
Author: Juan Carlos Garcia Arriero
Date: 26 Enero 2026

Purpose:
    Reorganiza la estructura del repositorio BotV2 para una arquitectura
    profesional y mantenible con dos aplicaciones principales:
    - bot/: Trading Bot Engine
    - dashboard/: Web Dashboard

Usage:
    python scripts/reorganize_repository.py [--dry-run] [--backup] [--verbose]

Options:
    --dry-run   : Muestra los cambios sin ejecutarlos
    --backup    : Crea backup antes de reorganizar (recomendado)
    --verbose   : Muestra información detallada
    --rollback  : Revierte al estado anterior (requiere backup previo)

================================================================================
"""

import os
import sys
import shutil
import json
import hashlib
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

class FileAction(Enum):
    """Tipos de acciones sobre archivos."""
    MOVE = "move"
    DELETE = "delete"
    MERGE = "merge"
    CREATE = "create"
    KEEP = "keep"

@dataclass
class ReorgConfig:
    """Configuración de la reorganización."""
    
    # Directorios raíz
    ROOT_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent)
    BACKUP_DIR: Path = field(default_factory=lambda: Path(__file__).parent.parent / ".backup_reorganization")
    
    # Estructura objetivo
    TARGET_STRUCTURE: Dict = field(default_factory=lambda: {
        "bot": {
            "__init__.py": "keep",
            "main.py": "keep",
            "engine": "keep",
            "exchanges": "keep", 
            "execution": "keep",
            "risk": "keep",
            "strategies": "keep",
            "utils": "keep"
        },
        "dashboard": {
            "__init__.py": "keep",
            "app.py": "rename:web_app.py",
            "api": "keep",
            "components": "keep",
            "pages": "keep",
            "utils": "keep",
            "static": "create",
            "templates": "create"
        },
        "shared": {
            "__init__.py": "keep",
            "config": "keep",
            "data": "keep",
            "models": "keep",
            "notifications": "keep",
            "security": "keep",
            "utils": "keep"
        },
        "tests": {
            "__init__.py": "keep",
            "conftest.py": "keep",
            "bot": "create",
            "dashboard": "create",
            "shared": "create",
            "integration": "create"
        },
        "scripts": {
            "README.md": "keep",
            "db": "create",
            "docker": "create",
            "security": "create",
            "utils": "create"
        },
        "docs": {
            "README.md": "create",
            "architecture": "create",
            "deployment": "create",
            "security": "create",
            "dashboard": "create",
            "api": "create",
            "guides": "create",
            "reference": "create"
        }
    })
    
    # Archivos a mantener en raíz
    ROOT_FILES_KEEP: List[str] = field(default_factory=lambda: [
        ".env.example",
        ".gitignore",
        ".gitattributes",
        "README.md",
        "CHANGELOG.md",
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.production.yml",
        "docker-compose.demo.yml",
        "config.yaml",
        "requirements.txt",
        "pytest.ini",
        "main.py",
        "build.py"
    ])
    
    # Mapeo de archivos a mover
    FILES_TO_MOVE: Dict[str, str] = field(default_factory=lambda: {
        # Documentación -> docs/
        "ARCHITECTURE.md": "docs/architecture/ARCHITECTURE.md",
        "AUDIT_SUMMARY.md": "docs/reference/AUDIT_SUMMARY.md",
        "CODE_REVIEW_AND_ROBUSTNESS_ASSESSMENT.md": "docs/reference/CODE_REVIEW.md",
        "CONFIRMATION_IMPLEMENTATION_STATUS.md": "docs/reference/IMPLEMENTATION_STATUS.md",
        "CONTROL_PANEL_README.md": "docs/dashboard/CONTROL_PANEL.md",
        "DASHBOARD_ACCESS.md": "docs/dashboard/ACCESS.md",
        "DASHBOARD_UPGRADE_SUMMARY.md": "docs/dashboard/UPGRADE_SUMMARY.md",
        "DOCKER_SETUP.md": "docs/deployment/DOCKER_SETUP.md",
        "DOCKER_FIX_v5.1.md": "docs/deployment/DOCKER_FIX.md",
        "FINAL_DEPLOYMENT_CHECKLIST.md": "docs/deployment/CHECKLIST.md",
        "IMPLEMENTATION_PLAN_V1_TO_V2.md": "docs/architecture/IMPLEMENTATION_PLAN.md",
        "IMPLEMENTATION_VISUAL_SUMMARY.txt": "docs/reference/VISUAL_SUMMARY.txt",
        "INTEGRATION_GUIDE_EXECUTION_ENGINE.md": "docs/guides/EXECUTION_ENGINE.md",
        "LOCAL_SETUP.md": "docs/deployment/LOCAL_SETUP.md",
        "REPOSITORY_REORGANIZATION.md": "docs/architecture/REPOSITORY_REORGANIZATION.md",
        "RESTRUCTURE_PLAN.md": "docs/architecture/RESTRUCTURE_PLAN.md",
        "RESTRUCTURE_PROGRESS.md": "docs/architecture/RESTRUCTURE_PROGRESS.md",
        "STRATEGIES_AUDIT_V1_VS_V2.md": "docs/reference/STRATEGIES_AUDIT.md",
        "STRATEGIES_COMPARISON.md": "docs/reference/STRATEGIES_COMPARISON.md",
        "STRUCTURE.md": "docs/architecture/STRUCTURE.md",
        "VERIFICACION_FINAL_SIMPLE.md": "docs/reference/VERIFICACION_FINAL.md",
        "00_START_HERE.md": "docs/guides/START_HERE.md",
        
        # Scripts -> scripts/
        "CLEANUP.sh": "scripts/docker/cleanup.sh",
        "DB_ACCESS.sh": "scripts/db/access.sh",
        "DOCKER_FIX.sh": "scripts/docker/fix.sh",
        "DOCKER_NUCLEAR_CLEAN.sh": "scripts/docker/nuclear_clean.sh",
        "FORCE_RESTART.sh": "scripts/docker/force_restart.sh",
        "UPDATE.sh": "scripts/utils/update.sh",
        "UPDATE_CONTROL.sh": "scripts/utils/update_control.sh",
        
        # Service Worker -> dashboard/static/js/
        "sw.js": "dashboard/static/js/sw.js",
        
        # SQL -> scripts/db/
        "scripts/init-db.sql": "scripts/db/init-db.sql",
        
        # Security scripts -> scripts/security/
        "scripts/integrate_security.py": "scripts/security/integrate_security.py",
        "scripts/security_integration.py": "scripts/security/security_integration.py",
        "scripts/test_security_integration.py": "scripts/security/test_security_integration.py",
        "scripts/verify_security.py": "scripts/security/verify_security.py",
        
        # Utils scripts -> scripts/utils/
        "scripts/fix_login_session.py": "scripts/utils/fix_login_session.py",
        "scripts/verify_system.sh": "scripts/utils/verify_system.sh",
    })
    
    # Archivos/directorios a eliminar (código duplicado o obsoleto)
    FILES_TO_DELETE: List[str] = field(default_factory=lambda: [
        # Directorio src/ completo (código duplicado/legacy)
        "src",
    ])
    
    # Tests a reorganizar por categoría
    TESTS_REORGANIZE: Dict[str, str] = field(default_factory=lambda: {
        "test_dashboard.py": "tests/dashboard/test_dashboard.py",
        "test_dashboard_security.py": "tests/dashboard/test_security.py",
        "test_dashboard_v4_4.py": "tests/dashboard/test_v4_4.py",
        "test_circuit_breaker.py": "tests/bot/test_circuit_breaker.py",
        "test_data_validation.py": "tests/shared/test_data_validation.py",
        "test_integration.py": "tests/integration/test_integration.py",
        "test_latency_simulator.py": "tests/bot/test_latency_simulator.py",
        "test_malicious_data.py": "tests/shared/test_malicious_data.py",
        "test_malicious_data_detector.py": "tests/shared/test_malicious_data_detector.py",
        "test_notification_system.py": "tests/shared/test_notification_system.py",
        "test_notifications.py": "tests/shared/test_notifications.py",
        "test_recovery.py": "tests/bot/test_recovery.py",
        "test_recovery_system.py": "tests/bot/test_recovery_system.py",
        "test_risk_manager.py": "tests/bot/test_risk_manager.py",
        "test_strategies.py": "tests/bot/test_strategies.py",
        "test_trailing_stops.py": "tests/bot/test_trailing_stops.py",
    })


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Configura el sistema de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # File handler
    log_file = Path(__file__).parent.parent / "logs" / "reorganization.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    logger = logging.getLogger("ReorgScript")
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# UTILITY CLASSES
# ============================================================================

@dataclass
class FileOperation:
    """Representa una operación sobre un archivo."""
    action: FileAction
    source: Path
    destination: Optional[Path] = None
    reason: str = ""
    executed: bool = False
    error: Optional[str] = None


class OperationLog:
    """Registro de operaciones para posible rollback."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.operations: List[Dict] = []
    
    def add(self, operation: FileOperation):
        """Añade una operación al log."""
        self.operations.append({
            "timestamp": datetime.now().isoformat(),
            "action": operation.action.value,
            "source": str(operation.source),
            "destination": str(operation.destination) if operation.destination else None,
            "reason": operation.reason,
            "executed": operation.executed,
            "error": operation.error
        })
    
    def save(self):
        """Guarda el log a disco."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(self.operations, f, indent=2, ensure_ascii=False)
    
    def load(self) -> List[Dict]:
        """Carga el log desde disco."""
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []


# ============================================================================
# MAIN REORGANIZER CLASS
# ============================================================================

class RepositoryReorganizer:
    """Clase principal para reorganizar el repositorio."""
    
    def __init__(self, config: ReorgConfig, logger: logging.Logger, 
                 dry_run: bool = False, create_backup: bool = True):
        self.config = config
        self.logger = logger
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.root = config.ROOT_DIR
        self.operations: List[FileOperation] = []
        self.op_log = OperationLog(self.root / "logs" / "reorganization_operations.json")
        
    def run(self) -> bool:
        """Ejecuta la reorganización completa."""
        self.logger.info("=" * 70)
        self.logger.info("BOTV2 REPOSITORY REORGANIZATION")
        self.logger.info("=" * 70)
        self.logger.info(f"Root directory: {self.root}")
        self.logger.info(f"Dry run: {self.dry_run}")
        self.logger.info(f"Create backup: {self.create_backup}")
        self.logger.info("=" * 70)
        
        try:
            # Fase 1: Análisis
            self.logger.info("\n📊 FASE 1: Análisis de estructura actual")
            self._analyze_current_structure()
            
            # Fase 2: Backup (si está habilitado)
            if self.create_backup and not self.dry_run:
                self.logger.info("\n💾 FASE 2: Creando backup")
                self._create_backup()
            
            # Fase 3: Crear estructura de directorios
            self.logger.info("\n📁 FASE 3: Creando estructura de directorios")
            self._create_directory_structure()
            
            # Fase 4: Mover archivos de documentación
            self.logger.info("\n📄 FASE 4: Moviendo documentación")
            self._move_documentation()
            
            # Fase 5: Mover scripts
            self.logger.info("\n🔧 FASE 5: Moviendo scripts")
            self._move_scripts()
            
            # Fase 6: Reorganizar tests
            self.logger.info("\n🧪 FASE 6: Reorganizando tests")
            self._reorganize_tests()
            
            # Fase 7: Mover archivos estáticos
            self.logger.info("\n🎨 FASE 7: Moviendo archivos estáticos")
            self._move_static_files()
            
            # Fase 8: Eliminar código legacy/duplicado
            self.logger.info("\n🗑️  FASE 8: Eliminando código legacy")
            self._cleanup_legacy_code()
            
            # Fase 9: Crear archivos de configuración
            self.logger.info("\n⚙️  FASE 9: Creando archivos de configuración")
            self._create_config_files()
            
            # Fase 10: Generar reporte
            self.logger.info("\n📋 FASE 10: Generando reporte")
            self._generate_report()
            
            # Guardar log de operaciones
            self.op_log.save()
            
            self.logger.info("\n" + "=" * 70)
            self.logger.info("✅ REORGANIZACIÓN COMPLETADA EXITOSAMENTE")
            self.logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error durante la reorganización: {e}")
            self.op_log.save()
            return False
    
    def _analyze_current_structure(self):
        """Analiza la estructura actual del repositorio."""
        self.logger.info("Analizando estructura actual...")
        
        # Contar archivos por tipo
        stats = {
            "md_files_root": 0,
            "sh_files_root": 0,
            "py_files_root": 0,
            "directories": 0,
            "total_files": 0
        }
        
        for item in self.root.iterdir():
            if item.is_file():
                stats["total_files"] += 1
                if item.suffix == ".md":
                    stats["md_files_root"] += 1
                elif item.suffix == ".sh":
                    stats["sh_files_root"] += 1
                elif item.suffix == ".py":
                    stats["py_files_root"] += 1
            elif item.is_dir() and not item.name.startswith('.'):
                stats["directories"] += 1
        
        self.logger.info(f"  📄 Archivos .md en raíz: {stats['md_files_root']}")
        self.logger.info(f"  📜 Archivos .sh en raíz: {stats['sh_files_root']}")
        self.logger.info(f"  🐍 Archivos .py en raíz: {stats['py_files_root']}")
        self.logger.info(f"  📁 Directorios: {stats['directories']}")
        self.logger.info(f"  📊 Total archivos en raíz: {stats['total_files']}")
    
    def _create_backup(self):
        """Crea un backup completo del repositorio."""
        backup_path = self.config.BACKUP_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.logger.info(f"  Creando backup en: {backup_path}")
        
        # Excluir directorios que no necesitan backup
        exclude_dirs = {'.git', '.backup_reorganization', '__pycache__', 
                       '.pytest_cache', 'node_modules', '.venv', 'venv'}
        
        def ignore_patterns(directory, files):
            return [f for f in files if f in exclude_dirs]
        
        shutil.copytree(self.root, backup_path, ignore=ignore_patterns)
        self.logger.info(f"  ✅ Backup creado exitosamente")
    
    def _create_directory_structure(self):
        """Crea la estructura de directorios objetivo."""
        directories_to_create = [
            # Docs subdirectories
            "docs/architecture",
            "docs/deployment", 
            "docs/security",
            "docs/dashboard",
            "docs/api",
            "docs/guides",
            "docs/reference",
            
            # Scripts subdirectories
            "scripts/db",
            "scripts/docker",
            "scripts/security",
            "scripts/utils",
            
            # Tests subdirectories
            "tests/bot",
            "tests/dashboard",
            "tests/shared",
            "tests/integration",
            
            # Dashboard subdirectories
            "dashboard/static/css",
            "dashboard/static/js",
            "dashboard/static/images",
            "dashboard/templates",
            
            # Logs directory
            "logs"
        ]
        
        for dir_path in directories_to_create:
            full_path = self.root / dir_path
            if not full_path.exists():
                if self.dry_run:
                    self.logger.info(f"  [DRY-RUN] Crearía: {dir_path}")
                else:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"  ✅ Creado: {dir_path}")
                    
                    # Crear __init__.py para directorios Python
                    if dir_path.startswith("tests/"):
                        init_file = full_path / "__init__.py"
                        if not init_file.exists():
                            init_file.write_text('"""Test package."""\n')
    
    def _move_documentation(self):
        """Mueve archivos de documentación a docs/."""
        for source, dest in self.config.FILES_TO_MOVE.items():
            if not dest.startswith("docs/"):
                continue
                
            source_path = self.root / source
            dest_path = self.root / dest
            
            if source_path.exists():
                op = FileOperation(
                    action=FileAction.MOVE,
                    source=source_path,
                    destination=dest_path,
                    reason="Organizar documentación"
                )
                self._execute_move(op)
    
    def _move_scripts(self):
        """Mueve scripts a scripts/."""
        for source, dest in self.config.FILES_TO_MOVE.items():
            if not dest.startswith("scripts/"):
                continue
                
            source_path = self.root / source
            dest_path = self.root / dest
            
            if source_path.exists():
                op = FileOperation(
                    action=FileAction.MOVE,
                    source=source_path,
                    destination=dest_path,
                    reason="Organizar scripts"
                )
                self._execute_move(op)
    
    def _reorganize_tests(self):
        """Reorganiza tests por categoría."""
        for test_file, dest in self.config.TESTS_REORGANIZE.items():
            source_path = self.root / "tests" / test_file
            dest_path = self.root / dest
            
            if source_path.exists() and source_path != dest_path:
                op = FileOperation(
                    action=FileAction.MOVE,
                    source=source_path,
                    destination=dest_path,
                    reason="Organizar tests por categoría"
                )
                self._execute_move(op)
    
    def _move_static_files(self):
        """Mueve archivos estáticos del dashboard."""
        for source, dest in self.config.FILES_TO_MOVE.items():
            if not dest.startswith("dashboard/static"):
                continue
                
            source_path = self.root / source
            dest_path = self.root / dest
            
            if source_path.exists():
                op = FileOperation(
                    action=FileAction.MOVE,
                    source=source_path,
                    destination=dest_path,
                    reason="Mover archivos estáticos"
                )
                self._execute_move(op)
    
    def _cleanup_legacy_code(self):
        """Elimina código legacy/duplicado."""
        for item in self.config.FILES_TO_DELETE:
            path = self.root / item
            
            if path.exists():
                op = FileOperation(
                    action=FileAction.DELETE,
                    source=path,
                    reason="Código legacy/duplicado"
                )
                
                if self.dry_run:
                    self.logger.info(f"  [DRY-RUN] Eliminaría: {item}")
                else:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    self.logger.info(f"  🗑️  Eliminado: {item}")
                    op.executed = True
                
                self.operations.append(op)
                self.op_log.add(op)
    
    def _create_config_files(self):
        """Crea archivos de configuración necesarios."""
        # .gitattributes para prevenir problemas de case-sensitivity
        gitattributes_content = """# Auto detect text files and perform LF normalization
* text=auto eol=lf

# Force specific file types to LF
*.py text eol=lf
*.md text eol=lf
*.yml text eol=lf
*.yaml text eol=lf
*.json text eol=lf
*.sh text eol=lf
*.sql text eol=lf
*.html text eol=lf
*.css text eol=lf
*.js text eol=lf

# Denote all files that are truly binary and should not be modified
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary
*.woff binary
*.woff2 binary
*.ttf binary
*.eot binary
"""
        
        gitattributes_path = self.root / ".gitattributes"
        if not gitattributes_path.exists():
            if self.dry_run:
                self.logger.info("  [DRY-RUN] Crearía: .gitattributes")
            else:
                gitattributes_path.write_text(gitattributes_content)
                self.logger.info("  ✅ Creado: .gitattributes")
        
        # docs/README.md - Índice de documentación
        docs_readme_content = """# 📚 BotV2 Documentation

## Directory Structure

```
docs/
├── architecture/     # System architecture and design
├── deployment/       # Deployment guides (Docker, local, production)
├── security/         # Security documentation and audits
├── dashboard/        # Dashboard features and usage
├── api/              # API reference documentation
├── guides/           # User guides and tutorials
└── reference/        # Technical reference and audits
```

## Quick Links

### Getting Started
- [Start Here](guides/START_HERE.md)
- [Local Setup](deployment/LOCAL_SETUP.md)
- [Docker Setup](deployment/DOCKER_SETUP.md)

### Architecture
- [System Architecture](architecture/ARCHITECTURE.md)
- [Project Structure](architecture/STRUCTURE.md)

### Dashboard
- [Dashboard Access](dashboard/ACCESS.md)
- [Control Panel](dashboard/CONTROL_PANEL.md)

### Deployment
- [Deployment Checklist](deployment/CHECKLIST.md)
- [Docker Troubleshooting](deployment/DOCKER_FIX.md)

---
*Documentation reorganized on {date}*
""".format(date=datetime.now().strftime("%Y-%m-%d"))
        
        docs_readme_path = self.root / "docs" / "README.md"
        if not docs_readme_path.exists():
            if self.dry_run:
                self.logger.info("  [DRY-RUN] Crearía: docs/README.md")
            else:
                docs_readme_path.write_text(docs_readme_content)
                self.logger.info("  ✅ Creado: docs/README.md")
    
    def _execute_move(self, op: FileOperation):
        """Ejecuta una operación de movimiento."""
        if self.dry_run:
            self.logger.info(f"  [DRY-RUN] Movería: {op.source.name} -> {op.destination}")
        else:
            try:
                op.destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(op.source), str(op.destination))
                self.logger.info(f"  ✅ Movido: {op.source.name} -> {op.destination.relative_to(self.root)}")
                op.executed = True
            except Exception as e:
                self.logger.error(f"  ❌ Error moviendo {op.source.name}: {e}")
                op.error = str(e)
        
        self.operations.append(op)
        self.op_log.add(op)
    
    def _generate_report(self):
        """Genera un reporte de la reorganización."""
        report_path = self.root / "logs" / f"reorganization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        executed = sum(1 for op in self.operations if op.executed)
        errors = sum(1 for op in self.operations if op.error)
        
        report_content = f"""# Repository Reorganization Report

**Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Mode:** {"Dry Run" if self.dry_run else "Production"}

## Summary

| Metric | Value |
|--------|-------|
| Total Operations | {len(self.operations)} |
| Executed | {executed} |
| Errors | {errors} |

## Operations Detail

"""
        
        for op in self.operations:
            status = "✅" if op.executed else ("❌" if op.error else "⏸️")
            report_content += f"- {status} **{op.action.value}**: `{op.source.name}`"
            if op.destination:
                report_content += f" -> `{op.destination.relative_to(self.root)}`"
            if op.error:
                report_content += f" (Error: {op.error})"
            report_content += "\n"
        
        report_content += """
## New Structure

```
BotV2/
├── bot/                    # Trading Bot Application
│   ├── engine/
│   ├── exchanges/
│   ├── execution/
│   ├── risk/
│   ├── strategies/
│   └── utils/
│
├── dashboard/              # Web Dashboard Application
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── static/
│   ├── templates/
│   └── utils/
│
├── shared/                 # Shared Code
│   ├── config/
│   ├── data/
│   ├── models/
│   ├── notifications/
│   ├── security/
│   └── utils/
│
├── tests/                  # Organized Tests
│   ├── bot/
│   ├── dashboard/
│   ├── shared/
│   └── integration/
│
├── scripts/                # Utility Scripts
│   ├── db/
│   ├── docker/
│   ├── security/
│   └── utils/
│
└── docs/                   # Documentation
    ├── architecture/
    ├── deployment/
    ├── security/
    ├── dashboard/
    ├── api/
    ├── guides/
    └── reference/
```

## Next Steps

1. Run `git status` to review changes
2. Update import statements in affected files
3. Update docker-compose volumes if needed
4. Run tests to verify functionality
5. Commit changes with descriptive message

---
*Report generated by reorganize_repository.py*
"""
        
        if not self.dry_run:
            report_path.parent.mkdir(parents=True, exist_ok=True)
            report_path.write_text(report_content)
            self.logger.info(f"  📋 Reporte guardado en: {report_path.relative_to(self.root)}")
        else:
            self.logger.info("  [DRY-RUN] Se generaría reporte de reorganización")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Punto de entrada principal."""
    parser = argparse.ArgumentParser(
        description="BotV2 Repository Reorganization Script",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python reorganize_repository.py --dry-run          # Preview changes
  python reorganize_repository.py --backup           # Create backup and execute
  python reorganize_repository.py --backup --verbose # Full execution with details
        """
    )
    
    parser.add_argument(
        "--dry-run", 
        action="store_true",
        help="Preview changes without executing"
    )
    parser.add_argument(
        "--backup",
        action="store_true", 
        help="Create backup before reorganization"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="Rollback to previous state (requires backup)"
    )
    
    args = parser.parse_args()
    
    # Setup
    logger = setup_logging(args.verbose)
    config = ReorgConfig()
    
    # Verificar que estamos en el directorio correcto
    if not (config.ROOT_DIR / "bot").exists() or not (config.ROOT_DIR / "dashboard").exists():
        logger.error("❌ Error: Este script debe ejecutarse desde la raíz del repositorio BotV2")
        sys.exit(1)
    
    # Crear reorganizador
    reorganizer = RepositoryReorganizer(
        config=config,
        logger=logger,
        dry_run=args.dry_run,
        create_backup=args.backup
    )
    
    # Ejecutar
    success = reorganizer.run()
    
    # Mostrar siguiente paso
    if args.dry_run:
        logger.info("\n💡 Para ejecutar los cambios, ejecuta sin --dry-run:")
        logger.info("   python scripts/reorganize_repository.py --backup")
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
