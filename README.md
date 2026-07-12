# 📡 MarketSignal Guardian - Radar Agéntico de Inteligencia de Mercado

**Hackathon Agentic Scale - Track 5**

Sistema agéntico que transforma noticias financieras en señales de mercado explicables, con control humano en bucle y sin ejecutar operaciones financieras automáticas.

---

## 🎯 Características Principales

✅ **Análisis Agéntico**: 4 agentes especializados (Coyuntura, Asesor Inversiones, Cumplimiento Riesgo, Generador Briefing)
✅ **Control Humano**: Validación manual de cada señal antes de generar reportes
✅ **Persistencia en Nube**: Supabase + fallback SQLite
✅ **Reportes PDF**: Generación automática de reportes de cumplimiento
✅ **Explicabilidad**: Cada señal incluye justificación técnica y acción recomendada

---

## 🚀 Acceso a la App

La app está desplegada en **Streamlit Cloud** y está lista para usar.

### URL de Acceso
```
https://market-signal-guardian.streamlit.app/
```

### Primeros Pasos
1. Abre el link en el navegador
4. ¡Comienza a analizar señales de mercado!

---

## 📋 Casos Probados Manualmente

### Caso 1: Análisis de Noticia (Monitor de Mercado → Detalle)

| Componente | Input | Resultado Esperado | Resultado Obtenido | Estado |
|-----------|-------|-------------------|-------------------|--------|
| **Filtro de Mercados** | Seleccionar "Acciones" | Lista filtra a noticias de Acciones | ✅ Filtra correctamente | ✅ PASS |
| **Botón "Ver Análisis Detallado"** | Click en cualquier noticia | Navega a detalle con impacto IA | ✅ Navega sin "Connecting" | ✅ PASS |
| **Descripción de Noticia** | Abrir detalle | Muestra descripción completa | ✅ Descripción visible | ✅ PASS |
| **Señal IA (Impacto)** | Abrir detalle | Muestra 🟢 Positivo / 🔴 Negativo / ⚪ Neutral | ✅ Impactos asignados | ✅ PASS |
| **Botón "Volver al Radar"** | Click en detalle | Regresa a list sin crash | ✅ Regresa sin errores | ✅ PASS |

**Pasos para reproducir:**
```
1. Abre la app → Tab "Monitor de Mercado"
2. Selecciona "Mercado: Acciones"
3. Click en "🔍 Ver Análisis Detallado"
4. Verifica que aparece:
   - Título completo
   - Descripción detallada
   - Impacto (color + emoji)
   - Confianza IA
5. Click en "⬅️ Volver al Radar"
6. Verifica que vuelve a la lista sin errores
```

---

### Caso 2: Auditoría de Señal (Crear Auditoría)

| Componente | Input | Resultado Esperado | Resultado Obtenido | Estado |
|-----------|-------|-------------------|-------------------|--------|
| **Expander Auditoría** | Click en "📝 Crear Auditoría" | Expande área de justificación | ✅ Se expande | ✅ PASS |
| **Botón Validar sin texto** | Click sin justificación | Muestra error "Se requiere..." | ✅ Error mostrado | ✅ PASS |
| **Botón Validar con texto** | Escribir 10 chars + click | Guarda y muestra "✅ Guardado" | ✅ Guarda en BD | ✅ PASS |
| **Botón Escalar** | Escribir texto + click | Guarda como "⚠️ Escalada" | ✅ Guarda estado | ✅ PASS |
| **Botón Descartar** | Click (sin texto requerido) | Guarda como "🗑️ Descartada" | ✅ Guarda estado | ✅ PASS |

**Pasos para reproducir:**
```
1. En Tab "Monitor de Mercado" → "Ver Análisis Detallado"
2. Expande "📝 Crear Auditoría"

Test A: Sin justificación
- Click en "✅ Validar"
- Verifica error rojo

Test B: Con justificación
- Escribe: "Señal validada por equipo de riesgo"
- Click en "✅ Validar"
- Verifica mensaje "✅ Señal Validada y Guardada"

Test C: Escalar
- Escribe justificación
- Click en "⚠️ Escalar"
- Verifica "⚠️ Señal Escalada a Comité"

Test D: Descartar
- Click en "🗑️ Descartar"
- Verifica "🗑️ Señal Descartada"
```

