import streamlit as st
import json
import os
import requests
from fpdf import FPDF
from agents.motor import MotorAgentesIA
from core.database import init_db, guardar_revision, obtener_revisiones

# Inicializar Base de Datos SQLite y Memoria Caché de Señales
init_db()
if "senales_cache" not in st.session_state: st.session_state.senales_cache = {}

st.set_page_config(page_title="MarketSignal Guardian", layout="wide", page_icon="🏦")

# Estilos CSS - Fin-AI Terminal Dark
st.markdown("""
<style>

div[data-testid="stTabs"] button {
    background-color: #161b22; /* Fondo oscuro */
    border: 1px solid #30363d;
    color: #c9d1d9;
    padding: 12px 24px;
    border-radius: 6px; 
    margin-right: 10px;
    transition: all 0.3s ease;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    background-color: #28a745 !important; 
    color: white !important;
    border: 1px solid #28a745 !important;
    font-weight: bold;
}

/* 3. Hover 
div[data-testid="stTabs"] button:hover {
    border: 1px solid #28a745;
    color: #28a745;
}

div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    border-bottom: none;
    gap: 10px;
}
</style>
""", unsafe_allow_html=True)

# Cargar Datos Estáticos de Respaldo
@st.cache_data
def cargar_catalogos():
    with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
        activos = json.load(f)
    with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
        noticias_default = json.load(f)
    return activos, noticias_default

activos_db, noticias_resguardo = cargar_catalogos()

# --- BARRA LATERAL (CONECTORES Y TICKERS) ---
st.sidebar.title("⚡ MarketSignal Guardian")
st.sidebar.caption("Hackathon Agentic Scale - Track 5")
st.sidebar.markdown("---")

# 1. Leemos las llaves silenciosamente desde los secretos de la nube o entorno local
api_key_gemini = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
api_key_news = st.secrets.get("NEWS_API_KEY", os.getenv("NEWS_API_KEY", ""))

# 2. INTERFAZ LIMPIA: Solo mostramos las cajas de texto si NO encontró la llave en la nube
if not api_key_gemini:
    api_key_gemini = st.sidebar.text_input("🔑 Google Gemini API Key:", value="", type="password")
if not api_key_news:
    api_key_news = st.sidebar.text_input("📰 NewsAPI Key (Opcional):", value="", type="password")

# 3. Inicializamos el cerebro con caché para no repetir el ping al hacer clic en botones
@st.cache_resource
def obtener_motor(api_key):
    return MotorAgentesIA(api_key=api_key)

motor = obtener_motor(api_key_gemini)

# 4. Indicador visual limpio para el jurado (Sin mostrar contraseñas)
if motor.model:
    st.sidebar.success("🟢 Cerebro IA: Gemini 1.5 Flash Activo")
else:
    st.sidebar.warning("🟡 Cerebro IA: Modo Simulación / Fórmula 9.2")

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Tickers en Vivo (Simulado)")
for a in activos_db[:4]:
    st.sidebar.metric(f"{a['name']} ({a['symbol']})", a['current_price'], f"{a['price_move_7d']}%")

# --- ENCABEZADO Y FILTROS (HU 1) ---
st.title("📡 Radar Agéntico de Inteligencia de Mercado")
st.markdown("**Agentes integrados:** `Coyuntura`, `Asesor Inversiones`, `Cumplimiento Riesgo` & `Generador Briefing`")
st.info("💡 **Regla del Track 5:** Transforma noticias en señales explicables sin ejecutar compras ni ventas y con control humano en bucle.")

c_cat, c_act, c_ref = st.columns([2, 2, 1])

with c_cat:
    cat_filtro = st.selectbox("1. Categoría:", ["Todas", "Renta Variable", "Instrumentos de crédito", "Criptoactivos", "Otros activos"])

with c_act:
    simbolo_filtro = st.selectbox("2. Activo:", ["Todos"] + [a["symbol"] for a in activos_db])

with c_ref: 
    st.write("") 
    if st.button("🔄 Actualizar Noticias", use_container_width=True):
        st.toast("Noticias Actualizadas.", icon="✅")
        st.session_state.recargar = True

# Obtener Noticias (NewsAPI o Resguardo JSON)
noticias_actuales = noticias_resguardo
if api_key_news:
    try:
        query_str = " OR ".join([a["symbol"] for a in activos_db])
        url = f"https://newsapi.org/v2/everything?q={query_str}&language=es,en&sortBy=publishedAt&pageSize=6&apiKey={api_key_news}"
        res = requests.get(url, timeout=3).json()
        if res.get("status") == "ok" and res.get("articles"):
            noticias_actuales = res["articles"]
            st.sidebar.toast(f"API: {len(res.get('articles', []))} noticias nuevas cargadas", icon="📡")
    except Exception:
        pass # Si falla internet, se mantiene noticias_resguardo automáticamente

# PESTAÑAS
tab1, tab2 = st.tabs(["📊 Monitor de Mercado - A1,A2", "📑 Reporte de Compliance - A3"])

