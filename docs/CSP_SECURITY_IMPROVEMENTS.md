# 🔒 CSP Security Improvements - Dashboard v7.4+

**Date**: January 25, 2026  
**Current Version**: 7.4  
**Status**: 🟡 **ANALYSIS & RECOMMENDATIONS**

---

## 📊 Executive Summary

### Current Security Posture: 🟡 **MODERATE**

La configuración actual de CSP (v7.4) **funciona correctamente** y permite que las librerías de export carguen sin problemas. Sin embargo, **tiene debilidades de seguridad** que deberían mejorarse para un entorno de producción enterprise.

### Vulnerabilidades Identificadas

| Directiva | Riesgo | Severidad | Impacto |
|-----------|--------|-----------|----------|
| **`'unsafe-inline'`** | Permite scripts inline sin validación | 🔴 ALTO | XSS bypass completo |
| **`'unsafe-eval'`** | Permite `eval()` y generación dinámica de código | 🟠 MEDIO | DOM-based XSS |
| **CDNs sin SRI** | Librerías externas sin verificación de integridad | 🟠 MEDIO | Supply chain attack |
| **Wildcards** | Permite todo localhost:* | 🟡 BAJO | Dev only |

---

## ⚠️ Riesgos de la Configuración Actual

### 1. `'unsafe-inline'` - **ALTO RIESGO** 🔴

#### Qué Permite

```html
<!-- Cualquier script inline ejecutará sin restricciones -->
<script>alert('XSS');</script>
<button onclick="maliciousCode()">Click me</button>
<div onload="stealData()"></div>
```

#### Por Qué Es Peligroso

- **Anula el propósito principal de CSP**: Prevenir XSS
- **Permite cualquier script inline**: Inyectado por atacante
- **Event handlers vulnerables**: `onclick`, `onerror`, etc.
- **Dificulta detección**: No se puede distinguir scripts legítimos de maliciosos

#### Estadísticas de Seguridad

- **90%+ de los XSS** se ejecutan mediante scripts inline[web:24]
- **CSP con `unsafe-inline`** es **casi inútil** contra XSS[web:28]
- **Auditorías de seguridad** marcan `unsafe-inline` como **vulnerabilidad crítica**[web:27]

---

### 2. `'unsafe-eval'` - **MEDIO RIESGO** 🟠

#### Qué Permite

```javascript
// Ejecución dinámica de código
eval(userInput);  // ✅ Permitido
new Function(userInput)();  // ✅ Permitido
setTimeout(stringCode, 1000);  // ✅ Permitido
```

#### Por Qué Es Necesario (Actualmente)

- **SheetJS requiere `eval()`** para parsear fórmulas de Excel
- **Generación dinámica de código** en procesamiento de datos complejos

#### Por Qué Es Peligroso

- **DOM-based XSS**: Si user input llega a `eval()`
- **Bypassa otras protecciones**: Puede evadir sanitización
- **Difícil de auditar**: Ejecución dinámica impredecible

#### Mitigación Actual

✅ **Tu aplicación ESTÁ PROTEGIDA** porque:
- Validación Pydantic en todos los inputs
- Sanitización con `bleach` backend
- XSS middleware activo
- **User input NUNCA llega directamente a `eval()`**

---

### 3. CDNs sin SRI - **MEDIO RIESGO** 🟠

#### Configuración Actual

```html
<!-- Sin verificación de integridad -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
```

#### Riesgos

1. **CDN comprometido**: Si el servidor del CDN es hackeado
2. **Man-in-the-Middle**: Ataque entre tu servidor y el CDN
3. **Cambios inesperados**: Actualizaciones que rompen tu app
4. **Supply chain attack**: Como el ataque Polyfill.io de 2024[web:31]

#### Ejemplo Real: Polyfill.io Attack (2024)

- **+500,000 sitios web afectados**[web:31]
- CDN confiable fue comprometido
- Script malicioso inyectado en librería legítima
- **Incluso sitios con CSP fueron vulnerables** si no usaban SRI

