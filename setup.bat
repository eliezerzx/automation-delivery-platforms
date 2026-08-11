@echo off
chcp 65001 >nul
cls

echo ============================================================
echo   Automation Delivery Platforms - Setup
echo          Instalacao completa
echo ============================================================
echo.
echo  Este script vai instalar:
echo    - Python 3.12
echo    - Visual Studio Code
echo    - Git
echo    - Oracle VirtualBox
echo    - Todas as bibliotecas Python necessarias
echo.
echo  Execute como Administrador para melhores resultados.
echo.
pause

set ROOT=%~dp0

:: ============================================================
:: [1] VERIFICAR WINGET
:: ============================================================
echo.
echo [1/5] Verificando winget...
winget --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo  ERRO: winget nao encontrado.
    echo  Atualize o Windows ou instale o App Installer pela Microsoft Store.
    echo.
    pause
    exit /b 1
)
echo  OK - winget disponivel.

:: ============================================================
:: [2] PYTHON 3.12
:: ============================================================
echo.
echo [2/5] Verificando Python 3.12...
py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    echo  OK - Python 3.12 ja instalado.
    goto :PYTHON_OK
)

python --version 2>&1 | findstr "3.12" >nul
if not errorlevel 1 (
    echo  OK - Python 3.12 ja instalado.
    goto :PYTHON_OK
)

echo  Instalando Python 3.12...
winget install --id Python.Python.3.12 --silent --accept-source-agreements --accept-package-agreements
if errorlevel 1 (
    echo.
    echo  AVISO: Falha ao instalar Python via winget.
    echo  Baixe manualmente: https://www.python.org/downloads/release/python-3128/
    echo.
    pause
    exit /b 1
)
echo  Python 3.12 instalado!

:PYTHON_OK

:: ============================================================
:: [3] VISUAL STUDIO CODE
:: ============================================================
echo.
echo [3/5] Verificando Visual Studio Code...
code --version >nul 2>&1
if not errorlevel 1 (
    echo  OK - VS Code ja instalado.
    goto :VSCODE_OK
)

echo  Instalando Visual Studio Code...
winget install --id Microsoft.VisualStudioCode --silent --accept-source-agreements --accept-package-agreements
if errorlevel 1 (
    echo  AVISO: Falha ao instalar VS Code. Baixe em: https://code.visualstudio.com/
) else (
    echo  VS Code instalado!
)

:VSCODE_OK

:: ============================================================
:: [4] GIT
:: ============================================================
echo.
echo [4/7] Verificando Git...
git --version >nul 2>&1
if not errorlevel 1 (
    echo  OK - Git ja instalado.
    goto :GIT_OK
)

echo  Instalando Git...
winget install --id Git.Git --silent --accept-source-agreements --accept-package-agreements
if errorlevel 1 (
    echo  AVISO: Falha ao instalar Git. Baixe em: https://git-scm.com/
) else (
    echo  Git instalado!
)

:GIT_OK

:: ============================================================
:: [5] ORACLE VIRTUALBOX
:: ============================================================
echo.
echo [5/7] Verificando Oracle VirtualBox...
winget list --id Oracle.VirtualBox >nul 2>&1
if not errorlevel 1 (
    echo  OK - VirtualBox ja instalado.
    goto :VBOX_OK
)

echo  Instalando Oracle VirtualBox...
winget install --id Oracle.VirtualBox --silent --accept-source-agreements --accept-package-agreements
if errorlevel 1 (
    echo  AVISO: Falha ao instalar VirtualBox. Baixe em: https://www.virtualbox.org/
) else (
    echo  VirtualBox instalado!
)

:VBOX_OK

:: ============================================================
:: [6] BIBLIOTECAS PYTHON
:: ============================================================
echo.
echo [6/7] Instalando bibliotecas Python...
echo.

py -3.12 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON=py -3.12
) else (
    set PYTHON=python
)

echo  Usando: %PYTHON%
echo.

echo  Atualizando pip...
%PYTHON% -m pip install --upgrade pip --quiet

echo  Instalando bibliotecas...
%PYTHON% -m pip install pyautogui==0.9.54 pyperclip==1.9.0 keyboard==0.13.5 nicegui Pillow pyscreeze opencv-python MouseInfo PyGetWindow PyMsgBox pyRect pytweening

if errorlevel 1 (
    echo.
    echo  AVISO: Algumas bibliotecas podem ter falhado. Veja os erros acima.
) else (
    echo.
    echo  Bibliotecas instaladas com sucesso!
)

:: ============================================================
:: [5] EXTENSOES VS CODE
:: ============================================================
echo.
echo [7/7] Instalando extensoes do VS Code...
code --version >nul 2>&1
if not errorlevel 1 (
    code --install-extension ms-python.python --force >nul 2>&1
    code --install-extension ms-python.vscode-pylance --force >nul 2>&1
    echo  Extensoes Python instaladas.
) else (
    echo  VS Code nao encontrado no PATH ainda.
    echo  Reinicie o PC e as extensoes serao instaladas automaticamente.
)

:: ============================================================
:: CONCLUIDO
:: ============================================================
echo.
echo ============================================================
echo   Setup concluido!
echo.
echo   Proximos passos:
echo   1. Reinicie o computador (recomendado)
echo   2. Abra a pasta no VS Code
echo   3. Ctrl+Shift+P - Python: Select Interpreter - Python 3.12
echo   4. Para rodar: python 99Food/painel/painel_nicegui.py
echo ============================================================
echo.
pause
