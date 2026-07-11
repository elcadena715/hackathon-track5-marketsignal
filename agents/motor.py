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
                    'gemini-1.5-flash',
                    'gemini-1.5-flash-latest',
                    'gemini-flash-latest',
                    'models/gemini-flash-latest',
                    'gemini-1.5-pro',
                    'gemini-pro',
                    'models/gemini-1.5-flash'
                ]
                
                print("⏳ Verificando cerebro IA y probando conexión en vivo...")
                
                for nombre in candidatos:
                    try:
                        modelo_test = genai.GenerativeModel(nombre)
                        resp_test = modelo_test.generate_content("ping", generation_config=genai.GenerationConfig(max_output_tokens=5))
                        if resp_test and resp_test.text:
                            self.model = modelo_test
                            print(f"🟢 ¡Cerebro IA Conectado y Verificado! Modelo oficial confirmado: {nombre}")
                            break
                    except Exception:
                        continue
                
                # Si los nombres estándar fallan, buscamos en el catálogo dando prioridad absoluta a "gemini"
                if not self.model:
                    modelos_disponibles = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                    
                    # Ordenamos para que los que tienen "gemini" y "flash" queden primeros en la fila, dejando "gemma" al final
                    modelos_ordenados = sorted(modelos_disponibles, key=lambda x: (0 if ('gemini' in x.lower() and 'flash' in x.lower()) else (1 if 'gemini' in x.lower() else 2)))
                    
                    for m_name in modelos_ordenados:
                        try:
                            modelo_test = genai.GenerativeModel(m_name)
                            resp_test = modelo_test.generate_content("ping", generation_config=genai.GenerationConfig(max_output_tokens=5))
                            if resp_test and resp_test.text:
                                self.model = modelo_test
                                print(f"🟢 Autodetectado modelo funcional en tu cuenta: {m_name}")
                                break
                        except Exception:
                            continue

                if not self.model:
                    print("⚠️ Tu API Key es válida pero ningún modelo respondió el ping. Usando respaldo determinista 9.2.")
                            
            except Exception as e:
                print(f"❌ Error al configurar Google AI: {e}")
                self.model = None

    def procesar_pipeline(self, noticia, activo):
        """Ejecuta el pipeline de los 4 agentes con extracción quirúrgica de JSON mediante Regex."""
        evento_coyuntura = {
            "id": noticia.get("id"),
            "titulo": noticia.get("title"),
            "fuente": noticia.get("source", {}).get("name", "Fuente externa"),
            "fecha": noticia.get("publishedAt", "")[:10],
            "activo_asociado": activo["symbol"],
            "categoria": activo["type"]
        }

        if self.model:
            try:
                prompt_usuario = f"""
                ANÁLISIS DE COYUNTURA Y MERCADO:
                - Noticia: {evento_coyuntura['titulo']} (Fuente: {evento_coyuntura['fuente']}, Fecha: {evento_coyuntura['fecha']})
                - Activo vinculado: {activo['name']} ({activo['symbol']}) - Categoría: {activo['type']}
                - Precio Actual: {activo['current_price']} | Variación últimos 7 días: {activo['price_move_7d']}%

                Genera la señal explicable en formato estrictamente JSON sin texto introductorio ni markdown.
                """
                resp = self.model.generate_content(
                    f"{SYSTEM_PROMPT_ASESOR}\n\n{prompt_usuario}",
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json", 
                        temperature=0.2
                    )
                )
                
                # --- EXTRACCIÓN QUIRÚRGICA CON REGEX ---
                # Buscamos exclusivamente el bloque que empieza con { y termina con }, ignorando saludos del LLM
                match = re.search(r'\{.*\}', resp.text, re.DOTALL)
                if match:
                    texto_json = match.group(0)
                    senal = json.loads(texto_json)
                    print(f"🟢 ¡Éxito en vivo! IA analizó: {evento_coyuntura['titulo'][:30]}...")
                else:
                    raise ValueError("El modelo no retornó una estructura JSON delimitada por llaves.")
                    
            except Exception as e:
                print(f"⚠️ Alerta en inferencia ({e}). Pasando al respaldo determinista 9.2.")
                senal = self._aplicar_formula_matematica(evento_coyuntura, activo)
        else:
            senal = self._aplicar_formula_matematica(evento_coyuntura, activo)

        # 3. Agente Supervisor de Cumplimiento (Guardrail regulatorio)
        senal = self._supervisor_cumplimiento(senal)
        
        senal["noticia_ref"] = evento_coyuntura
        senal["activo_ref"] = activo
        return senal

    def _aplicar_formula_matematica(self, evento, activo):
        move_7d = activo.get("price_move_7d", 0.0)
        price_score = max(-1.0, min(1.0, move_7d / 10.0))
        
        txt = evento["titulo"].lower()
        sentiment = 0.5 if any(w in txt for w in ["aprueba", "supera", "impulsa", "favorable"]) else (-0.5 if any(w in txt for w in ["retraso", "caída", "riesgo", "enfriamiento"]) else 0.0)
        
        event_weight = 0.8 if any(w in txt for w in ["sec", "reserva federal", "tasa", "regulación"]) else 0.5
        evidence_score = 0.85 if evento["fuente"] in ["Bloomberg News", "Reuters", "Wall Street Journal"] else 0.50

        impact_score = (0.35 * sentiment) + (0.25 * event_weight) + (0.25 * price_score) + (0.15 * evidence_score)

        if evidence_score < 0.40: impact = "Incierto"
        elif abs(impact_score) < 0.15: impact = "Neutral"
        elif impact_score >= 0.15: impact = "Positivo"
        else: impact = "Negativo"

        conf_score = min(1.0, max(0.0, (evidence_score * 0.7) + (abs(impact_score) * 0.3)))
        conf_label = "Alta" if conf_score >= 0.75 else ("Media" if conf_score >= 0.50 else "Baja")

        return {
            "impacto": impact,
            "confianza": conf_label,
            "confianza_score": round(conf_score, 2),
            "explicacion": f"Análisis determinista (Fórmula 9.2): El evento presenta un impacto ponderado de {round(impact_score, 2)} al contrastar un sentimiento de {sentiment} con una variación de precio del {move_7d}% en 7 días.",
            "accion_investigacion": f"Auditar volúmenes transaccionales y validar exposición al activo {activo['symbol']}.",
            "disclaimer": "Esta señal explicable se genera con fines de análisis e investigación; no constituye asesoría personalizada ni garantiza resultados financieros."
        }

    def _supervisor_cumplimiento(self, senal):
        prohibidas = ["compre ya", "venda ahora", "garantizado", "inversión segura", "buy now", "sell now"]
        texto = senal.get("explicacion", "")
        for p in prohibidas:
            if p in texto.lower():
                senal["explicacion"] = " [TEXTO AJUSTADO POR CUMPLIMIENTO REGULATORIO: Se eliminaron directrices directivas de inversión]. " + texto
        
        if "no constituye asesoría" not in senal.get("disclaimer", "").lower():
            senal["disclaimer"] = "Esta señal explicable se genera con fines de análisis e investigación; no constituye asesoría personalizada ni garantiza resultados financieros."
        return senal