---

## ✅ Mejoras Recomendadas

### Roadmap de Seguridad

```
v7.4 (Actual)          v7.5 (Corto plazo)      v8.0 (Largo plazo)
   │                       │                         │
   │                       │                         │
🟡 Moderado              🟢 Bueno                   🟢 Enterprise
   │                       │                         │
   │                       │                         │
   └───────────────────────→ └─────────────────────────────────────→
    unsafe-inline           + SRI integrity          Self-hosted libs
    unsafe-eval             + Nonce-based            + Worker isolation
    No SRI                  + Report-only            + Zero-trust CSP
```

---

## 🚀 Mejora #1: Subresource Integrity (SRI)

### 🎯 Prioridad: **ALTA** | Esfuerzo: **BAJO** | Impacto: **ALTO**

### Qué Es SRI

Subresource Integrity permite al navegador **verificar que el archivo descargado coincide exactamente** con el hash esperado[web:36].

### Implementación

#### dashboard.html - ANTES (v7.4)

```html
<!-- Sin protección -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

#### dashboard.html - DESPUÉS (v7.5 - RECOMENDADO)

```html
<!-- ✅ Protección SRI completa -->
<script 
    src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"
    integrity="sha384-[HASH_GENERADO]"
    crossorigin="anonymous"></script>

<script 
    src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"
    integrity="sha384-[HASH_GENERADO]"
    crossorigin="anonymous"></script>

<script 
    src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"
    integrity="sha384-[HASH_GENERADO]"
    crossorigin="anonymous"></script>

<script 
    src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
    integrity="sha384-[HASH_GENERADO]"
    crossorigin="anonymous"></script>
```

### Cómo Generar los Hashes

#### Opción 1: Online (Más Fácil)

1. Visita: https://www.srihash.org/
2. Pega la URL del CDN
3. Copia el tag completo con `integrity`

#### Opción 2: Comando (Más Seguro)

```bash
# Descargar archivo
wget https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js

# Generar hash SHA-384
openssl dgst -sha384 -binary xlsx.full.min.js | openssl base64 -A

# Output: sha384-[TU_HASH_AQUI]
```

#### Opción 3: Script Python

```python
import hashlib
import base64
import requests

def generate_sri_hash(url):
    """Generate SRI hash for a CDN resource"""
    response = requests.get(url)
    content = response.content
    
    # Generate SHA-384 hash
    hash_obj = hashlib.sha384(content)
    hash_b64 = base64.b64encode(hash_obj.digest()).decode('utf-8')
    
    return f"sha384-{hash_b64}"

# Usage
cdns = [
    "https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js",
    "https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"
]

for url in cdns:
    integrity = generate_sri_hash(url)
    print(f'<script src="{url}"')
    print(f'        integrity="{integrity}"')
    print(f'        crossorigin="anonymous"></script>\n')
```

### Beneficios de SRI

✅ **Protección contra CDN comprometido**: El navegador bloquea archivos alterados  
✅ **Protección contra MITM**: Incluso con intercepción, hash no coincidirá  
✅ **Versionado explícito**: Actualizaciones accidentales no cargarán  
✅ **Auditoría fácil**: Puedes verificar exactamente qué versión usas  
✅ **Sin cambios en CSP**: Compatible con configuración actual  

### ⚠️ Consideraciones

- **Actualizaciones manuales**: Si actualizas la librería, debes regenerar el hash
- **Fallback**: Si el hash no coincide, la librería NO cargará (feature, not bug)
- **CORS requerido**: El CDN debe soportar `Access-Control-Allow-Origin: *`

---

## 🚀 Mejora #2: Nonce-Based Scripts

### 🎯 Prioridad: **MEDIA** | Esfuerzo: **MEDIO** | Impacto: **ALTO**

### Problema

Actualmente usamos `'unsafe-inline'` que permite **CUALQUIER** script inline.

### Solución: Nonces

Un **nonce** (number used once) es un token aleatorio único por request que autoriza scripts específicos[web:41].

### Implementación

#### Paso 1: Generar Nonce en Flask

**web_app.py**:
```python
import secrets
from flask import g

