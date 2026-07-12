#!/bin/bash
# Script para ejecutar tests

echo "🧪 MarketSignal Guardian - Test Suite"
echo "======================================"
echo ""

if [ "$1" == "agent" ]; then
    echo "📡 Ejecutando tests del AGENTE IA..."
    pytest test/test_agent.py -v -s

elif [ "$1" == "database" ]; then
    echo "💾 Ejecutando tests de BASE DE DATOS..."
    pytest test/test_database.py -v -s

elif [ "$1" == "data" ]; then
    echo "📊 Ejecutando tests de DATOS..."
    pytest test/test_news_feed.py -v -s

elif [ "$1" == "all" ]; then
    echo "🔬 Ejecutando TODOS los tests..."
    pytest test/ -v --tb=short

else
    echo "Uso: ./run_tests.sh [agent|database|data|all]"
    echo ""
    echo "Opciones:"
    echo "  agent     - Tests del motor agéntico (recomendado primero)"
    echo "  database  - Tests de persistencia en BD"
    echo "  data      - Tests de integridad de datos (JSON)"
    echo "  all       - Todos los tests"
    echo ""
    echo "Ejemplo:"
    echo "  ./run_tests.sh agent"
    exit 1
fi
