"""
Test Suite para Datos (News Feed y Assets)
Valida que los JSONs tienen estructura correcta
"""

import pytest
import json
import os


class TestNewsFeed:
    """Pruebas del feed de noticias"""

    def test_news_feed_existe(self):
        """Verifica que el archivo news_feed.json existe"""
        path = os.path.join("data", "news_feed.json")
        assert os.path.exists(path), f"Archivo {path} no existe"
        print(f"✅ Archivo {path} existe")

    def test_news_feed_es_json_valido(self):
        """Verifica que news_feed.json es JSON válido"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            try:
                noticias = json.load(f)
                assert isinstance(noticias, list), "news_feed.json debe ser un array"
                print(f"✅ news_feed.json es JSON válido ({len(noticias)} noticias)")
            except json.JSONDecodeError as e:
                pytest.fail(f"news_feed.json tiene JSON inválido: {e}")

    def test_cada_noticia_tiene_campos_requeridos(self):
        """Verifica que cada noticia tiene los campos obligatorios"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        campos_requeridos = ["id", "title", "description", "source", "publishedAt", "market", "related_assets"]
        
        for noticia in noticias:
            for campo in campos_requeridos:
                assert campo in noticia, f"Noticia {noticia.get('id')} falta campo '{campo}'"
                assert noticia[campo] is not None, f"Campo '{campo}' en {noticia.get('id')} es None"
        
        print(f"✅ Todas las {len(noticias)} noticias tienen campos requeridos")

    def test_noticia_tiene_descripcion_completa(self):
        """Verifica que las descripciones no están vacías"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        for noticia in noticias:
            desc = noticia.get("description", "")
            assert len(desc) > 20, f"Noticia '{noticia['id']}' tiene descripción muy corta ({len(desc)} chars)"
            assert "." in desc or "," in desc, f"Noticia '{noticia['id']}' no tiene puntuación"
        
        print(f"✅ Todas las descripciones son completas (mínimo 20 caracteres)")

    def test_noticia_tiene_activos_relacionados(self):
        """Verifica que cada noticia menciona activos"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        for noticia in noticias:
            assets = noticia.get("related_assets", [])
            assert len(assets) > 0, f"Noticia '{noticia['id']}' no tiene activos relacionados"
            assert isinstance(assets, list), f"related_assets debe ser lista"
        
        print(f"✅ Todas las noticias tienen activos relacionados")

    def test_noticia_tiene_mercado_valido(self):
        """Verifica que el mercado es válido"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        mercados_validos = ["Monedas", "Acciones", "Criptoactivos", "ETFs", "Bonos", "Materias Primas"]
        
        for noticia in noticias:
            market = noticia.get("market")
            assert market in mercados_validos, \
                f"Noticia '{noticia['id']}' tiene mercado inválido: {market}"
        
        print(f"✅ Todos los mercados son válidos")

    def test_noticia_tiene_fecha_valida(self):
        """Verifica que las fechas están en formato ISO"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        for noticia in noticias:
            fecha = noticia.get("publishedAt", "")
            # Verificar formato ISO 8601
            assert "T" in fecha or "-" in fecha, f"Fecha '{fecha}' no está en formato ISO"
            assert len(fecha) >= 10, f"Fecha '{fecha}' muy corta"
        
        print(f"✅ Todas las fechas están en formato válido")

    def test_noticia_tiene_fuente_valida(self):
        """Verifica que la fuente está presente"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        for noticia in noticias:
            source = noticia.get("source", {})
            assert isinstance(source, dict), "source debe ser diccionario"
            assert "name" in source, f"source en '{noticia['id']}' sin campo 'name'"
            assert len(source["name"]) > 0, f"source name en '{noticia['id']}' está vacío"
        
        print(f"✅ Todas las fuentes son válidas")

    def test_no_duplicados_en_news_feed(self):
        """Verifica que no hay IDs duplicados"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        ids = [n.get("id") for n in noticias]
        duplicados = [id for id in ids if ids.count(id) > 1]
        
        assert len(duplicados) == 0, f"Hay IDs duplicados: {set(duplicados)}"
        print(f"✅ No hay noticias duplicadas (IDs únicos)")