def generate_csp_nonce():
    """Generate cryptographic nonce for CSP"""
    return secrets.token_urlsafe(16)

@app.before_request
def set_csp_nonce():
    """Set nonce for each request"""
    g.csp_nonce = generate_csp_nonce()

# Update CSP configuration
csp_config = {
    'script-src': [
        "'self'",
        # ✅ REMOVE: "'unsafe-inline'",  # NO LONGER NEEDED
        "'unsafe-eval'",  # Still needed for SheetJS
        lambda: f"'nonce-{g.csp_nonce}'",  # ✅ Dynamic nonce
        "https://cdn.sheetjs.com",
        "https://cdnjs.cloudflare.com",
        # ... other CDNs
    ]
}
```

#### Paso 2: Pasar Nonce a Template

**Routes**:
```python
@app.route('/')
@login_required
def index():
    return render_template(
        'dashboard.html', 
        user=session.get('user'),
        csp_nonce=g.csp_nonce  # ✅ Pass nonce to template
    )
```

#### Paso 3: Usar Nonce en Scripts Inline

**dashboard.html**:
```html
<!-- ANTES: Sin protección -->
<script>
    const DashboardApp = { /* ... */ };
</script>

<!-- DESPUÉS: Con nonce -->
<script nonce="{{ csp_nonce }}">
    const DashboardApp = { /* ... */ };
</script>

<!-- Otros scripts inline -->
<script nonce="{{ csp_nonce }}">
    // Verification script
    console.log('Libraries loaded:', {
        XLSX: typeof XLSX !== 'undefined',
        jsPDF: typeof jspdf !== 'undefined'
    });
</script>
```

### Beneficios

✅ **Elimina `'unsafe-inline'`**: Bloquea XSS inline  
✅ **Selectivo**: Solo scripts con nonce correcto ejecutan  
✅ **Único por request**: Nonce diferente cada vez  
✅ **No afecta scripts externos**: CDNs siguen funcionando  

### Desventajas

⚠️ **Más complejo**: Requiere cambios en backend + frontend  
⚠️ **Regenerar en cada request**: No puede cachearse el HTML  
⚠️ **Event handlers**: `onclick`, `onerror` seguirán bloqueados (esto es bueno)  

---

## 🚀 Mejora #3: Self-Hosted Libraries

### 🎯 Prioridad: **BAJA** | Esfuerzo: **ALTO** | Impacto: **MUY ALTO**

### Por Qué Self-Host

**Ventajas**:
- ✅ **Control total**: Tú decides cuándo actualizar
- ✅ **Sin dependencias externas**: No hay CDN que pueda caer
- ✅ **Mejor CSP**: Puedes usar solo `'self'`
- ✅ **Offline**: Funciona sin internet
- ✅ **Más rápido**: Sin DNS lookup + SSL negotiation[web:48]
- ✅ **Privacidad**: Sin tracking del CDN

**Desventajas**:
- ⚠️ **Mantenimiento manual**: Debes actualizar librerías tú
- ⚠️ **Tamaño del repo**: Archivos grandes en Git
- ⚠️ **Bandwidth**: Tu servidor sirve los archivos

### Implementación

#### Paso 1: Descargar Librerías

```bash
cd ~/BotV2/src/dashboard/static/js/vendor

# SheetJS
wget https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js

# jsPDF
wget https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js

# jsPDF AutoTable
wget https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js

# html2canvas
wget https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js
```

#### Paso 2: Actualizar HTML

**dashboard.html**:
```html
<!-- ANTES: CDN -->
<script src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"></script>

