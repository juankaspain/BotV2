# 💻 Local Development Setup

## 🛠️ Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Git

---

## 🚀 Quick Start

### 1. Clonar repositorio

```bash
git clone https://github.com/juankaspain/BotV2.git
cd BotV2
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
.\venv\Scripts\activate  # Windows
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Iniciar servicios con Docker

```bash
# Solo PostgreSQL y Redis
docker compose up -d botv2-postgres botv2-redis
```

### 6. Ejecutar el Bot

```bash
python main.py
```

### 7. Ejecutar el Dashboard (en otra terminal)

```bash
python -m dashboard.web_app
```

---

## 📁 Estructura del Proyecto

```
BotV2/
├── bot/                # Trading Bot Application
│   ├── main.py         # Bot entry point
│   ├── engine/         # Trading engine
│   ├── exchanges/      # Exchange connectors
│   ├── strategies/     # Trading strategies
│   └── risk/           # Risk management
│
├── dashboard/          # Web Dashboard
│   ├── web_app.py      # Dashboard entry point
│   ├── api/            # API endpoints
│   ├── components/     # UI components
│   └── pages/          # Dashboard pages
│
├── shared/             # Shared code
├── tests/              # Test suite
├── scripts/            # Utility scripts
├── docs/               # Documentation
└── main.py             # Main entry point
```

---

## 🧪 Running Tests

```bash
# Todos los tests
pytest

# Tests del bot
pytest tests/bot/

# Tests del dashboard
pytest tests/dashboard/

# Con cobertura
pytest --cov=bot --cov=dashboard
```

---

## 🔧 Development Tips

### Hot Reload

```bash
# Dashboard con auto-reload
python -m dashboard.web_app --debug
```

### Database Access

```bash
# PostgreSQL
docker exec -it botv2-postgres psql -U botv2_user -d botv2_user

# Redis
docker exec -it botv2-redis redis-cli -a botv2_user
```

### Logs

```bash
# Ver logs del bot
tail -f logs/bot.log

# Ver logs del dashboard
tail -f logs/dashboard.log
```

---

**Fecha:** 26 Enero 2026
