@echo off
echo ============================================
echo   Construyendo LittleStep2.6...
echo ============================================
echo.

cd /d "%~dp0"

echo [1/2] Compilando el ejecutable con PyInstaller...
call venv\Scripts\pyinstaller LittleStep26.spec --noconfirm
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la compilacion del ejecutable.
    pause
    exit /b 1
)

echo.
echo [2/2] Creando el instalador con Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "LittleStep26.iss"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Fallo la creacion del instalador.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Listo! El instalador fue creado en:
echo   installer\LittleStep26_Setup.exe
echo ============================================
pause