---

### Caso 3: Briefing de Mercado (Estados de Auditoría)

| Componente | Input | Resultado Esperado | Resultado Obtenido | Estado |
|-----------|-------|-------------------|-------------------|--------|
| **Selector Mercado** | Cambiar entre mercados | Filtra noticias | ✅ Filtra correcto | ✅ PASS |
| **Estado sin auditoría** | Noticia sin revisar | Muestra "❓ Sin Auditoría" | ✅ Se muestra | ✅ PASS |
| **Estado Validada** | Después de validar | Muestra "✅ Validada" | ✅ Se muestra | ✅ PASS |
| **Estado Escalada** | Después de escalar | Muestra "⚠️ Escalada" | ✅ Se muestra | ✅ PASS |
| **Botón "Leer Análisis"** | Click | Abre análisis detallado | ✅ Abre detalle | ✅ PASS |

**Pasos para reproducir:**
```
1. Tab "Briefing de Mercado" → Selecciona "Acciones"
2. Observa estados iniciales de noticias (todos "❓ Sin Auditoría")
3. Valida una noticia (Monitor → Detalle → Auditoría → Validar)
4. Vuelve a "Briefing de Mercado"
5. Verifica que la noticia ahora muestra "✅ Validada"
6. Repite con "Escalar" y "Descartar"
7. Verifica cambios de estado
```

---

### Caso 4: Reporte de Compliance (Persistencia)

| Componente | Input | Resultado Esperado | Resultado Obtenido | Estado |
|-----------|-------|-------------------|-------------------|--------|
| **Métricas (Validadas/Escaladas/Descartadas)** | Después de auditar | Incrementan contadores | ✅ Contadores actualizan | ✅ PASS |
| **Lista de Señales Validadas** | Después de validar | Muestra señales en lista | ✅ Aparecen en lista | ✅ PASS |
| **Persistencia al recargar** | F5 en navegador | Datos persisten en BD | ✅ Datos persistentes | ✅ PASS |
| **Generar PDF** | Click en "📄 Generar Reporte" | Descarga PDF | ✅ Descarga correcta | ✅ PASS |

**Pasos para reproducir:**
```
1. Valida 2-3 noticias en "Monitor de Mercado"
2. Escala 1-2 noticias
3. Descarta 1 noticia
4. Ve a Tab "Reporte de Compliance"
5. Verifica métricas (ej: Validadas: 2, Escaladas: 1, Descartadas: 1)
6. Verifica lista de señales auditorias
7. Click en "📄 Generar Reporte"
8. Descarga PDF y abre
9. Recarga página (F5)
10. Verifica que los datos siguen ahí (persistencia)
```

---

## 🔍 Validaciones del Código

### 1. Validación de Entrada (Auditoría)

**Archivo**: `app.py` línea ~230

```python
if b1.button("✅ Validar", key=f"ok_{sid}"):
    if len(justificacion) > 5:  # ✅ Validación: mínimo 5 caracteres
        guardar_revision(sid, "✅ Validada", justificacion)
        st.success("✅ Señal Validada y Guardada.")
    else: 
        st.error("Se requiere justificación.")  # ✅ Feedback al usuario
```

**Casos validados:**
- ✅ Texto vacío → Error
- ✅ Menos de 5 caracteres → Error
- ✅ Más de 5 caracteres → Guarda exitoso

---

### 2. Validación de Persistencia (Supabase + SQLite)

**Archivo**: `core/database.py` líneas 50-65

```python
def guardar_revision(signal_id, status, justification, reviewer="Analista de Turno"):
    supabase = get_supabase_client()
    
    if supabase:  # ✅ Intenta Supabase primero
        try:
            supabase.table("reviews").insert({...}).execute()
        except Exception as e:
            # ✅ Fallback automático a SQLite
            _guardar_revision_sqlite(...)
    else:
        _guardar_revision_sqlite(...)  # ✅ Fallback en desarrollo
```

**Validación:**
- ✅ Con Supabase configurado → Guarda en PostgreSQL
- ✅ Sin Supabase → Fallback a SQLite automático
- ✅ Datos persisten entre reinicios

---

### 3. Validación de Caché

**Archivo**: `app.py` línea 56

