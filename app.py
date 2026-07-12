import streamlit as st
import json
import os
import requests
from fpdf import FPDF
from agents.motor import MotorAgentesIA
from core.database import init_db, guardar_revision, obtener_revisiones
from datetime import datetime


init_db()
if "senales_cache" not in st.session_state: st.session_state.senales_cache = {}
if 'view' not in st.session_state:
    st.session_state.view = 'list'
if 'selected_news' not in st.session_state:
    st.session_state.selected_news = None

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
div.stButton > button:hover p {
    color: #58a6ff !important;
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
    mercados = ["Todos", "Monedas", "Acciones", "Criptoactivos", "ETFs", "Bonos", "Materias Primas"]
    cat_filtro = st.selectbox("1. Mercados:", mercados)

with c_act:
    activos_disponibles = [a for a in activos_db if cat_filtro == "Todos" or a["type"] == cat_filtro]
    simbolos = ["Todos"] + [a["symbol"] for a in activos_disponibles]
    simbolo_filtro = st.selectbox("2. Activo:", simbolos)

with c_ref: 
    st.write("") 
    if st.button("🔄 Buscar Noticias", use_container_width=True):
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
    # --- LÓGICA DE NAVEGACIÓN ---
    if st.session_state.view == 'list':
        st.subheader("Titulares y Análisis de Impacto")
        revisiones_db = obtener_revisiones()
        
        # Aseguramos que usamos todas las noticias cargadas
        for i, noti in enumerate(noticias_actuales):
            # 1. Mapear activo (Lógica de búsqueda)
            activo_rel = activos_db[0]
            for a in activos_db:
                if a["symbol"] in str(noti.get("related_assets", [])):
                    activo_rel = a
                    break
        
        # 2. Filtros (Si no coinciden, saltamos esta noticia)
            if cat_filtro != "Todos" and activo_rel["type"] != cat_filtro: continue
            if simbolo_filtro != "Todos" and activo_rel["symbol"] != simbolo_filtro: continue

            sid = f"sig_{activo_rel['symbol']}_{i}"
            
            # 3. Procesar impacto (Caché inteligente)
            if sid not in st.session_state.senales_cache:
                st.session_state.senales_cache[sid] = motor.procesar_pipeline(noti, activo_rel)
            senal = st.session_state.senales_cache[sid]

            # 4. Renderizado estilo Bloomberg (con Impacto incluido)
            with st.container(border=True):
                st.markdown(f"#### {noti.get('title')}")
                
                # Línea de metadatos con Impacto destacado
                imp = senal["impacto"]
                col_info, col_btn = st.columns([3, 1])
                
                with col_info:
                    st.caption(f"**Activo:** `{activo_rel['name']} ({activo_rel['symbol']})` | **Fuente:** {noti.get('source', {}).get('name', 'N/A')}")
                    st.markdown(f"**Impacto:** {imp.upper()}")
                    
                    if st.button("🔍 Ver Análisis Detallado", key=f"det_{sid}"):
                        st.session_state.selected_news = (noti, activo_rel, sid)
                        st.session_state.view = 'detail'
                        st.rerun()

    # --- FICHA DE AUDITORÍA (DETALLE) ---
    elif st.session_state.view == 'detail':
        noti, activo_rel, sid = st.session_state.selected_news
        
        if st.button("⬅️ Volver al Radar"):
            st.session_state.view = 'list'
            st.rerun()
            
        # PROCESAMIENTO CON MOTOR
        if sid not in st.session_state.senales_cache:
            st.session_state.senales_cache[sid] = motor.procesar_pipeline(noti, activo_rel)
        senal = st.session_state.senales_cache[sid]
        
        # RENDERIZADO DE FICHA COMPLETA
        st.title(noti.get('title'))
        
        # --- AQUÍ ESTÁ LO QUE FALTABA: IMPACTO Y CONFIANZA ---
        imp = senal["impacto"]
        color = "🟢" if imp == "Positivo" else ("🔴" if imp == "Negativo" else ("⚪" if imp == "Neutral" else "🟡"))
        
        c_head1, c_head2 = st.columns([2, 1])
        with c_head1:
            st.caption(f"{noti.get('source', {}).get('name', 'N/A')} - {noti.get('publishedAt', '')[:10]}")
        with c_head2:
            st.markdown(f"### {color} **{imp.upper()}**")
        
        st.write(noti.get("description", "Sin descripción detallada."))
        st.caption(f"Confianza IA: **{senal['confianza']}** ({senal.get('confianza_score', 'N/A')})")
        
        st.markdown("---")
        
        # Explicabilidad COMPLETA
        st.subheader("🔍 Explicabilidad y Acción Recomendada")
        st.info(f"**Explicación:** {senal['explicacion']}")
        st.write(f"**⚡ Acción:** {senal['accion_investigacion']}")
        st.caption(f"⚠️ *{senal['disclaimer']}*")
        
        # Flujo de Auditoría
        with st.expander("📝 Crear Auditoría", expanded=True):
            justificacion = st.text_area("Justificación técnica:", key=f"just_{sid}")
            b1, b2, b3 = st.columns(3)
            if b1.button("✅ Validar", key=f"ok_{sid}"):
                if len(justificacion) > 5:
                    guardar_revision(sid, "✅ Validada", justificacion)
                    st.success("Guardado.")
                else: st.error("Se requiere justificación.")
            b2.button("⚠️ Escalar", key=f"esc_{sid}")
            b3.button("🗑️ Descartar", key=f"del_{sid}")

with tab2:
    st.subheader("📑 Reporte de Compliance - A4")
    st.write("Resumen consolidado exclusivo para comités de inversión. **Solo incluye señales marcadas como Aprobadas por analistas humanos**.")
    
    revs = obtener_revisiones()
    aprobadas = {k: v for k, v in revs.items() if "Aprobada" in v["status"]}
    
    if not aprobadas:
        st.warning("No hay señales aprobadas aún. Ve a la pestaña de Radar, escribe una justificación y aprueba una alerta para generar el briefing.")
    else:
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
            pdf.cell(200, 10, txt="REPORTE DE CUMPLIMIENTO - MARKETSIGNAL GUARDIAN", ln=True, align='C')
            pdf.set_font("Arial", size=10)
            pdf.set_text_color(0, 0, 0)
            pdf.ln(15)
            pdf.set_font("Arial", '', 10)
            pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='R')
            pdf.ln(5)

            # Cuerpo (Iteración mejorada)
            for sid, datos in aprobadas.items():
                # Título de la sección de señal
                pdf.set_fill_color(240, 240, 240)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"  SEÑAL: {sid}", ln=True, fill=True)
                
                # Detalles en formato limpio
                pdf.set_font("Arial", '', 11)
                pdf.ln(2)
                pdf.cell(0, 8, f"Analista: {datos.get('reviewer', 'Analista de Turno')}", ln=True)
                pdf.cell(0, 8, f"Fecha de auditoría: {datos.get('date', '')[:16]}", ln=True)
                pdf.ln(2)
                
                # Justificación (con caja de texto)
                pdf.set_font("Arial", 'B', 10)
                pdf.cell(0, 7, "Justificación técnica:", ln=True)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 6, datos.get('justification', 'N/A'))
                pdf.ln(2)
                pdf.line(10, pdf.get_y(), 200, pdf.get_y()) # Línea divisoria entre señales
                pdf.ln(3)

                # Footer (Legal)
                pdf.set_y(-30)
                pdf.set_font("Arial", 'I', 8)
                pdf.multi_cell(0, 4, "ADVERTENCIA LEGAL: Este documento es una herramienta de priorización de investigación basada en análisis agéntico y supervisión humana. No constituye asesoría financiera personalizada ni garantiza rentabilidad. Uso exclusivo para comités internos.")
            
            # Generar el PDF para el botón de descarga
            pdf_output = pdf.output(dest='S').encode('latin-1')
            
            st.download_button(
                label="📥 Descargar Reporte en PDF",
                data=pdf_output,
                file_name="Reporte_Cumplimiento.pdf",
                mime="application/pdf"
            )
            st.success("Reporte institucional generado exitosamente.")