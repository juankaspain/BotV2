#!/bin/bash
# BotV2 - Quick Database Access Script
# Funciona en: Linux, Mac, Windows (MINGW64)
# Author: Juan Carlos Garcia
# Date: 21-01-2026

echo "🗄️  BotV2 Database Access Menu"
echo "================================"
echo ""
echo "Opciones:"
echo "  1) Conectar a PostgreSQL (SQL)"
echo "  2) Conectar a Redis (Cache)"
echo "  3) Ver estado de servicios"
echo "  4) Ver logs"
echo "  5) Backup de BBDD"
echo "  6) Restaurar BBDD desde backup"
echo ""
read -p "Selecciona opción (1-6): " option

case $option in
  1)
    echo ""
    echo "Conectando a PostgreSQL..."
    echo "Host: localhost"
    echo "Port: 5432"
    echo "User: botv2"
    echo "Password: botv2password"
    echo "Database: botv2_db"
    echo ""
    docker-compose exec botv2-postgres psql -U botv2 -d botv2_db
    ;;
  2)
    echo ""
    echo "Conectando a Redis..."
    echo "Host: localhost"
    echo "Port: 6379"
    echo ""
    docker-compose exec botv2-redis redis-cli
    ;;
  3)
    echo ""
    echo "Estado de servicios:"
    echo ""
    docker-compose ps
    echo ""
    echo "Volúmenes:"
    docker volume ls | grep botv2
    ;;
  4)
    echo ""
    echo "Logs (última hora):"
    echo ""
    echo "=== PostgreSQL ==="
    docker-compose logs --tail 20 botv2-postgres
    echo ""
    echo "=== Redis ==="
    docker-compose logs --tail 20 botv2-redis
    echo ""
    echo "=== App ==="
    docker-compose logs --tail 20 botv2-app
    ;;
  5)
    echo ""
    echo "Creando backup de PostgreSQL..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    filename="backup_${timestamp}.sql"
    docker-compose exec -T botv2-postgres pg_dump -U botv2 botv2_db > "./backups/${filename}"
    echo "✅ Backup creado: ./backups/${filename}"
    ;;
  6)
    echo ""
    echo "Archivos de backup disponibles:"
    ls -lah ./backups/ | grep -E "\.sql$"
    echo ""
    read -p "Ingresa nombre del archivo (ej: backup_20260121_030000.sql): " backup_file
    if [ -f "./backups/${backup_file}" ]; then
      echo "Restaurando desde ${backup_file}..."
      docker-compose exec -T botv2-postgres psql -U botv2 botv2_db < "./backups/${backup_file}"
      echo "✅ Restauración completada"
    else
      echo "❌ Archivo no encontrado: ./backups/${backup_file}"
    fi
    ;;
  *)
    echo "❌ Opción inválida"
    exit 1
    ;;
esac

echo ""
echo "Done! ✅"
