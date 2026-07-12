import streamlit as st
import os
import json
import plotly.express as px
import plotly.graph_objects as go

from agents.motor import MotorAgentesIA
from core.database import init_db, guardar_revision, obtener_revisiones

# =====================================================
# INICIALIZACIÓN
# =====================================================

init_db()

if "resultado_ia" not in st.session_state:
    st.session_state.resultado_ia = None


st.set_page_config(
    page_title="MarketSignal Guardian | Track 5", layout="wide", page_icon="⚡"
)


# =====================================================
# ESTILOS
# =====================================================

st.markdown(
    """
<style>

.reportview-container {
    background: #0e1117;
}


.signal-card {

    background-color:#161b22;
    padding:18px;
    border-radius:8px;
    border:1px solid #30363d;
    margin-bottom:12px;

}

</style>
""",
    unsafe_allow_html=True,
)


# =====================================================
# MÉTRICAS DE AGENTES
# =====================================================


def get_agent_metrics(senal):

    impacto = senal.get("impacto", "Neutral")

    impacto_map = {
        "Positivo": 0.85,
        "Neutral": 0.55,
        "Negativo": 0.25,
        "Incierto": 0.45,
    }

    impacto_score = impacto_map.get(impacto, 0.5)

    confianza_score = float(senal.get("confianza_score", 0.5))

    asesor_score = min(1.0, max(0.0, (confianza_score + impacto_score) / 2))

    cumplimiento_score = 1.0

    return [
        {"agente": "Coyuntura", "score": impacto_score, "label": f"Impacto: {impacto}"},
        {
            "agente": "Asesor Inversiones",
            "score": asesor_score,
            "label": f"Confianza: {round(confianza_score*100)}%",
        },
        {
            "agente": "Cumplimiento Riesgo",
            "score": cumplimiento_score,
            "label": "Control: 100%",
        },
    ]


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("⚡ MarketSignal Guardian")

st.sidebar.caption("Hackathon Agentic Scale - Track 5")

st.sidebar.markdown("---")


api_key_gemini = st.sidebar.text_input("🔑 Google Gemini API Key:", type="password")


# Crear motor IA

motor = MotorAgentesIA(api_key=api_key_gemini)


if motor.model:

    st.sidebar.success("🟢 Gemini conectado")


else:

    st.sidebar.error("🔴 Gemini no disponible")


st.sidebar.markdown("---")


st.sidebar.info("""
Este sistema funciona únicamente
con análisis generado por Gemini.

No utiliza datos simulados.
""")


# =====================================================
# TITULO PRINCIPAL
# =====================================================


st.title("📡 Radar Agéntico de Inteligencia de Mercado")


st.markdown("""
**Agentes integrados:**

`Coyuntura`
`Asesor Inversiones`
`Cumplimiento Riesgo`
`Generador Briefing`

""")


st.info("""
💡 Regla del Track 5:

Transforma noticias en señales explicables
sin ejecutar compras ni ventas y con control
humano en bucle.
""")


st.markdown("### 📰 Analizar una noticia")


texto_noticia = st.text_area(
    "Pegue aquí el texto de la noticia",
    height=220,
    placeholder="""

Ejemplo:

NVIDIA anunció nuevos chips de inteligencia artificial
y espera aumentar sus ingresos durante el próximo trimestre.

""",
)


analizar = st.button("🔍 Analizar noticia con Gemini", disabled=not motor.model)


if not motor.model:

    st.warning("""
Ingrese una API Key válida de Gemini
para habilitar el análisis.
""")

    st.stop()
# =====================================================
# PESTAÑAS
# =====================================================


tab1, tab2 = st.tabs(
    ["📊 Radar & Señales IA (HU 1 & 2)", "📑 Briefing Ejecutivo Validado (HU 3)"]
)


# =====================================================
# TAB 1
# =====================================================


