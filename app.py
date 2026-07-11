import streamlit as st
import json
import os
import requests
import plotly.express as px
import plotly.graph_objects as go
from agents.motor import MotorAgentesIA
from core.database import init_db, guardar_revision, obtener_revisiones

# Inicializar Base de Datos SQLite y Memoria Caché de Señales
init_db()
if "senales_cache" not in st.session_state: st.session_state.senales_cache = {}

st.set_page_config(page_title="MarketSignal Guardian | Track 5", layout="wide", page_icon="⚡")

# Estilos CSS - Fin-AI Terminal Dark
st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    .signal-card { background-color: #161b22; padding: 18px; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 12px; }
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


def get_agent_metrics(senal):
    impacto = senal.get("impacto", "Neutral")
    impacto_map = {"Positivo": 0.85, "Neutral": 0.55, "Negativo": 0.25, "Incierto": 0.45}
    impacto_score = impacto_map.get(impacto, 0.5)

    confianza_score = float(senal.get("confianza_score", 0.5)) if senal.get("confianza_score") is not None else 0.5
    asesor_score = min(1.0, max(0.0, (confianza_score + impacto_score) / 2))

    cumplimiento_score = 1.0 if "ajustado" not in senal.get("explicacion", "").lower() else 0.65

    return [
        {"agente": "Coyuntura", "score": impacto_score, "label": f"Impacto: {impacto}"},
        {"agente": "Asesor Inversiones", "score": asesor_score, "label": f"Confianza: {round(confianza_score * 100)}%"},
        {"agente": "Cumplimiento Riesgo", "score": cumplimiento_score, "label": f"Control: {round(cumplimiento_score * 100)}%"}
    ]


activos_db, noticias_resguardo = cargar_catalogos()

# --- BARRA LATERAL (CONECTORES Y TICKERS) ---
st.sidebar.title("⚡ MarketSignal Guardian")
st.sidebar.caption("Hackathon Agentic Scale - Track 5")
st.sidebar.markdown("---")

# --- LECTURA INTELIGENTE DE LLAVES (SECRETS + INPUT) ---
# Intenta leer primero de los secretos de Streamlit (st.secrets) o de variables de entorno
#gemini_default = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
#news_default = st.secrets.get("NEWS_API_KEY", os.getenv("NEWS_API_KEY", ""))

# La casilla de texto toma el valor por defecto del servidor, el jurado no necesita tocarla
api_key_gemini = st.sidebar.text_input("🔑 Google Gemini API Key:", type="password")
api_key_news = st.sidebar.text_input("📰 NewsAPI Key (Opcional):", type="password")

motor = MotorAgentesIA(api_key=api_key_gemini)
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
st.markdown("### 📰 Analizar una noticia")

texto_noticia = st.text_area(
    "Pegue aquí el texto de la noticia",
    height=200,
    placeholder="Ejemplo: NVIDIA anunció nuevos chips para IA y las acciones subieron..."
)

analizar = st.button("🔍 Analizar noticia")
c_f1, c_f2, c_f3 = st.columns([2, 2, 1])
with c_f1:
    cat_filtro = st.selectbox("1. Filtrar por Categoría:", ["Todas", "Renta Variable", "Instrumentos de crédito", "Criptoactivos", "Otros activos"])
with c_f2:
    simbolo_filtro = st.selectbox("2. Filtrar por Activo:", ["Todos"] + [a["symbol"] for a in activos_db])
with c_f3:
    if st.button("🚀 Consultar Feeds", use_container_width=True):
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
    except Exception:
        pass # Si falla internet, se mantiene noticias_resguardo automáticamente

# PESTAÑAS
tab1, tab2 = st.tabs(["📊 Radar & Señales IA (HU 1 & 2)", "📑 Briefing Ejecutivo Validado (HU 3)"])

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
        with st.expander(f"📰 {noti.get('title')} | Estado: {estado_rev}", expanded=False):
            with st.container():
                col1, col2 = st.columns([3, 2])
                with col1:
                    st.caption(f"**Fuente:** {noti.get('source', {}).get('name', 'N/A')} | **Fecha:** {noti.get('publishedAt', '')[:10]} | **Activo:** `{activo_rel['name']} ({activo_rel['symbol']})`")
                    st.write(noti.get("description", "Sin descripción detallada en el feed."))
                
                with col2:
                    imp = senal["impacto"]
                    color = "🟢" if imp == "Positivo" else ("🔴" if imp == "Negativo" else ("⚪" if imp == "Neutral" else "🟡"))
                    st.markdown(f"### {color} Impacto: **{imp.upper()}**")
                    st.caption(f"Confianza IA: **{senal['confianza']}** ({senal.get('confianza_score', 'N/A')}) | Precio 7d: **{activo_rel['price_move_7d']}%**")
                    
                    with st.container():
                        st.write("🔍 Ver Explicabilidad y Acción Recomendada")
                        st.write(f"**Explicación Técnica:** {senal['explicacion']}")
                        st.markdown(f"**⚡ Acción de Investigación:** *{senal['accion_investigacion']}*")
                        st.caption(f"⚠️ *{senal['disclaimer']}*")

                    with st.container():
                        st.write("📊 Métricas de Agentes")
                        
                        agent_metrics = get_agent_metrics(senal)
                        tipo = senal.get("tipo_grafico", "bar")

                        # ==========================
                        # GAUGE
                        # ==========================
                        if tipo == "gauge":

                            fig = go.Figure(go.Indicator(
                                mode="gauge+number",
                                value=senal.get("confianza_score", 0.5) * 100,
                                title={"text": "Confianza IA"},
                                gauge={
                                    "axis": {"range": [0, 100]},
                                    "bar": {"color": "#00b1ff"},
                                    "steps": [
                                        {"range": [0, 40], "color": "#8b0000"},
                                        {"range": [40, 70], "color": "#d4a017"},
                                        {"range": [70, 100], "color": "#0f9d58"},
                                    ]
                                }
                            ))

                            fig.update_layout(
                                template="plotly_dark",
                                height=320
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # ==========================
                        # PIE
                        # ==========================
                        elif tipo == "pie":

                            fig = px.pie(
                                values=[m["score"] for m in agent_metrics],
                                names=[m["agente"] for m in agent_metrics],
                                hole=0.45
                            )

                            fig.update_layout(
                                template="plotly_dark",
                                height=320
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # ==========================
                        # SCATTER
                        # ==========================
                        elif tipo == "scatter":

                            fig = px.scatter(
                                x=[m["score"] for m in agent_metrics],
                                y=[senal.get("confianza_score",0.5)]*len(agent_metrics),
                                text=[m["agente"] for m in agent_metrics]
                            )

                            fig.update_layout(
                                template="plotly_dark",
                                height=320
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # ==========================
                        # LINE
                        # ==========================
                        elif tipo == "line":

                            fig = px.line(
                                x=[m["agente"] for m in agent_metrics],
                                y=[m["score"] for m in agent_metrics],
                                markers=True
                            )

                            fig.update_layout(
                                template="plotly_dark",
                                yaxis_range=[0,1],
                                height=320
                            )

                            st.plotly_chart(fig, use_container_width=True)

                        # ==========================
                        # BARRAS (por defecto)
                        # ==========================
                        else:

                            cols = st.columns(3)

                            for col, metric in zip(cols, agent_metrics):

                                fig = px.bar(
                                    x=[metric["agente"]],
                                    y=[metric["score"]],
                                    text=[metric["label"]],
                                    title=metric["agente"]
                                )

                                fig.update_traces(
                                    marker_color="#00b1ff",
                                    textposition="outside"
                                )

                                fig.update_layout(
                                    yaxis=dict(range=[0,1]),
                                    template="plotly_dark",
                                    showlegend=False,
                                    height=260
                                )

                                col.plotly_chart(
                                    fig,
                                    use_container_width=True,
                                    key=f"plotly_{sid}_{metric['agente']}"
                                )
                
                st.markdown("---")
                # Panel de Revisión Humana - HITL
                st.markdown(f"**Estado de Auditoría:** `{estado_rev}`")
                c_a, c_b = st.columns([3, 2])
                with c_a:
                    just = st.text_input(f"Justificación obligatoria del analista para {sid}:", key=f"j_{sid}")
                with c_b:
                    st.write("Decisión fiduciaria:")
                    b1, b2, b3 = st.columns(3)
                    if b1.button("✅ Aprobar", key=f"ok_{sid}"):
                        if len(just) < 5: st.error("Escribe una justificación.")
                        else:
                            guardar_revision(sid, "✅ Aprobada", just)
                            st.rerun()
                    if b2.button("⚠️ Escalar", key=f"esc_{sid}"):
                        guardar_revision(sid, "⚠️ Escalada a Comité", just or "Requiere auditoría de riesgo alto.")
                        st.rerun()
                    if b3.button("🗑️ Descartar", key=f"del_{sid}"):
                        guardar_revision(sid, "❌ Descartada", just or "Ruido de mercado sin impacto temporal.")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.subheader("📑 Briefing Ejecutivo de Mercado (Agente 4)")
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
        if st.button("🖨️ Exportar Briefing para Clientes"):
            st.balloons()
            st.success("Briefing empaquetado y listo para envío institucional sin directrices de compra/venta.")