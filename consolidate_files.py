#!/usr/bin/env python3
"""
Consolidar archivos duplicados - Fase 1.1
Ejecuta este script desde la raíz del repositorio BotV2
"""

import shutil
import os
from pathlib import Path

def main():
    print("⚙️ Iniciando consolidación de archivos...\n")
    
    # Verificar que estamos en el directorio correcto
    if not Path('dashboard').exists():
        print("❌ Error: Ejecuta este script desde la raíz del repositorio BotV2")
        return 1
    
    # 1. Consolidar bot_controller.py
    print("🔧 1/2: Consolidando bot_controller.py")
    src = Path('dashboard/bot_controller.py')
    dst = Path('dashboard/routes/bot_controller.py')
    
    if src.exists():
        # Leer el contenido del archivo raíz
        with open(src, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Agregar demo_mode al __init__
        if "self.demo_mode" not in content:
            content = content.replace(
                "self.main_script = self.base_dir / 'src' / 'main.py'",
                """self.main_script = self.base_dir / 'src' / 'main.py'
        
        # Demo mode support
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')"""
            )
        
        # Escribir el archivo consolidado en routes/
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Consolidado: {dst}")
    else:
        print(f"  ⚠️  No se encontró: {src}")
    
    # 2. Consolidar strategy_editor.py
    print("\n🔧 2/2: Consolidando strategy_editor.py")
    src = Path('dashboard/strategy_editor.py')
    dst = Path('dashboard/routes/strategy_editor.py')
    
    if src.exists():
        # Leer el contenido del archivo raíz
        with open(src, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Agregar demo_mode al __init__
        if "self.demo_mode" not in content:
            content = content.replace(
                "self._initialized = True",
                """self._initialized = True
        
        # Demo mode support
        self.demo_mode = os.getenv('DEMO_MODE', 'false').lower() in ('true', '1', 'yes')"""
            )
        
        # Agregar demo_mode a get_statistics()
        if "'demo_mode': self.demo_mode" not in content:
            content = content.replace(
                "'history_size': len(self.change_history)",
                """'history_size': len(self.change_history),
            'demo_mode': self.demo_mode"""
            )
        
        # Escribir el archivo consolidado en routes/
        with open(dst, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Consolidado: {dst}")
    else:
        print(f"  ⚠️  No se encontró: {src}")
    
    print("\n✅ Consolidación completada!")
    print("\n📝 Próximos pasos:")
    print("1. Verifica que los archivos consolidados funcionan correctamente")
    print("2. Ejecuta los tests: python -m pytest tests/")
    print("3. Una vez verificado, elimina los duplicados con: python cleanup_duplicates.py")
    
    return 0

if __name__ == '__main__':
    exit(main())
