#!/bin/bash
# 🔥 DOCKER NUCLEAR CLEAN - Solución final para network endpoint error
# Problema: network botv2_botv2-network has active endpoints (persistente)
# Solución: Limpiar Docker completamente a nivel sistema

echo "🔥 DOCKER NUCLEAR CLEAN - Limpieza completa de Docker"
echo "====================================================="
echo ""
echo "⚠️  ADVERTENCIA: Esto va a remover TODOS los contenedores botv2"
echo "    Pero los volúmenes con datos se preservarán."
echo ""
read -p "¿Continuar? (s/n): " confirm
if [[ $confirm != "s" && $confirm != "S" ]]; then
    echo "Cancelado."
    exit 0
fi

echo ""
echo "🔴 Paso 1: Detener compose..."
docker-compose down -v --remove-orphans 2>/dev/null || true

echo ""
echo "🔴 Paso 2: Esperar 3 segundos..."
sleep 3

echo ""
echo "🔴 Paso 3: Remover TODOS los contenedores botv2..."
docker ps -a | grep botv2 | awk '{print $1}' | xargs -r docker rm -f

echo ""
echo "🔴 Paso 4: Esperar 2 segundos..."
sleep 2

echo ""
echo "🔴 Paso 5: Remover la red botv2_botv2-network..."
docker network rm botv2_botv2-network 2>/dev/null || echo "  (Network no encontrada o ya removida)"

echo ""
echo "🔴 Paso 6: Limpiar volúmenes huérfanos..."
docker volume prune -f

echo ""
echo "🔴 Paso 7: Limpiar sistema completo..."
docker system prune -a --volumes -f

echo ""
echo "🟢 Paso 8: Esperar 5 segundos..."
sleep 5

echo ""
echo "🟢 Paso 9: Levantando servicios..."
docker-compose up -d

echo ""
echo "🟢 Paso 10: Verificando estado..."
docker-compose ps

echo ""
echo "✅ ¡Limpieza completada!"
echo ""
echo "Verifica:"
echo "  - API: http://localhost:8000"
echo "  - Dashboard: http://localhost:8050"
echo "  - PostgreSQL: docker-compose exec botv2-postgres psql -U botv2 -d botv2_db"
echo "  - Redis: docker-compose exec botv2-redis redis-cli"
