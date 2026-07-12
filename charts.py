import plotly.express as px
import plotly.graph_objects as go


def crear_grafico(senal, datos):
    
    tipo = senal.get("tipo_grafico", "bar")

    confianza = senal.get("confianza_score", 0.5)

    impacto = senal.get("impacto", "Neutral")

    # =====================
    # GAUGE
    # =====================
    if tipo == "gauge":

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=confianza * 100,
            title={"text": "Confianza IA"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#00b1ff"},
                "steps": [
                    {"range": [0, 40], "color": "#8b0000"},
                    {"range": [40, 70], "color": "#d4a017"},
                    {"range": [70, 100], "color": "#0f9d58"}
                ]
            }
        ))

        fig.update_layout(
            template="plotly_dark",
            height=350
        )

        return fig

    # =====================
    # PIE
    # =====================
    elif tipo == "pie":

        fig = px.pie(
            names=["Impacto", "Riesgo", "Confianza"],
            values=[
                confianza * 100,
                (1 - confianza) * 100,
                50
            ],
            hole=.45
        )

        fig.update_layout(
            template="plotly_dark",
            height=350
        )

        return fig

    # =====================
    # SCATTER
    # =====================
    elif tipo == "scatter":

        fig = px.scatter(
            x=[1],
            y=[confianza],
            text=[impacto]
        )

        fig.update_layout(
            template="plotly_dark",
            yaxis_range=[0, 1],
            height=350
        )

        return fig

    # =====================
    # LINE
    # =====================
    elif tipo == "line":

        fig = px.line(
            datos,
            x=datos.index,
            y="Close",
            title=f"Precio histórico de {senal['ticker']}"
        )

        fig.update_layout(
            template="plotly_dark",
            height=350,
            xaxis_title="Fecha",
            yaxis_title="Precio"
        )

        return fig

    # =====================
    # BAR
    # =====================
    else:

        fig = px.bar(
            x=["Confianza"],
            y=[confianza]
        )

        fig.update_layout(
            template="plotly_dark",
            yaxis_range=[0, 1],
            showlegend=False,
            height=350
        )

        return fig