<!-- DESPUÉS: Local -->
<script src="{{ url_for('static', filename='js/vendor/xlsx.full.min.js') }}"></script>
<script src="{{ url_for('static', filename='js/vendor/jspdf.umd.min.js') }}"></script>
<script src="{{ url_for('static', filename='js/vendor/jspdf.plugin.autotable.min.js') }}"></script>
<script src="{{ url_for('static', filename='js/vendor/html2canvas.min.js') }}"></script>
```

#### Paso 3: Actualizar CSP

**web_app.py**:
```python
csp_config = {
    'script-src': [
        "'self'",  # ✅ Solo necesitas 'self' ahora
        "'unsafe-eval'",  # Aún necesario para SheetJS
        # ✅ REMOVE: Todos los CDNs externos
    ]
}
```

### CSP Ultra-Restringido (Objetivo v8.0)

```python
csp_config = {
    'default-src': "'none'",  # Deny all by default
    'script-src': [
        "'self'",
        "'nonce-[GENERATED]'",
        # NO unsafe-inline
        # NO unsafe-eval (requeriría reemplazar SheetJS)
        # NO CDNs externos
    ],
    'style-src': [
        "'self'",
        "'nonce-[GENERATED]'"
    ],
    'img-src': "'self' data:",
    'font-src': "'self'",
    'connect-src': "'self' wss://localhost:* ws://localhost:*",
    'frame-ancestors': "'none'",
    'base-uri': "'self'",
    'form-action': "'self'"
}
```

---

## 📋 Roadmap de Implementación

### Fase 1: SRI (1-2 horas) - **RECOMENDADO INMEDIATO**

- [ ] Generar hashes SHA-384 para todas las librerías CDN
- [ ] Actualizar `dashboard.html` con atributos `integrity`
- [ ] Testing: Verificar que todas las librerías cargan
- [ ] Commit: "security: Add SRI to all CDN libraries"

**Impacto**: 🟢 **ALTO** | Esfuerzo: 🟢 **BAJO**

### Fase 2: Nonce-Based Scripts (4-8 horas)

- [ ] Implementar generación de nonce en Flask
- [ ] Actualizar CSP para usar nonces
- [ ] Identificar todos los scripts inline
- [ ] Añadir nonce a cada script inline
- [ ] Testing exhaustivo
- [ ] Commit: "security: Replace unsafe-inline with nonces"

**Impacto**: 🟢 **MUY ALTO** | Esfuerzo: 🟡 **MEDIO**

### Fase 3: Self-Hosted Libraries (1-2 días)

- [ ] Descargar todas las librerías CDN
- [ ] Crear estructura `/static/js/vendor/`
- [ ] Actualizar referencias en HTML
- [ ] Simplificar CSP (solo `'self'`)
- [ ] Testing completo offline
- [ ] Documentar proceso de actualización
- [ ] Commit: "security: Self-host all export libraries"

**Impacto**: 🟢 **MUY ALTO** | Esfuerzo: 🟠 **ALTO**

### Fase 4: Eliminar unsafe-eval (Semanas)

- [ ] Investigar alternativas a SheetJS que no requieran `eval()`
- [ ] Opción: Web Workers para aislar procesamiento
- [ ] Opción: Backend processing (Python) en lugar de JavaScript
- [ ] Refactoring completo del export system
- [ ] Testing exhaustivo

**Impacto**: 🟢 **ALTO** | Esfuerzo: 🔴 **MUY ALTO**

---

## 🔷 Comparación de Configuraciones

### Actual v7.4 - 🟡 Moderado

```python
# 🟡 Seguridad moderada - FUNCIONA pero con debilidades
csp_config = {
    'script-src': [
        "'self'",
        "'unsafe-inline'",  # 🔴 RIESGO ALTO
        "'unsafe-eval'",     # 🟠 RIESGO MEDIO
        "https://cdn.sheetjs.com",  # 🟠 Sin SRI
        "https://cdnjs.cloudflare.com"  # 🟠 Sin SRI
    ]
}
```

**Protege contra**:
- ✅ Scripts de dominios no autorizados
- ✅ Inyección de CDNs maliciosos

**NO protege contra**:
- ❌ XSS mediante scripts inline
- ❌ CDN comprometido
- ❌ Supply chain attacks

---

### Recomendado v7.5 - 🟢 Bueno

```python
# 🟢 Seguridad buena - Añade SRI + nonces
csp_config = {
    'script-src': [
        "'self'",
        lambda: f"'nonce-{g.csp_nonce}'",  # ✅ Reemplaza unsafe-inline
        "'unsafe-eval'",  # 🟠 Aún necesario
        "https://cdn.sheetjs.com",  # ✅ Con SRI
        "https://cdnjs.cloudflare.com"  # ✅ Con SRI
    ]
}
```

**HTML con SRI**:
```html
<script 
    src="https://cdn.sheetjs.com/xlsx-0.20.1/package/dist/xlsx.full.min.js"
    integrity="sha384-[HASH]"
    crossorigin="anonymous"></script>
