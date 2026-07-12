# Test Suite - MarketSignal Guardian

Suite de pruebas automatizadas para validar la app agéntica.

## Estructura

```
test/
├── conftest.py              # Fixtures compartidas de pytest
├── test_agent.py            # Tests del motor agéntico (CRÍTICO)
├── test_database.py         # Tests de persistencia en BD
├── test_news_feed.py        # Tests de datos (JSON)
└── README.md                # Este archivo
```

## Ejecutar Tests

### ✅ Todos los tests

```bash
pytest test/ -v
```

### ✅ Solo tests del agente (RECOMENDADO PRIMERO)

```bash
pytest test/test_agent.py -v -s
```

### ✅ Solo tests de base de datos

```bash
pytest test/test_database.py -v -s
```

### ✅ Solo tests de datos

```bash
pytest test/test_news_feed.py -v -s
```

### ✅ Con salida detallada

```bash
pytest test/test_agent.py -v -s --tb=short
```

### ✅ Mostrar prints

```bash
pytest test/test_agent.py -s
```

---

## 📋 Qué Testan

### `test_agent.py` ⭐ (PRINCIPAL)

**Valida que el agente IA responde señales coherentes:**

- ✅ Inicialización del motor sin API key
- ✅ Estructura correcta de señal retornada
- ✅ Campos obligatorios presentes: impacto, confianza, explicación, acción, disclaimer
- ✅ Valores válidos: impacto ∈ {Positivo, Negativo, Neutral}
- ✅ Confianza válida ∈ {Alta, Media, Baja}
- ✅ Confianza score entre 0-1
- ✅ Explicación y acción tienen contenido
- ✅ Disclaimer de riesgos presente
- ✅ **Agente diferencia señales** (positivas vs negativas) - PRUEBA DE INTELIGENCIA
- ✅ Maneja noticias sin descripción
- ✅ Procesa múltiples noticias sin crashes
- ✅ Señal es JSON serializable

**Resultado esperado:** ✅ 12+ tests pasando

---

### `test_database.py`

**Valida persistencia en BD:**

- ✅ Inicialización sin errores
- ✅ Guardar y recuperar auditorías
- ✅ Múltiples auditorías
- ✅ Reviewer y timestamp grabados
- ✅ Diferentes estados (Validada, Escalada, Descartada)
- ✅ Contadores de auditorías
- ✅ Caracteres especiales soportados
- ✅ **Flujo completo simulated** (guardar → recuperar → contar)
- ✅ Reporte compliance JSON serializable

**Resultado esperado:** ✅ 15+ tests pasando

---

### `test_news_feed.py`

**Valida integridad de datos:**

- ✅ JSON files existen y son válidos
- ✅ Noticias tienen campos: id, title, description, source, publishedAt, market, related_assets
- ✅ Descripciones completas (> 20 chars)
- ✅ Activos relacionados (no vacío)
- ✅ Mercados válidos
- ✅ Fechas en formato ISO
- ✅ Fuentes válidas
- ✅ Sin IDs duplicados
- ✅ Activos existen en assets.json
- ✅ Mercado noticia coincide con tipo activo

**Resultado esperado:** ✅ 20+ tests pasando

---

## 🚀 Correr desde la App

Durante desarrollo local, si quieres correr tests sin interrumpir Streamlit:

```bash
# Terminal 1: App
streamlit run app.py

# Terminal 2: Tests (en paralelo)
pytest test/test_agent.py -v --tb=short
```

---

## 📊 Cobertura Esperada

```
test_agent.py         : 14 tests → ~90% agente
test_database.py      : 13 tests → ~95% persistencia
test_news_feed.py     : 15 tests → ~100% datos

TOTAL                 : 42+ tests ✅
```

---

## ⚠️ Problemas Comunes

### Error: `ModuleNotFoundError: No module named 'agents'`

**Solución:** Ejecutar desde la raíz del proyecto

```bash
cd hackathon-track5-marketsignal
pytest test/
```

### Error: `FileNotFoundError: data/news_feed.json`

**Solución:** Verificar que estás en el directorio correcto

```bash
ls data/
# Debería mostrar: assets.json, marketsignal.db, news_feed.json
```

### Tests no encuentran fixtures

**Solución:** Verificar que `conftest.py` está en carpeta `test/`

```bash
ls test/conftest.py
# Debe existir
```

---

## 💡 Tips

- Usa `-s` para ver prints y logs detallados
- Usa `--tb=short` para stacktraces más legibles
- Usa `-k "test_agent"` para correr solo tests que coincidan con ese string
- Usa `-x` para parar en el primer error

---

## ✅ Validación en CI/CD

En Streamlit Cloud, antes de cada deploy:

```bash
pytest test/ -v --tb=short
```

Si algún test falla, el deploy debe ser rechazado.

---

**Última actualización:** 2026-07-12
