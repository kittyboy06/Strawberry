@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"

echo ============================================================
echo   Strawberry Windows Release ^& Installer Builder
echo ============================================================
echo.

where uv >nul 2>nul
if errorlevel 1 (
    echo [ERROR] 'uv' is not installed or not in PATH.
    pause
    exit /b 1
)

REM Locate Inno Setup Compiler (ISCC.exe)
set "ISCC_CMD="
where iscc >nul 2>nul
if not errorlevel 1 (
    set "ISCC_CMD=iscc"
)
if not defined ISCC_CMD if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_CMD=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
)
if not defined ISCC_CMD if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC_CMD=%ProgramFiles%\Inno Setup 6\ISCC.exe"
)
if not defined ISCC_CMD if exist "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" (
    set "ISCC_CMD=%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"
)
if not defined ISCC_CMD (
    echo [ERROR] Inno Setup 6 ^(ISCC.exe^) not found. Install via:
    echo         winget install JRSoftware.InnoSetup
    pause
    exit /b 1
)

echo [1/4] Running strawberry-cli automated test suite...
pushd "%~dp0strawberry-cli"
call uv run pytest -v
if errorlevel 1 (
    popd
    echo [ERROR] Unit tests failed. Release aborted.
    pause
    exit /b 1
)

echo.
echo [2/4] Building standalone executable ^(strawberry.exe^)...
if not exist ".venv\Scripts\pyinstaller.exe" (
    call uv pip install pyinstaller
)
call .\.venv\Scripts\pyinstaller.exe --onefile --name strawberry --paths src --clean src\strawberry_cli\main.py
if errorlevel 1 (
    popd
    echo [ERROR] PyInstaller build failed.
    pause
    exit /b 1
)
popd

echo.
echo [3/4] Staging public client config ^(URL + Publishable Key only^)...
set "PUB_URL="
set "PUB_KEY="
if exist "%~dp0.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do (
        set "K=%%A"
        set "V=%%B"
        if /i "!K!"=="STRAWBERRY_SUPABASE_URL" set "PUB_URL=!V!"
        if /i "!K!"=="VITE_SUPABASE_URL" if not defined PUB_URL set "PUB_URL=!V!"
        if /i "!K!"=="STRAWBERRY_SUPABASE_PUBLISHABLE_KEY" set "PUB_KEY=!V!"
        if /i "!K!"=="VITE_SUPABASE_PUBLISHABLE_KEY" if not defined PUB_KEY set "PUB_KEY=!V!"
    )
)

if not defined PUB_URL (
    echo [ERROR] Missing STRAWBERRY_SUPABASE_URL in root .env
    pause
    exit /b 1
)
if not defined PUB_KEY (
    echo [ERROR] Missing STRAWBERRY_SUPABASE_PUBLISHABLE_KEY in root .env
    pause
    exit /b 1
)

set "STAGED_ENV=%~dp0installer\.env.student"
(
    echo STRAWBERRY_SUPABASE_URL=!PUB_URL!
    echo STRAWBERRY_SUPABASE_PUBLISHABLE_KEY=!PUB_KEY!
) > "!STAGED_ENV!"

echo.
echo [4/4] Compiling Strawberry_Setup.exe via Inno Setup...
call "!ISCC_CMD!" "%~dp0installer\strawberry.iss"
set "ISCC_ERR=%errorlevel%"

if exist "!STAGED_ENV!" del /f /q "!STAGED_ENV!" >nul 2>nul

if not "!ISCC_ERR!"=="0" (
    echo [ERROR] Inno Setup compilation failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Release Build Complete:
echo   - Executable: strawberry-cli\dist\strawberry.exe
echo   - Installer:  dist\Strawberry_Setup.exe
echo ============================================================
if not defined STRAWBERRY_BATCH_NOPAUSE pause
exit /b 0
