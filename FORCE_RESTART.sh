#!/bin/bash
# ⚡ FORCE RESTART - Solución agresiva para network endpoint error
# Problema: network botv2_botv2-network has active endpoints
# Solución: Matar todos los contenedores + limpiar + reiniciar

echo "🔧 FORCE RESTART - Limpieza agresiva"
echo "====================================="
echo ""

echo "1️⃣  Parando todo de forma forzada..."
docker-compose kill

echo ""
echo "2️⃣  Removiendo contenedores..."
docker-compose rm -f

echo ""
echo "3️⃣  Limpiando redes huérfanas..."
docker network prune -f

echo ""
echo "4️⃣  Esperando 5 segundos..."
sleep 5

echo ""
echo "5️⃣  Levantando servicios de nuevo..."
docker-compose up -d

echo ""
echo "6️⃣  Verificando estado..."
docker-compose ps

echo ""
echo "✅ ¡Listo! Verifica:"
echo "   - API: http://localhost:8000"
echo "   - Dashboard: http://localhost:8050"
echo "   - PostgreSQL: localhost:5432"
echo "   - Redis: localhost:6379"
