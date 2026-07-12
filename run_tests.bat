@echo off
REM Script para ejecutar tests en Windows

echo.
echo 🧪 MarketSignal Guardian - Test Suite
echo ======================================
echo.

if "%1%"=="agent" (
    echo 📡 Ejecutando tests del AGENTE IA...
    pytest test/test_agent.py -v -s

) else if "%1%"=="database" (
    echo 💾 Ejecutando tests de BASE DE DATOS...
    pytest test/test_database.py -v -s

) else if "%1%"=="data" (
    echo 📊 Ejecutando tests de DATOS...
    pytest test/test_news_feed.py -v -s

) else if "%1%"=="all" (
    echo 🔬 Ejecutando TODOS los tests...
    pytest test/ -v --tb=short

) else (
    echo Uso: run_tests.bat [agent^|database^|data^|all]
    echo.
    echo Opciones:
    echo   agent     - Tests del motor agéntico (recomendado primero)
    echo   database  - Tests de persistencia en BD
    echo   data      - Tests de integridad de datos (JSON)
    echo   all       - Todos los tests
    echo.
    echo Ejemplo:
    echo   run_tests.bat agent
    exit /b 1
)
