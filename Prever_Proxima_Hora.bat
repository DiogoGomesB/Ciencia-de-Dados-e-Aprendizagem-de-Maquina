@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual e instalando dependencias ^(so na primeira vez^)...
    py -3.13 -m venv .venv 2>nul || py -3 -m venv .venv 2>nul || python -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        echo ERRO: Python nao encontrado. Instale o Python 3.13 e tente de novo.
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo.
echo Buscando dados recentes e prevendo a proxima hora...
echo.
".venv\Scripts\python.exe" -m src.aplicacao.Prever_Proxima_Hora
if errorlevel 1 (
    echo.
    echo ERRO: a previsao falhou. Verifique a conexao com a internet e tente novamente.
)
echo.
pause