with tab1:
    st.subheader("Titulares y Análisis de Impacto")
    revisiones_db = obtener_revisiones()
    
    for i, noti in enumerate(noticias_actuales):
        # Mapear noticia a un activo del catálogo
        activo_rel = activos_db[0]
        for a in activos_db:
            if a["symbol"] in noti.get("title", "") or a["symbol"] in str(noti.get("related_assets", "")):
                activo_rel = a
                break
        
        # Filtros de UI
        if cat_filtro != "Todas" and activo_rel["type"] != cat_filtro: continue
        if simbolo_filtro != "Todos" and activo_rel["symbol"] != simbolo_filtro: continue

        sid = f"sig_{activo_rel['symbol']}_{i}"
        
        # --- CACHÉ INTELIGENTE DE SEÑALES ---
        # Si la señal no está en memoria, llamamos a la IA (Gemini) y la guardamos
        if sid not in st.session_state.senales_cache:
            st.session_state.senales_cache[sid] = motor.procesar_pipeline(noti, activo_rel)
        
        # Leemos la señal directamente de la memoria rápida
        senal = st.session_state.senales_cache[sid]
        # -------------------------------------

        estado_rev = revisiones_db.get(sid, {}).get("status", "⏳ Pendiente de Auditoría")

        with st.container(border=True):
            col1, col2 = st.columns([3, 2])
            
            # Columna izquierda: Información del activo y noticia
            with col1:
                st.markdown(f"#### 📰 {noti.get('title')}")
                st.caption(f"**Fuente:** {noti.get('source', {}).get('name', 'N/A')} | **Fecha:** {noti.get('publishedAt', '')[:10]} | **Activo:** `{activo_rel['name']} ({activo_rel['symbol']})`")
                st.caption(f"**ID Auditoría:** `{sid}`") 
                st.write(noti.get("description", "Sin descripción detallada."))
            
            # Columna derecha: Impacto y métricas
            with col2:
                imp = senal["impacto"]
                color = "🟢" if imp == "Positivo" else ("🔴" if imp == "Negativo" else ("⚪" if imp == "Neutral" else "🟡"))
                st.markdown(f"### {color} Impacto: **{imp.upper()}**")
                st.caption(f"Confianza IA: **{senal['confianza']}** ({senal.get('confianza_score', 'N/A')}) | Precio 7d: **{activo_rel['price_move_7d']}%**")

            # 1. Expandible de Explicabilidad (Ahora arriba, desplegable)
            with st.expander("🔍 Ver Explicabilidad y Acción Recomendada"):
                st.write(f"**Explicación Técnica:** {senal['explicacion']}")
                st.markdown(f"**⚡ Acción de Investigación:** *{senal['accion_investigacion']}*")
                st.caption(f"⚠️ *{senal['disclaimer']}*")

            # 2. Expandible de Auditoría (Workflow de Cumplimiento)
            with st.expander("📝 Crear Auditoría"):
                st.markdown(f"**Estado de Auditoría:** `{estado_rev}`")
                justificacion = st.text_area("Justificación técnica obligatoria:", key=f"just_{sid}")
                
                # Diseño compacto: Texto y botones en una misma línea
                c_titulo, c_botones = st.columns([1, 2]) # El título ocupa 1/3, los botones 2/3
                with c_titulo:
                    st.markdown("**Decisión fiduciaria:**")
                
                with c_botones:
                    # Usamos un contenedor de botones para que no tengan espacio extra
                    b1, b2, b3 = st.columns(3)
                    
                    if b1.button("✅ Validar", key=f"ok_{sid}"):
                        if len(justificacion) < 5: 
                            st.error("Se requiere justificación.")
                        else:
                            guardar_revision(sid, "✅ Validada", justificacion)
                            st.rerun()
                    b2.button("⚠️ Escalar", key=f"esc_{sid}")
                    b3.button("🗑️ Descartar", key=f"del_{sid}")
            st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("📑 Reporte de Compliance - A4")
    st.write("Resumen consolidado exclusivo para comités de inversión. **Solo incluye señales marcadas como Aprobadas por analistas humanos**.")
    
    revs = obtener_revisiones()
    aprobadas = {k: v for k, v in revs.items() if "Aprobada" in v["status"]}
    
    if not aprobadas:
        st.warning("No hay señales aprobadas aún. Ve a la pestaña de Radar, escribe una justificación y aprueba una alerta para generar el briefing.")
    else:
        # Línea de depuración para confirmar los datos
        st.write("Datos de auditoría detectados:", aprobadas)
        for sid, datos in aprobadas.items():
            st.markdown(f"### 📌 Señal Auditada: `{sid}`")
            st.markdown(f"**Revisor Fiduciario:** {datos['reviewer']} | **Fecha:** {datos['date'][:16]}")
            st.success(f"**Justificación de Aprobación:** {datos['justification']}")
            st.divider()
        if  st.button("📄 Generar Reporte Institucional"):
                       
            # Crear PDF en memoria
            pdf = FPDF()
            pdf.add_page()
            
            # Título
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(200, 10, txt="MARKETSIGNAL GUARDIAN - BRIEFING EJECUTIVO", ln=True, align='C')
            pdf.ln(10) # Salto de línea
            
            # Contenido
            pdf.set_font("Arial", size=12)
            for sid, datos in aprobadas.items():
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(200, 10, txt=f"Señal: {sid}", ln=True)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, txt=f"Justificación: {datos['justification']}\nFecha: {datos['date']}\n")
                pdf.ln(5)
            
            # Generar el PDF para el botón de descarga
            pdf_output = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="📥 Descargar Reporte en PDF",
                data=pdf_output,
                file_name="Reporte_Ejecutivo.pdf",
                mime="application/pdf"
            )
            st.success("Reporte institucional generado exitosamente.")