class TestAssetsDB:
    """Pruebas de la base de activos"""

    def test_assets_existe(self):
        """Verifica que el archivo assets.json existe"""
        path = os.path.join("data", "assets.json")
        assert os.path.exists(path), f"Archivo {path} no existe"
        print(f"✅ Archivo {path} existe")

    def test_assets_es_json_valido(self):
        """Verifica que assets.json es JSON válido"""
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            try:
                activos = json.load(f)
                assert isinstance(activos, list), "assets.json debe ser un array"
                print(f"✅ assets.json es JSON válido ({len(activos)} activos)")
            except json.JSONDecodeError as e:
                pytest.fail(f"assets.json tiene JSON inválido: {e}")

    def test_activo_tiene_campos_requeridos(self):
        """Verifica que cada activo tiene campos obligatorios"""
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            activos = json.load(f)
        
        campos_requeridos = ["symbol", "name", "type", "current_price", "price_move_7d"]
        
        for activo in activos:
            for campo in campos_requeridos:
                assert campo in activo, f"Activo {activo.get('symbol')} falta campo '{campo}'"
        
        print(f"✅ Todos los {len(activos)} activos tienen campos requeridos")

    def test_precio_es_numero(self):
        """Verifica que los precios son números"""
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            activos = json.load(f)
        
        for activo in activos:
            price = activo.get("current_price")
            assert isinstance(price, (int, float)), \
                f"current_price en {activo['symbol']} debe ser número, es {type(price)}"
            assert price > 0, f"current_price en {activo['symbol']} debe ser positivo"
        
        print(f"✅ Todos los precios son válidos (positivos y numéricos)")

    def test_price_move_es_numero(self):
        """Verifica que price_move_7d es número"""
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            activos = json.load(f)
        
        for activo in activos:
            move = activo.get("price_move_7d")
            assert isinstance(move, (int, float)), \
                f"price_move_7d en {activo['symbol']} debe ser número"
        
        print(f"✅ Todos los price_move_7d son válidos")

    def test_tipo_activo_valido(self):
        """Verifica que el tipo de activo es válido"""
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            activos = json.load(f)
        
        tipos_validos = ["Monedas", "Acciones", "Criptoactivos", "ETFs", "Bonos", "Materias Primas"]
        
        for activo in activos:
            tipo = activo.get("type")
            assert tipo in tipos_validos, \
                f"Activo {activo['symbol']} tiene tipo inválido: {tipo}"
        
        print(f"✅ Todos los tipos de activo son válidos")

    def test_symbol_unico(self):
        """Verifica que los símbolos son únicos"""
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            activos = json.load(f)
        
        symbols = [a.get("symbol") for a in activos]
        duplicados = [s for s in symbols if symbols.count(s) > 1]
        
        assert len(duplicados) == 0, f"Hay símbolos duplicados: {set(duplicados)}"
        print(f"✅ Todos los símbolos son únicos")


class TestDataIntegracion:
    """Pruebas de integración entre noticias y activos"""

    def test_activos_en_noticias_existen(self):
        """Verifica que los activos mencionados en noticias existen en assets.json"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            activos = json.load(f)
        
        simbolos_activos = [a["symbol"] for a in activos]
        
        for noticia in noticias:
            activos_rel = noticia.get("related_assets", [])
            for sym in activos_rel:
                assert sym in simbolos_activos, \
                    f"Noticia '{noticia['id']}' menciona activo '{sym}' que no existe en assets.json"
        
        print(f"✅ Todos los activos mencionados en noticias existen en assets.json")

    def test_mercado_noticia_coincide_tipo_activo(self):
        """Verifica que el mercado de la noticia coincide con el tipo del activo"""
        with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
            noticias = json.load(f)
        
        with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
            activos = json.load(f)
        
        activos_por_symbol = {a["symbol"]: a for a in activos}
        
        for noticia in noticias:
            mercado_noticia = noticia.get("market")
            for sym in noticia.get("related_assets", []):
                activo = activos_por_symbol.get(sym)
                if activo:
                    tipo_activo = activo.get("type")
                    assert tipo_activo == mercado_noticia or mercado_noticia == "Todos", \
                        f"Mercado de noticia '{mercado_noticia}' no coincide con tipo activo '{tipo_activo}' ({sym})"
        
        print(f"✅ Mercados de noticias coinciden con tipos de activos")


if __name__ == "__main__":
    # Ejecutar con: pytest test/test_news_feed.py -v
    pytest.main([__file__, "-v", "-s"])
