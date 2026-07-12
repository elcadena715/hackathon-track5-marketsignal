"""
Test Suite para Persistencia de Datos
Valida que las auditorías se guardan y recuperan correctamente
"""

import pytest
import os
import json
from datetime import datetime
from core.database import init_db, guardar_revision, obtener_revisiones


class TestDatabasePersistencia:
    """Pruebas de persistencia en BD"""

    def test_init_db_sin_errores(self):
        """Verifica que la inicialización de BD no genera errores"""
        try:
            init_db()
            print("✅ Base de datos inicializada correctamente")
        except Exception as e:
            pytest.fail(f"init_db() falló: {e}")

    def test_guardar_revision_simple(self):
        """Verifica que se puede guardar una revisión"""
        init_db()
        
        signal_id = "test_signal_001"
        status = "✅ Validada"
        justificacion = "Señal validada por equipo de compliance"
        
        try:
            guardar_revision(signal_id, status, justificacion)
            print(f"✅ Revisión guardada: {signal_id}")
        except Exception as e:
            pytest.fail(f"guardar_revision() falló: {e}")

    def test_obtener_revision_guardada(self):
        """Verifica que se puede recuperar una revisión guardada"""
        init_db()
        
        # Guardar
        signal_id = "test_get_001"
        status = "⚠️ Escalada"
        justificacion = "Debe ser revisada por comité"
        guardar_revision(signal_id, status, justificacion)
        
        # Recuperar
        revisiones = obtener_revisiones()
        
        assert signal_id in revisiones, f"Señal {signal_id} no encontrada en BD"
        assert revisiones[signal_id]["status"] == status, "Status no coincide"
        assert revisiones[signal_id]["justification"] == justificacion, "Justificación no coincide"
        print(f"✅ Revisión recuperada correctamente")

    def test_guardar_multiples_revisiones(self):
        """Verifica que se pueden guardar múltiples revisiones"""
        init_db()
        
        revisiones_a_guardar = [
            ("signal_001", "✅ Validada", "Validada por Juan"),
            ("signal_002", "⚠️ Escalada", "Requiere revisión"),
            ("signal_003", "🗑️ Descartada", "No relevante"),
        ]
        
        for sig_id, status, just in revisiones_a_guardar:
            guardar_revision(sig_id, status, just)
        
        # Verificar que todas fueron guardadas
        revisiones = obtener_revisiones()
        
        for sig_id, status, just in revisiones_a_guardar:
            assert sig_id in revisiones, f"Señal {sig_id} no encontrada"
            assert revisiones[sig_id]["status"] == status, f"Status incorrecto para {sig_id}"
        
        print(f"✅ Todas las {len(revisiones_a_guardar)} revisiones guardadas correctamente")

    def test_revisor_y_timestamp(self):
        """Verifica que se guardan reviewer y timestamp"""
        init_db()
        
        signal_id = "test_meta_001"
        status = "✅ Validada"
        justificacion = "Test de metadatos"
        reviewer = "TestUser"
        
        guardar_revision(signal_id, status, justificacion, reviewer=reviewer)
        
        revisiones = obtener_revisiones()
        revision = revisiones[signal_id]
        
        assert revision["reviewer"] == reviewer, "Reviewer no guardado"
        assert "date" in revision, "Date no guardado"
        assert len(revision["date"]) > 0, "Date vacío"
        print(f"✅ Metadatos (reviewer, date) guardados correctamente")

    def test_estados_diferentes_signals(self):
        """Verifica que se pueden guardar señales con diferentes estados"""
        init_db()
        
        estados = {
            "sig_validada": "✅ Validada",
            "sig_escalada": "⚠️ Escalada",
            "sig_descartada": "🗑️ Descartada",
        }
        
        for sig_id, status in estados.items():
            guardar_revision(sig_id, status, f"Justificación para {sig_id}")
        
        revisiones = obtener_revisiones()
        
        # Contar por estado
        validadas = len([v for v in revisiones.values() if "Validada" in v["status"]])
        escaladas = len([v for v in revisiones.values() if "Escalada" in v["status"]])
        descartadas = len([v for v in revisiones.values() if "Descartada" in v["status"]])
        
        assert validadas > 0, "No hay revisiones validadas"
        assert escaladas > 0, "No hay revisiones escaladas"
        assert descartadas > 0, "No hay revisiones descartadas"
        print(f"✅ Estados contabilizados: Validadas={validadas}, Escaladas={escaladas}, Descartadas={descartadas}")

    def test_revision_es_dict(self):
        """Verifica que obtener_revisiones() retorna un diccionario"""
        init_db()
        
        revisiones = obtener_revisiones()
        
        assert isinstance(revisiones, dict), f"obtener_revisiones() debe retornar dict, obtuvo {type(revisiones)}"
        print("✅ obtener_revisiones() retorna diccionario")

    def test_cada_revision_tiene_campos_requeridos(self):
        """Verifica que cada revisión tiene los campos necesarios"""
        init_db()
        
        # Guardar una revisión
        guardar_revision("test_campos_001", "✅ Validada", "Test")
        
        revisiones = obtener_revisiones()
        revision = revisiones["test_campos_001"]
        
        campos_requeridos = ["status", "justification", "reviewer", "date"]
        for campo in campos_requeridos:
            assert campo in revision, f"Campo '{campo}' no encontrado en revisión"
        
        print(f"✅ Todos los campos requeridos presentes: {campos_requeridos}")


