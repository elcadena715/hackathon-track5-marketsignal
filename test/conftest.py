import pytest
import json
import os
from datetime import datetime


@pytest.fixture
def sample_noticia():
    """Noticia de ejemplo para pruebas"""
    return {
        "id": "test_1",
        "title": "La SEC aprueba nuevas directrices para Bitcoin",
        "description": "La SEC ha aprobado nuevas regulaciones para custodios de Bitcoin",
        "source": {"name": "Bloomberg News"},
        "publishedAt": "2026-07-11T09:30:00Z",
        "market": "Criptoactivos",
        "related_assets": ["BTC"]
    }


@pytest.fixture
def sample_activo():
    """Activo de ejemplo para pruebas"""
    return {
        "symbol": "BTC",
        "name": "Bitcoin",
        "type": "Criptoactivos",
        "current_price": 65000.0,
        "price_move_7d": 5.2
    }


@pytest.fixture
def invalid_noticia():
    """Noticia inválida para pruebas"""
    return {
        "id": "invalid",
        # Falta título
        "source": {"name": "Unknown"},
    }


@pytest.fixture
def news_feed():
    """Carga el feed de noticias"""
    with open(os.path.join("data", "news_feed.json"), "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def assets_db():
    """Carga la base de activos"""
    with open(os.path.join("data", "assets.json"), "r", encoding="utf-8") as f:
        return json.load(f)