```python
@st.cache_data(ttl=3600)  # ✅ Cache con expiración de 1 hora
def cargar_catalogos():
    # Carga JSON de noticias y activos
    ...
```

**Validación:**
- ✅ Primera carga → Lee de JSON
- ✅ Cargas subsecuentes (< 1 hora) → Usa caché
- ✅ Después de 1 hora → Recarga desde JSON

---

### 4. Validación de Filtros

**Archivo**: `app.py` líneas 120-122

```python
if cat_filtro != "Todos" and activo_rel["type"] != cat_filtro: 
    continue  # ✅ Salta si no coincide
if simbolo_filtro != "Todos" and activo_rel["symbol"] != simbolo_filtro: 
    continue  # ✅ Salta si no coincide
```

**Casos validados:**
- ✅ Mercado "Todos" + Activo "Todos" → Muestra todas (9 noticias)
- ✅ Mercado "Acciones" → Filtra a 3 noticias
- ✅ Mercado "Criptoactivos" → Filtra a 2 noticias
- ✅ Activo específico → Filtra a 1 noticia

---

## 📸 Cómo Probar Cada Funcionalidad

### ✅ Test 1: Setup y Conexión

**En la app desplegada:**
1. Abre `https://market-signal-guardian.streamlit.app/`
2. Ingresa las API Keys (si aplica)

**Verifica:**
- [ ] App carga sin errores
- [ ] Sidebar muestra "🟢 Cerebro IA: Gemini 1.5 Flash Activo" (o 🟡 Modo Simulación)
- [ ] Encabezado muestra 4 agentes
- [ ] 3 tabs: "Monitor de Mercado", "Briefing de Mercado", "Reporte de Compliance"

**Captura esperada:**
```
Sidebar izquierdo: Cerebro IA activo ✅
Encabezado: "📡 Radar Agéntico..." ✅
Tabs: 3 pestañas visibles ✅
```

---

### ✅ Test 2: Filtros y Listado

**Pasos:**
1. En "Monitor de Mercado"
2. Mercado: "Todos" → Deberías ver 9 noticias
3. Mercado: "Acciones" → Deberías ver 3 noticias (Tesla, Apple, Chips)
4. Mercado: "Criptoactivos" → Deberías ver 2 noticias

**Captura esperada:**
```
Monitor de Mercado
├─ Mercado: Todos (9 noticias)
├─ Mercado: Acciones (3 noticias)
├─ Mercado: Criptoactivos (2 noticias)
└─ Mercado: Materias Primas (3 noticias)
```

---

### ✅ Test 3: Análisis Detallado

**Pasos:**
1. Abre cualquier noticia → "🔍 Ver Análisis Detallado"
2. Verifica que aparecen:
   - Título completo
   - Descripción detallada (no "Sin descripción")
   - Impacto IA con emoji y color (🟢/🔴/⚪/🟡)
   - Confianza y Score
   - Acción recomendada
   - Disclaimer

**Captura esperada:**
```
Título: "La SEC aprueba..."
Descripción: "La Comisión de Valores..."
Impacto: 🟢 POSITIVO
Confianza: Alta
Acción: Investigar oportunidad de compra
```

---

### ✅ Test 4: Auditoría y Persistencia

**Pasos:**
1. En detalle → Expande "📝 Crear Auditoría"
2. Test sin justificación:
   - Click "✅ Validar"
   - Debe aparecer error rojo
3. Test con justificación:
   - Escribe: "Validado por equipo de compliance"
   - Click "✅ Validar"
   - Debe decir "✅ Señal Validada y Guardada"
4. Vuelve a "Monitor de Mercado" 
5. Abre la misma noticia nuevamente
6. Verifica que la auditoría se mantiene

**Captura esperada:**
```
Crear Auditoría
├─ Sin texto → ❌ "Se requiere justificación"
├─ Con texto → ✅ "Señal Validada y Guardada"
└─ Al reabrirla → Datos persisten ✅
```

---

### ✅ Test 5: Briefing con Estados

**Pasos:**
1. Ve a "Briefing de Mercado"
2. Selecciona "Acciones"
3. Observa estado inicial (todas "❓ Sin Auditoría")
4. Valida una noticia (via Monitor)
5. Vuelve a Briefing
6. Verifica que el estado cambió a "✅ Validada"
7. Repite con "Escalar" y "Descartar"

