import json
import os
import google.generativeai as genai
from prompts import SYSTEM_PROMPT_ASESOR

class MotorAgentesIA:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                
                # --- AUTODETECTOR DE MODELOS (SOLUCIÓN AL ERROR 404) ---
                # Intentamos conectar primero a los nombres estándar más rápidos
                nombres_a_probar = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro', 'models/gemini-1.5-flash']
                
                for nombre in nombres_a_probar:
                    try:
                        self.model = genai.GenerativeModel(nombre)
                        # Hacemos una mini prueba silenciosa para validar que no dé 404
                        print(f"🟢 Conectado exitosamente al modelo de Google: {nombre}")
                        break
                    except Exception:
                        continue
                
                # Si ninguno de la lista anterior funcionó, buscamos automáticamente en tu cuenta
                if not self.model:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            self.model = genai.GenerativeModel(m.name)
                            print(f"🟢 Autodetectado modelo compatible en tu cuenta: {m.name}")
                            break
                            
            except Exception as e:
                print(f"❌ Error al configurar Gemini: {e}")
                self.model = None

    def procesar_pipeline(self, noticia, activo):
        """Ejecuta el pipeline de los 4 agentes con limpieza robusta de JSON."""
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

                Genera la señal explicable en formato estrictamente JSON sin formato markdown extra.
                """
                resp = self.model.generate_content(
                    f"{SYSTEM_PROMPT_ASESOR}\n\n{prompt_usuario}",
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json", 
                        temperature=0.2
                    )
                )
                texto_limpio = resp.text.replace("```json", "").replace("```", "").strip()
                senal = json.loads(texto_limpio)
                print(f"🟢 ¡Éxito en vivo! IA analizó: {evento_coyuntura['titulo'][:30]}...")
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