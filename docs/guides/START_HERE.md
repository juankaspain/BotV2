# 🚀 START HERE - BotV2 Quick Start Guide

## Overview

BotV2 es un sistema de trading automatizado con las siguientes aplicaciones:

| App | Descripción | Puerto |
|-----|-------------|--------|
| **bot/** | Trading Bot Engine | - (proceso) |
| **dashboard/** | Web Dashboard | 8050 |

---

## 🎯 Quick Start (5 minutos)

### 1. Clonar repositorio

```bash
git clone https://github.com/juankaspain/BotV2.git
cd BotV2
```

### 2. Configurar entorno

```bash
cp .env.example .env
# Editar .env con tus API keys
```

### 3. Iniciar con Docker

```bash
docker compose up -d
```

### 4. Acceder al Dashboard

- URL: http://localhost:8050
- Usuario: admin
- Password: (definido en .env)

---

## 📁 Estructura del Proyecto

```
BotV2/
├── bot/                # Trading Bot Application
├── dashboard/          # Web Dashboard Application  
├── shared/             # Código compartido
├── tests/              # Tests organizados
├── scripts/            # Scripts de utilidad
├── docs/               # Documentación
└── main.py             # Entry point principal
```

---

## 📚 Documentación Adicional

- [Docker Setup](../deployment/DOCKER_SETUP.md)
- [Arquitectura](../architecture/ARCHITECTURE.md)
- [Dashboard Access](../dashboard/ACCESS.md)

---

**Fecha:** 26 Enero 2026
