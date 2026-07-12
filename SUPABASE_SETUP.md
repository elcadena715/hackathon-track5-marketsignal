# 🔧 Configuración de Supabase para Persistencia de Datos

## Problema resuelto
✅ Las auditorías ahora se guardan en **Supabase (PostgreSQL en la nube)** en lugar de SQLite efímero
✅ **Fallback automático a SQLite** si Supabase no está disponible (desarrollo local)
✅ Los datos **persisten entre reinicios** de Streamlit Cloud

---

## Paso 1: Crear cuenta en Supabase

1. Ve a [https://supabase.com](https://supabase.com)
2. Clic en **Sign In** → **Sign up**
3. Usa GitHub, Google o email
4. Crea un nuevo **Project** (ej: "marketsignal")
5. Espera a que se provisione (2-3 minutos)

---

## Paso 2: Crear la tabla en Supabase

1. En el dashboard de Supabase, ve a **SQL Editor**
2. Clic en **New Query**
3. Copia y pega esto:

```sql
CREATE TABLE IF NOT EXISTS reviews (
  id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
  signal_id TEXT NOT NULL,
  status TEXT NOT NULL,
  justification TEXT NOT NULL,
  reviewer TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Crear índice para queries rápidas
CREATE INDEX idx_signal_id ON reviews(signal_id);
```

4. Clic en **Run** (ícono de play)
5. ✅ Tabla creada!

---

## Paso 3: Obtener credenciales

1. En Supabase, ve a **Project Settings** (abajo a la izquierda)
2. Clic en **API**
3. Copia:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY` (la key pública está bien)

Ejemplo:
```
SUPABASE_URL = https://abc123def456.supabase.co
SUPABASE_KEY = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Paso 4: Configurar Streamlit Cloud

### Opción A: Local (para testing)
1. Abre `.streamlit/secrets.toml` en tu editor
2. Reemplaza los valores:
```toml
SUPABASE_URL = "tu-url-aqui"
SUPABASE_KEY = "tu-key-aqui"
GEMINI_API_KEY = "tu-gemini-key"
NEWS_API_KEY = "tu-news-key"
```
3. Guarda

### Opción B: En GitHub (para despliegue en Streamlit Cloud)
1. En GitHub, ve a tu repositorio → **Settings** → **Secrets and variables** → **Actions**
2. Clic en **New repository secret**
3. Crea cada uno:
   - Name: `SUPABASE_URL` → Value: `https://abc123.supabase.co`
   - Name: `SUPABASE_KEY` → Value: tu key
   - Name: `GEMINI_API_KEY` → Value: tu key
   - Name: `NEWS_API_KEY` → Value: tu key

4. Luego en Streamlit Cloud:
   - Ve a **App settings** → **Secrets**
   - Copia lo mismo que pusiste en GitHub

---

## Paso 5: Instalar dependencias

```bash
pip install -r requirements.txt
```

Ya incluye `supabase>=2.0.0`

---

## Verificar que funciona

Cuando ejecutes la app, deberías ver en los logs:

```
✅ Tabla 'reviews' existe en Supabase
```

O si usas fallback local:

```
⚠️ SUPABASE_URL o SUPABASE_KEY no configuradas. Usando modo fallback SQLite.
```

---

## Flujo de datos

1. **Usuario hace clic en "Validar", "Escalar" o "Descartar"**
   ↓
2. `guardar_revision()` intenta **Supabase** primero
   ↓
3. Si funciona → ✅ Guardado en PostgreSQL (persiste)
   ↓
4. Si falla → 🔄 Fallback a SQLite local automáticamente

---

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `ModuleNotFoundError: No module named 'supabase'` | Ejecuta `pip install supabase` |
| `401 Unauthorized` | Verifica que `SUPABASE_KEY` es la **key pública**, no la privada |
| Datos desaparecen en cloud | Revisa que `SUPABASE_URL` y `SUPABASE_KEY` están en Streamlit Cloud Secrets |
| Table doesn't exist | Ejecuta el SQL del Paso 2 en Supabase SQL Editor |

---

## Límites Gratuitos de Supabase

- ✅ 500 MB almacenamiento
- ✅ 2 GB bandwidth/mes
- ✅ Hasta 100,000 requests/mes
- ✅ APIs REST y realtime
- ❌ No logs de auditoría ilimitada (plan Pro)

Para tu app de auditorías, es **más que suficiente**.

---

## Validación final

Prueba local:
```bash
streamlit run app.py
```

1. Ve a "Monitor de Mercado"
2. Haz clic en "🔍 Ver Análisis Detallado"
3. Expande "📝 Crear Auditoría"
4. Agrega una justificación
5. Haz clic en "✅ Validar"
6. Deberías ver "✅ Señal Validada y Guardada"
7. Recarga la página (F5)
8. Si vuelves a ver la misma auditoría en "Reporte de Compliance" → ✅ Funciona!

---

**¿Preguntas?** Revisa los logs de Streamlit en la terminal donde ejecutas `streamlit run app.py`
