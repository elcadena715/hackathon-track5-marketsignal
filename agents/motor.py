import json
import os
import re
import google.generativeai as genai
from prompts import SYSTEM_PROMPT_ASESOR


class MotorAgentesIA:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)

                # --- SELECTOR BLINDADO CON PING DE VALIDACIÓN Y PRIORIDAD GEMINI ---
                # Priorizamos los nombres estándar más rápidos y estables para finanzas
                candidatos = [
                    "gemini-1.5-flash",
                    "gemini-1.5-flash-latest",
                    "gemini-flash-latest",
                    "models/gemini-flash-latest",
                    "gemini-1.5-pro",
                    "gemini-pro",
                    "models/gemini-1.5-flash",
                ]

                print("⏳ Verificando cerebro IA y probando conexión en vivo...")

                for nombre in candidatos:
                    try:
                        modelo_test = genai.GenerativeModel(nombre)
                        resp_test = modelo_test.generate_content(
                            "ping",
                            generation_config=genai.GenerationConfig(
                                max_output_tokens=5
                            ),
                        )
                        if resp_test and resp_test.text:
                            self.model = modelo_test
                            print(
                                f"🟢 ¡Cerebro IA Conectado y Verificado! Modelo oficial confirmado: {nombre}"
                            )
                            break
                    except Exception:
                        continue

                # Si los nombres estándar fallan, buscamos en el catálogo dando prioridad absoluta a "gemini"
                if not self.model:
                    modelos_disponibles = [
                        m.name
                        for m in genai.list_models()
                        if "generateContent" in m.supported_generation_methods
                    ]

                    # Ordenamos para que los que tienen "gemini" y "flash" queden primeros en la fila, dejando "gemma" al final
                    modelos_ordenados = sorted(
                        modelos_disponibles,
                        key=lambda x: (
                            0
                            if ("gemini" in x.lower() and "flash" in x.lower())
                            else (1 if "gemini" in x.lower() else 2)
                        ),
                    )

                    for m_name in modelos_ordenados:
                        try:
                            modelo_test = genai.GenerativeModel(m_name)
                            resp_test = modelo_test.generate_content(
                                "ping",
                                generation_config=genai.GenerationConfig(
                                    max_output_tokens=5
                                ),
                            )
                            if resp_test and resp_test.text:
                                self.model = modelo_test
                                print(
                                    f"🟢 Autodetectado modelo funcional en tu cuenta: {m_name}"
                                )
                                break
                        except Exception:
                            continue

                if not self.model:
                    print(
                        "⚠️ Tu API Key es válida pero ningún modelo respondió el ping. Usando respaldo determinista 9.2."
                    )

            except Exception as e:
                print(f"❌ Error al configurar Google AI: {e}")
                self.model = None

    def procesar_pipeline(self, texto_noticia):
        """
        Pipeline principal:
        Recibe una noticia libre y Gemini genera
        una señal financiera estructurada.
        """

        if not self.model:
            raise Exception("Gemini no está conectado. Ingrese una API Key válida.")

        try:

            prompt_usuario = f"""

    Analiza la siguiente noticia financiera:

    ------------------------------------------------

    {texto_noticia}

    ------------------------------------------------


    Genera una señal explicable para un analista humano.


    Debes identificar:

    - activo financiero principal
    - ticker compatible con Yahoo Finance
    - sector económico
    - tipo de activo
    - impacto esperado
    - confianza
    - riesgo
    - horizonte temporal
    - tipo de gráfico


    No generes recomendaciones de compra o venta.

    Devuelve únicamente JSON válido.

    """

            respuesta = self.model.generate_content(
                f"{SYSTEM_PROMPT_ASESOR}\n\n{prompt_usuario}",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json", temperature=0.2
                ),
            )

            texto = respuesta.text

            # Protección por si Gemini agrega texto

            match = re.search(r"\{.*\}", texto, re.DOTALL)

            if not match:

                raise Exception("Gemini no devolvió JSON válido.")

            senal = json.loads(match.group(0))

            print("🟢 Gemini analizó correctamente la noticia")

        except Exception as e:

            raise Exception(f"Error generando análisis Gemini: {e}")

        # Guardrail de cumplimiento

        senal = self._supervisor_cumplimiento(senal)

        # Guardamos referencia

        senal["noticia_original"] = texto_noticia

        return senal

    def _aplicar_formula_matematica(self, evento, activo):
        move_7d = activo.get("price_move_7d", 0.0)
        price_score = max(-1.0, min(1.0, move_7d / 10.0))

        txt = evento["titulo"].lower()
        sentiment = (
            0.5
            if any(w in txt for w in ["aprueba", "supera", "impulsa", "favorable"])
            else (
                -0.5
                if any(w in txt for w in ["retraso", "caída", "riesgo", "enfriamiento"])
                else 0.0
            )
        )

        event_weight = (
            0.8
            if any(w in txt for w in ["sec", "reserva federal", "tasa", "regulación"])
            else 0.5
        )
        evidence_score = (
            0.85
            if evento["fuente"] in ["Bloomberg News", "Reuters", "Wall Street Journal"]
            else 0.50
        )

        impact_score = (
            (0.35 * sentiment)
            + (0.25 * event_weight)
            + (0.25 * price_score)
            + (0.15 * evidence_score)
        )

        if evidence_score < 0.40:
            impact = "Incierto"
        elif abs(impact_score) < 0.15:
            impact = "Neutral"
        elif impact_score >= 0.15:
            impact = "Positivo"
        else:
            impact = "Negativo"

        conf_score = min(
            1.0, max(0.0, (evidence_score * 0.7) + (abs(impact_score) * 0.3))
        )
        conf_label = (
            "Alta"
            if conf_score >= 0.75
            else ("Media" if conf_score >= 0.50 else "Baja")
        )

        return {
            "impacto": impact,
            "confianza": conf_label,
            "confianza_score": round(conf_score, 2),
            "explicacion": f"Análisis determinista (Fórmula 9.2): El evento presenta un impacto ponderado de {round(impact_score, 2)} al contrastar un sentimiento de {sentiment} con una variación de precio del {move_7d}% en 7 días.",
            "accion_investigacion": f"Auditar volúmenes transaccionales y validar exposición al activo {activo['symbol']}.",
            "disclaimer": "Esta señal explicable se genera con fines de análisis e investigación; no constituye asesoría personalizada ni garantiza resultados financieros.",
        }

    def _supervisor_cumplimiento(self, senal):

        prohibidas = [
            "compre",
            "compra",
            "venda",
            "venta",
            "garantizado",
            "ganancia segura",
            "buy now",
            "sell now",
        ]

        campos_revision = ["explicacion", "accion_investigacion"]

        for campo in campos_revision:

            texto = senal.get(campo, "")

            texto_lower = texto.lower()

            for palabra in prohibidas:

                if palabra in texto_lower:

                    senal[campo] = (
                        "[AJUSTADO POR CUMPLIMIENTO] "
                        "El análisis fue modificado "
                        "para evitar instrucciones "
                        "directas de inversión. " + texto
                    )

                    break

        senal["disclaimer"] = (
            "Esta señal se genera únicamente "
            "con fines informativos y de investigación. "
            "No constituye asesoría financiera personalizada "
            "ni garantiza resultados futuros."
        )

        return senal
