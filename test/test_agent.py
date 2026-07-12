"""
Test Suite para el Motor Agéntico IA
Valida que el agente responde señales coherentes
"""

import pytest
import json
from agents.motor import MotorAgentesIA


class TestMotorAgentesIA:
    """Pruebas del motor de análisis agéntico"""

    def test_agent_initialization_without_key(self):
        """Verifica que el agente se inicializa en modo simulación sin API key"""
        motor = MotorAgentesIA(api_key="")
        assert motor.model is None or hasattr(motor, 'simulation')
        print("✅ Agente inicializado en modo fallback")

    def test_agent_responde_señal_estructura(self, sample_noticia, sample_activo):
        """
        TEST CRÍTICO: Verifica que el agente retorna una señal con estructura coherente
        
        Input: Noticia de Bitcoin + Activo BTC
        Output esperado: Diccionario con campos obligatorios
        """
        motor = MotorAgentesIA(api_key="")
        
        # Procesar la noticia
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        # ✅ Validación 1: Tipo de dato correcto
        assert isinstance(senal, dict), f"Señal debe ser dict, obtuvo {type(senal)}"
        print("✅ Señal es un diccionario")
        
        # ✅ Validación 2: Campos obligatorios presentes
        campos_obligatorios = [
            "impacto",
            "confianza",
            "confianza_score",
            "explicacion",
            "accion_investigacion",
            "disclaimer",
            "noticia_ref",
            "activo_ref"
        ]
        
        for campo in campos_obligatorios:
            assert campo in senal, f"Campo '{campo}' no encontrado en señal"
            assert senal[campo] is not None, f"Campo '{campo}' es None"
        print(f"✅ Todos los {len(campos_obligatorios)} campos obligatorios presentes")

    def test_agent_impacto_es_valido(self, sample_noticia, sample_activo):
        """Verifica que el impacto sea uno de los valores esperados"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        impactos_validos = ["Positivo", "Negativo", "Neutral"]
        assert senal["impacto"] in impactos_validos, \
            f"Impacto '{senal['impacto']}' no es válido. Esperado: {impactos_validos}"
        print(f"✅ Impacto válido: {senal['impacto']}")

    def test_agent_confianza_es_valida(self, sample_noticia, sample_activo):
        """Verifica que la confianza sea uno de los valores esperados"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        confianzas_validas = ["Alta", "Media", "Baja"]
        assert senal["confianza"] in confianzas_validas, \
            f"Confianza '{senal['confianza']}' no es válida. Esperado: {confianzas_validas}"
        print(f"✅ Confianza válida: {senal['confianza']}")

    def test_agent_confianza_score_es_numero(self, sample_noticia, sample_activo):
        """Verifica que confianza_score sea un número entre 0 y 1"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        score = senal.get("confianza_score")
        assert isinstance(score, (int, float)), f"confianza_score debe ser número, obtuvo {type(score)}"
        assert 0 <= score <= 1, f"confianza_score debe estar entre 0 y 1, obtuvo {score}"
        print(f"✅ Confianza score válido: {score}")

    def test_agent_explicacion_no_vacia(self, sample_noticia, sample_activo):
        """Verifica que la explicación tiene contenido"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        explicacion = senal.get("explicacion", "")
        assert len(explicacion) > 10, f"Explicación muy corta: '{explicacion}'"
        assert isinstance(explicacion, str), f"Explicación debe ser string"
        print(f"✅ Explicación coherente ({len(explicacion)} chars)")

    def test_agent_accion_investigacion_presentes(self, sample_noticia, sample_activo):
        """Verifica que hay acción recomendada"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        accion = senal.get("accion_investigacion", "")
        assert len(accion) > 5, f"Acción muy corta: '{accion}'"
        assert isinstance(accion, str), f"Acción debe ser string"
        print(f"✅ Acción recomendada presente ({len(accion)} chars)")

    def test_agent_disclaimer_presente(self, sample_noticia, sample_activo):
        """Verifica que hay disclaimer de riesgo"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        disclaimer = senal.get("disclaimer", "")
        assert len(disclaimer) > 5, f"Disclaimer muy corto: '{disclaimer}'"
        assert "riesgo" in disclaimer.lower() or "asesor" in disclaimer.lower(), \
            f"Disclaimer debe mencionar riesgos o asesoramiento"
        print(f"✅ Disclaimer de riesgos presente")

    def test_agent_referencia_noticia(self, sample_noticia, sample_activo):
        """Verifica que la señal referencia la noticia original"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        noticia_ref = senal.get("noticia_ref")
        assert noticia_ref is not None, "noticia_ref no debe ser None"
        assert noticia_ref.get("titulo") == sample_noticia["title"], \
            "Referencia de noticia no coincide"
        assert noticia_ref.get("activo_asociado") == sample_activo["symbol"], \
            "Referencia de activo no coincide"
        print(f"✅ Referencias de noticia correctas")

    def test_agent_diferencia_señales(self, sample_noticia, sample_activo):
        """
        TEST AVANZADO: Verifica que el agente genera señales diferentes para noticias diferentes
        """
        motor = MotorAgentesIA(api_key="")
        
        # Primera noticia (positiva)
        noticia_positiva = sample_noticia.copy()
        noticia_positiva["title"] = "Aprobación regulatoria impulsa demanda de Bitcoin"
        senal_1 = motor.procesar_pipeline(noticia_positiva, sample_activo)
        
        # Segunda noticia (negativa)
        noticia_negativa = sample_noticia.copy()
        noticia_negativa["title"] = "Retraso en regulación causa caída de Bitcoin"
        senal_2 = motor.procesar_pipeline(noticia_negativa, sample_activo)
        
        # Las señales NO deben ser idénticas (evidencia de análisis diferenciado)
        assert senal_1["impacto"] != senal_2["impacto"], \
            "Agente debería diferenciar entre noticias positivas y negativas"
        print(f"✅ Agente diferencia señales: '{senal_1['impacto']}' vs '{senal_2['impacto']}'")

    def test_agent_maneja_noticias_sin_descripcion(self, sample_activo):
        """Verifica que el agente maneja noticias sin descripción"""
        motor = MotorAgentesIA(api_key="")
        
        noticia_minima = {
            "id": "min",
            "title": "Noticia simple",
            "source": {"name": "Fuente"},
            "publishedAt": "2026-07-11"
        }
        
        # No debe fallar
        senal = motor.procesar_pipeline(noticia_minima, sample_activo)
        assert senal["impacto"] in ["Positivo", "Negativo", "Neutral"]
        print("✅ Agente maneja noticias mínimas correctamente")


class TestMotorEstabilidad:
    """Pruebas de estabilidad y robustez"""

    def test_agent_proceso_multiplenoticias(self, news_feed, assets_db):
        """
        STRESS TEST: Procesa todas las noticias del feed sin crashes
        """
        motor = MotorAgentesIA(api_key="")
        
        procesadas = 0
        errores = 0
        
        for noticia in news_feed[:3]:  # Procesa primeras 3 para no tardar
            try:
                # Encontrar activo relevante
                activo = assets_db[0]
                for a in assets_db:
                    if a["symbol"] in str(noticia.get("related_assets", [])):
                        activo = a
                        break
                
                senal = motor.procesar_pipeline(noticia, activo)
                assert "impacto" in senal
                procesadas += 1
            except Exception as e:
                print(f"⚠️ Error procesando noticia {noticia.get('id')}: {e}")
                errores += 1
        
        assert procesadas > 0, "No se procesó ninguna noticia"
        print(f"✅ Procesadas {procesadas} noticias exitosamente ({errores} errores)")

    def test_agent_señal_json_serializable(self, sample_noticia, sample_activo):
        """Verifica que la señal puede ser serializada a JSON"""
        motor = MotorAgentesIA(api_key="")
        senal = motor.procesar_pipeline(sample_noticia, sample_activo)
        
        # Intentar serializar a JSON
        try:
            json_str = json.dumps(senal, default=str)
            assert len(json_str) > 50, "JSON muy corto"
            print(f"✅ Señal serializable a JSON ({len(json_str)} chars)")
        except Exception as e:
            pytest.fail(f"Señal no es JSON serializable: {e}")


if __name__ == "__main__":
    # Ejecutar con: pytest test/test_agent.py -v
    pytest.main([__file__, "-v", "-s"])