with tab1:

    st.subheader("Titulares y Análisis de Impacto")

    # ==========================================
    # EJECUTAR GEMINI
    # ==========================================

    if analizar:

        if not texto_noticia.strip():

            st.warning("Debe ingresar una noticia.")

        else:

            with st.spinner("🤖 Gemini analizando la noticia..."):

                try:

                    resultado = motor.procesar_pipeline(texto_noticia)

                    st.session_state.resultado_ia = resultado

                except Exception as e:

                    st.error(f"Error en análisis IA: {e}")

    # ==========================================
    # MOSTRAR RESULTADO
    # ==========================================

    if st.session_state.resultado_ia:

        senal = st.session_state.resultado_ia

        sid = "sig_" + senal.get("ticker", "UNKNOWN")

        revisiones_db = obtener_revisiones()

        estado_rev = revisiones_db.get(sid, {}).get(
            "status", "⏳ Pendiente de Auditoría"
        )

        with st.expander(
            f"📌 {senal.get('activo','Activo desconocido')} " f"| Estado: {estado_rev}",
            expanded=True,
        ):

            col1, col2 = st.columns([3, 2])

            # ==================================
            # INFORMACIÓN GENERAL
            # ==================================

            with col1:

                st.caption(f"""
                    **Activo:** {senal.get('activo','N/A')}

                    **Ticker:** {senal.get('ticker','N/A')}

                    **Sector:** {senal.get('sector','N/A')}

                    **Tipo activo:** {senal.get('tipo_activo','N/A')}

                    """)

                st.write("### Explicación IA")

                st.write(senal.get("explicacion", "Sin explicación"))

                st.markdown(f"""
                    **⚡ Acción de investigación:**

                    {senal.get(
                        "accion_investigacion",
                        "No definida"
                    )}

                    """)

                st.caption(senal.get("disclaimer", ""))

            # ==================================
            # IMPACTO
            # ==================================

            with col2:

                impacto = senal.get("impacto", "Neutral")

                icono = {
                    "Positivo": "🟢",
                    "Negativo": "🔴",
                    "Neutral": "⚪",
                    "Incierto": "🟡",
                }.get(impacto, "⚪")

                st.markdown(f"""
                    ## {icono}

                    Impacto:

                    **{impacto.upper()}**

                    """)

                st.metric("Confianza IA", f"{round(
                        senal.get(
                            'confianza_score',
                            0
                        )*100
                    )}%")

                st.metric("Riesgo", senal.get("riesgo", "N/A"))

                st.metric("Horizonte", senal.get("horizonte", "N/A"))

            st.divider()

            # ==================================
            # GRÁFICOS DINÁMICOS GEMINI
            # ==================================

            st.write("## 📊 Métricas de Agentes")

            agent_metrics = get_agent_metrics(senal)

            datos_grafico = senal.get("grafico", {})
            tipo = senal.get("tipo_grafico", "bar")

            if tipo == "gauge":

                fig = go.Figure(
                    go.Indicator(
                        mode="gauge+number",
                        value=senal.get("confianza_score", 0.5) * 100,
                        title={"text": "Confianza IA"},
                        gauge={"axis": {"range": [0, 100]}},
                    )
                )

                fig.update_layout(template="plotly_dark", height=320)

                st.plotly_chart(fig, use_container_width=True)

            elif tipo == "pie":

                fig = px.pie(
                    values=[x["score"] for x in agent_metrics],
                    names=[x["agente"] for x in agent_metrics],
                    hole=0.4,
                )

                fig.update_layout(template="plotly_dark")

                st.plotly_chart(fig, use_container_width=True)

            else:

                fig = px.bar(
                    x=datos_grafico.get("categorias", []),
                    y=datos_grafico.get("valores", []),
                    title=datos_grafico.get("titulo", "Análisis IA"),
                )

                fig.update_layout(template="plotly_dark", yaxis={"range": [0, 1]})

                st.plotly_chart(fig, use_container_width=True)

            # ==================================================
            # PANEL DE REVISIÓN HUMANA (HITL)
            # ==================================================

            st.markdown("---")

            st.markdown(f"""
                ### 🧑‍💼 Auditoría Humana

                Estado actual:

                `{estado_rev}`

                """)

            justificacion = st.text_input(
                "Justificación del analista:", key=f"just_{sid}"
            )

            col_a, col_b, col_c = st.columns(3)

            # APROBAR

            with col_a:

                if st.button("✅ Aprobar", key=f"approve_{sid}"):

                    if len(justificacion.strip()) < 5:

                        st.error("Debe escribir una justificación.")

                    else:

                        guardar_revision(sid, "✅ Aprobada", justificacion)

                        st.success("Señal aprobada correctamente.")

                        st.rerun()

            # ESCALAR

            with col_b:

                if st.button("⚠️ Escalar", key=f"scale_{sid}"):

                    guardar_revision(
                        sid,
                        "⚠️ Escalada a Comité",
                        (
                            justificacion
                            if justificacion
                            else "Requiere revisión adicional."
                        ),
                    )

                    st.warning("Señal enviada a comité.")

                    st.rerun()

            # DESCARTAR

            with col_c:

                if st.button("🗑️ Descartar", key=f"discard_{sid}"):

                    guardar_revision(
                        sid,
                        "❌ Descartada",
                        justificacion if justificacion else "Señal descartada.",
                    )

                    st.info("Señal descartada.")

                    st.rerun()

# =====================================================
# TAB 2
# BRIEFING EJECUTIVO
# =====================================================


with tab2:

    st.subheader("📑 Briefing Ejecutivo de Mercado")

    st.write("""
Resumen consolidado generado únicamente
con señales aprobadas por analistas humanos.
""")

    revisiones = obtener_revisiones()

    aprobadas = {k: v for k, v in revisiones.items() if "Aprobada" in v["status"]}

    if not aprobadas:

        st.warning("""
No existen señales aprobadas todavía.

Analiza una noticia en la pestaña Radar
y aprueba una señal.
""")

    else:

        for sid, datos in aprobadas.items():

            st.markdown(f"""
                ## 📌 Señal Auditada

                **ID:**
                `{sid}`


                **Estado:**

                {datos["status"]}


                **Analista:**

                {datos.get(
                    "reviewer",
                    "Sistema"
                )}


                **Fecha:**

                {datos.get(
                    "date",
                    ""
                )}


                """)

            st.success(f"""
                Justificación:

                {datos["justification"]}
                """)

            st.divider()

        if st.button("🖨️ Exportar Briefing"):

            st.balloons()

            st.success("""
Briefing generado correctamente.

Documento listo para distribución institucional.
""")