```

**Protege contra**:
- ✅ Scripts de dominios no autorizados
- ✅ XSS mediante scripts inline (✅ **NUEVO**)
- ✅ CDN comprometido (✅ **NUEVO**)
- ✅ Supply chain attacks (✅ **NUEVO**)

**NO protege contra**:
- ❌ Vulnerabilidades en librerías (funcionalidad legítima)
- ❌ `eval()` abuse (mitigado por validación de inputs)

---

### Objetivo v8.0 - 🟢 Enterprise

```python
# 🟢 Seguridad enterprise - Self-hosted + sin unsafes
csp_config = {
    'default-src': "'none'",
    'script-src': [
        "'self'",
        lambda: f"'nonce-{g.csp_nonce}'"
        # ✅ NO unsafe-inline
        # ✅ NO unsafe-eval
        # ✅ NO CDNs externos
    ],
    'require-sri-for': "script style",  # ✅ SRI obligatorio
    'upgrade-insecure-requests': True
}
```

**Protege contra**:
- ✅ Scripts de dominios no autorizados
- ✅ XSS mediante scripts inline
- ✅ CDN comprometido
- ✅ Supply chain attacks
- ✅ Vulnerabilidades de `eval()`
- ✅ Cualquier inyección de código

---

## ❓ FAQ - Preguntas Frecuentes

### ¿Es segura la configuración actual (v7.4)?

**Respuesta corta**: Sí, **para desarrollo y uso personal**.

**Respuesta larga**: 
- ✅ **Funciona correctamente**: Todas las features operan sin problemas
- ✅ **Mejor que nada**: Mucho mejor que no tener CSP
- ✅ **Otras defensas activas**: CSRF, XSS middleware, validación Pydantic
- ⚠️ **No es enterprise-grade**: No cumple estándares estrictos (SOC2, ISO 27001)
- ⚠️ **Auditorías fallarían**: `unsafe-inline` y `unsafe-eval` se marcan como vulnerabilidades

### ¿Debo cambiar algo YA?

**Para producción personal**: **NO urgente**, pero recomendado.

**Para producción enterprise**: **SÍ, implementar SRI inmediatamente**.

**Prioridad recomendada**:
1. **Hoy**: Añadir SRI (1-2 horas, alto impacto)
2. **Esta semana**: Implementar nonces (4-8 horas)
3. **Próximo sprint**: Self-hosting (opcional, según necesidad)

### ¿Afectará el rendimiento?

**SRI**: Impacto mínimo (<1ms por archivo)[web:46]

**Nonces**: Sin impacto en rendimiento

**Self-hosting**: 
- ➕ Ligeramente más rápido (sin DNS lookup)[web:48]
- ➖ Usa tu bandwidth en lugar del CDN

### ¿Puedo mantener CDNs?

Sí, pero **SIEMPRE con SRI**. Es el mínimo aceptable para producción.

### ¿Qué pasa si no hago nada?

**Riesgos aceptados**:
- Vulnerable a XSS si hay un bug de validación
- Vulnerable a CDN comprometido
- No pasará auditorías de seguridad enterprise

**Protección existente**:
- Validación Pydantic protege contra la mayoría de XSS
- XSS middleware activo
- Uso personal (bajo riesgo de ataque dirigido)

---

## 📊 Matriz de Decisión

### ¿Cuál es la mejor opción para ti?

| Escenario | Recomendación | Prioridad |
|-----------|----------------|----------|
| **Uso personal** | v7.4 actual está bien, considera SRI | Baja |
| **Demo/MVP** | v7.5 con SRI | Media |
| **Producción startup** | v7.5 con SRI + nonces | Alta |
| **Enterprise/Regulado** | v8.0 self-hosted + zero unsafes | Crítica |
| **SOC2/ISO compliance** | v8.0 obligatorio | Crítica |

---

## 📝 Resumen Ejecutivo

### Estado Actual (v7.4)

| Aspecto | Rating | Notas |
|---------|--------|-------|
| **Funcionalidad** | 🟢 Excelente | Todo funciona correctamente |
| **Seguridad básica** | 🟢 Buena | Mejor que la mayoría de apps web |
| **Seguridad enterprise** | 🟠 Moderada | Necesita mejoras |
| **Compliance** | 🔴 Insuficiente | No cumple estándares estrictos |
| **Riesgo real** | 🟢 Bajo | Para uso personal está bien |

### Recomendaciones Priorizadas

1. **CORTO PLAZO (Esta semana)**: 🟢 **Implementar SRI**
   - Esfuerzo: 1-2 horas
   - Impacto: Alto
   - Riesgo: Ninguno
   - Beneficio: Protección contra CDN comprometido

2. **MEDIO PLAZO (Este mes)**: 🟡 **Nonce-based scripts**
   - Esfuerzo: 4-8 horas
   - Impacto: Muy alto
   - Riesgo: Bajo (requiere testing)
   - Beneficio: Elimina vulnerabilidad principal de CSP

3. **LARGO PLAZO (Opcional)**: ⚪ **Self-hosting**
   - Esfuerzo: 1-2 días
   - Impacto: Muy alto
   - Riesgo: Medio (más mantenimiento)
   - Beneficio: Control total + mejor CSP

---

## 🚀 Siguiente Paso

### Opción 1: Mantener v7.4 (Conservador)

✅ **Pros**: Sin trabajo adicional, funciona perfectamente  
❌ **Contras**: Vulnerabilidades conocidas, no enterprise-ready

**Recomendado para**: Uso personal, demos, prototipos

### Opción 2: Actualizar a v7.5 (Recomendado)

✅ **Pros**: Mejor seguridad con poco esfuerzo  
✅ **SRI**: Protección contra supply chain attacks  
✅ **Nonces**: Elimina principal vulnerabilidad  
⚠️ **Contras**: Requiere 6-10 horas de trabajo

**Recomendado para**: Producción, startups, apps serias

### Opción 3: Objetivo v8.0 (Enterprise)

✅ **Pros**: Máxima seguridad, compliance-ready  
✅ **Self-hosted**: Control total  
✅ **Zero unsafes**: CSP ideal  
⚠️ **Contras**: Mucho trabajo (semanas), más mantenimiento

**Recomendado para**: Enterprise, regulado, financiero, salud

---

## 📦 Archivos para Implementar

Si decides actualizar a v7.5, necesitarás modificar:

1. `src/dashboard/web_app.py` - CSP config + nonce generation
2. `src/dashboard/templates/dashboard.html` - Añadir SRI + nonces
3. Testing completo de todas las features de export

**¿Quieres que genere los archivos actualizados con SRI?**

---

**Document Version**: 1.0.0  
**Last Updated**: January 25, 2026  
**Status**: 🟡 Recommendations for review  
**Next Review**: After decision on implementation
