@echo off
echo ================================================
echo   Automation Delivery Platforms — Setup
echo ================================================
echo.

set ROOT=%~dp0

:: ── 99Food ──────────────────────────────────────
echo [1/3] Configurando 99Food...
cd /d "%ROOT%99Food"
python -m venv venv
call venv\Scripts\activate
pip install pyautogui pyperclip keyboard nicegui Pillow
call venv\Scripts\deactivate
echo.

:: ── iFood ───────────────────────────────────────
echo [2/3] Configurando iFood...
cd /d "%ROOT%ifood"
python -m venv venv
call venv\Scripts\activate
pip install pyautogui pyperclip keyboard nicegui Pillow
call venv\Scripts\deactivate
echo.

:: ── Keeta ───────────────────────────────────────
echo [3/3] Configurando Keeta...
cd /d "%ROOT%Keeta"
python -m venv venv
call venv\Scripts\activate
pip install pyautogui pyperclip keyboard nicegui Pillow
call venv\Scripts\deactivate
echo.

echo ================================================
echo   Tudo pronto! Abra cada projeto no VSCode e
echo   selecione o interpretador: .\venv\Scripts\python.exe
echo ================================================
pause