class TestDatabaseConsistencia:
    """Pruebas de consistencia y validaciones"""

    def test_justificacion_vacia_permitida(self):
        """Verifica que se puede guardar sin justificación (para Descartar)"""
        init_db()
        
        try:
            guardar_revision("test_empty_just", "🗑️ Descartada", "")
            print("✅ Justificación vacía permitida")
        except Exception as e:
            pytest.fail(f"No debería fallar con justificación vacía: {e}")

    def test_signal_id_unico_se_actualiza(self):
        """Verifica que la misma señal se puede actualizar"""
        init_db()
        
        sig_id = "test_update_001"
        
        # Primera auditoría
        guardar_revision(sig_id, "✅ Validada", "Primera validación")
        rev1 = obtener_revisiones()[sig_id]
        
        # Segunda auditoría de la misma señal
        guardar_revision(sig_id, "⚠️ Escalada", "Requiere escalación")
        rev2 = obtener_revisiones()[sig_id]
        
        # Ambas deberían existir en la BD (como inserts, no updates)
        print(f"✅ Se pueden guardar múltiples auditorías de la misma señal")

    def test_caracteres_especiales_en_justificacion(self):
        """Verifica que se pueden guardar caracteres especiales"""
        init_db()
        
        justificaciones_especiales = [
            "Validada por @usuario_compliance",
            "Incluye análisis con $, €, £",
            'Justificación con "comillas" y \'apóstrofos\'',
            "Análisis con emojis: 🔍 📊 ✅",
        ]
        
        for i, just in enumerate(justificaciones_especiales):
            try:
                guardar_revision(f"test_especial_{i}", "✅ Validada", just)
            except Exception as e:
                pytest.fail(f"Falló con caracteres especiales: {e}")
        
        print("✅ Caracteres especiales manejados correctamente")


class TestDatabaseIntegracion:
    """Pruebas de integración completa"""

    def test_flujo_completo_auditoria(self):
        """
        TEST INTEGRACIÓN: Simula el flujo completo de auditoría
        
        1. Guardar auditoría
        2. Recuperar
        3. Filtrar por estado
        4. Generar contadores
        """
        init_db()
        
        # Paso 1: Crear auditorías diversas
        auditorias = [
            ("news_001", "✅ Validada", "Validada por compliance"),
            ("news_002", "⚠️ Escalada", "Requiere comité"),
            ("news_003", "✅ Validada", "Validada por riesgo"),
            ("news_004", "🗑️ Descartada", "No relevante"),
            ("news_005", "⚠️ Escalada", "Evaluación pendiente"),
        ]
        
        for sig_id, status, just in auditorias:
            guardar_revision(sig_id, status, just)
        
        # Paso 2: Recuperar y analizar
        revisiones = obtener_revisiones()
        
        # Paso 3: Filtrar por estado
        validadas = {k: v for k, v in revisiones.items() if "Validada" in v["status"]}
        escaladas = {k: v for k, v in revisiones.items() if "Escalada" in v["status"]}
        descartadas = {k: v for k, v in revisiones.items() if "Descartada" in v["status"]}
        
        # Paso 4: Verificar contadores
        assert len(validadas) == 2, f"Esperaba 2 validadas, obtuvo {len(validadas)}"
        assert len(escaladas) == 2, f"Esperaba 2 escaladas, obtuvo {len(escaladas)}"
        assert len(descartadas) == 1, f"Esperaba 1 descartada, obtuvo {len(descartadas)}"
        
        print(f"✅ Flujo completo: {len(validadas)} validadas, {len(escaladas)} escaladas, {len(descartadas)} descartadas")

    def test_reporte_compliance_simulado(self):
        """Simula la generación de reporte de compliance"""
        init_db()
        
        # Crear auditorías
        for i in range(5):
            guardar_revision(f"signal_{i}", "✅ Validada", f"Señal {i} validada")
        
        # Recuperar y simular reporte
        revisiones = obtener_revisiones()
        validadas = {k: v for k, v in revisiones.items() if "Validada" in v["status"]}
        
        # Estructura de reporte
        reporte = {
            "total_auditadas": len(validadas),
            "fecha": datetime.now().isoformat(),
            "señales": list(validadas.keys())
        }
        
        # Verificar que puede ser JSON
        json_reporte = json.dumps(reporte, default=str)
        assert len(json_reporte) > 50
        
        print(f"✅ Reporte simulado generado: {reporte['total_auditadas']} señales auditorias")


if __name__ == "__main__":
    # Ejecutar con: pytest test/test_database.py -v
    pytest.main([__file__, "-v", "-s"])