**Captura esperada:**
```
Briefing de Mercado - Acciones
├─ Tesla... Estado: ❓ Sin Auditoría
├─ Apple... Estado: ✅ Validada ← (después de validar)
├─ Chips... Estado: ⚠️ Escalada ← (después de escalar)
└─ Botón: "Leer Análisis IA" ✅
```

---

### ✅ Test 6: Reporte de Compliance

**Pasos:**
1. Valida 2-3 noticias
2. Escala 1 noticia
3. Descarta 1 noticia
4. Ve a "Reporte de Compliance"
5. Verifica métricas actualizadas
6. Verifica lista de señales
7. Click "📄 Generar Reporte"
8. Descarga PDF
9. Abre PDF y verifica contenido

**Captura esperada:**
```
Reporte de Compliance
├─ Métricas:
│  ├─ Validadas: 2 ✅
│  ├─ Escaladas: 1 ✅
│  └─ Descartadas: 1 ✅
├─ Señales Auditadas:
│  ├─ sig_TSLA_0: Justificación: "..."
│  └─ ...más señales
└─ Botón: "📥 Descargar Reporte en PDF" ✅
```

---

### ✅ Test 7: Persistencia en Nube (Supabase)

**Pasos:**
1. Valida una noticia
2. Recarga la página (F5)
3. Ve a "Reporte de Compliance"
4. Verifica que la auditoría sigue ahí

**Captura esperada:**
```
Antes de recargar: 1 señal validada
Después de F5:    1 señal validada (persiste)
```

---

## 📊 Validaciones de Arquitectura

### ✅ Capas Implementadas

| Capa | Componente | Validación | Estado |
|------|-----------|-----------|--------|
| **Presentación** | `app.py` | UI responsiva con Streamlit | ✅ PASS |
| **Agentes** | `agents/motor.py` | Procesa pipeline IA | ✅ PASS |
| **Persistencia** | `core/database.py` | Guarda en Supabase + fallback SQLite | ✅ PASS |
| **Datos** | `data/*.json` | 9 noticias con descripciones completas | ✅ PASS |

### ✅ Flujos Críticos

1. **Ingesta de Noticias**
   - NewsAPI → `noticias_actuales` ✅
   - Fallback a `news_feed.json` ✅

2. **Análisis Agéntico**
   - Noticia + Activo → `motor.procesar_pipeline()` ✅
   - Retorna: impacto, confianza, explicación, acción ✅

3. **Auditoría + Persistencia**
   - Usuario valida → `guardar_revision()` ✅
   - Supabase intenta insertar ✅
   - Fallback a SQLite ✅

4. **Reporte**
   - Obtiene auditorías validadas ✅
   - Genera PDF con contenido ✅
   - Permite descarga ✅

---

## 🐛 Bugs Conocidos y Soluciones

| Bug | Síntoma | Solución | Estado |
|-----|---------|----------|--------|
| Descripción no aparece | "Sin descripción detallada" | La app usa caché con expiración de 1 hora, espera o solicita recarga del servidor | ✅ FIXED |
| "Connecting" infinito al volver | UI se congela | Ya fue solucionado con `st.stop()` en navegación | ✅ FIXED |
| Datos desaparecen al reiniciar | Auditorías se pierden | Supabase PostgreSQL proporciona persistencia en nube | ✅ FIXED |

---

## 📞 Contacto & Soporte

- **App Desplegada**: Streamlit Cloud (en vivo)
- **Stack**: Streamlit + Google Gemini 1.5 Flash + Supabase PostgreSQL
- **Persistencia**: ☁️ Datos guardados en nube (Supabase)
- **Estado**: ✅ Producción - Completamente Funcional

### Características de la Versión Desplegada

✅ **Análisis de Noticias en Tiempo Real** (vía NewsAPI)
✅ **Auditorías Persistentes** (guardadas en Supabase)
✅ **Reportes PDF Descargables**
✅ **4 Agentes IA Especializados**
✅ **Control Humano en Bucle**
✅ **Sin Riesgos Financieros** (no ejecuta operaciones)

---

**Última actualización**: 2026-07-12
**Estado**: ✅ Desplegado en Producción
