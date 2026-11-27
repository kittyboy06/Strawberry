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
    if not defined STRAWBERRY_BATCH_NOPAUSE pause
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
    if not defined STRAWBERRY_BATCH_NOPAUSE pause
    exit /b 1
)

echo [1/5] Running strawberry-cli automated test suite...
pushd "%~dp0strawberry-cli"
call uv run pytest -v
if errorlevel 1 (
    popd
    echo [ERROR] Unit tests failed. Release aborted.
    if not defined STRAWBERRY_BATCH_NOPAUSE pause
    exit /b 1
)

echo.
echo [2/5] Building standalone executable ^(strawberry.exe^)...
if not exist ".venv\Scripts\pyinstaller.exe" (
    call uv pip install pyinstaller
)
call .\.venv\Scripts\pyinstaller.exe --onefile --name strawberry --paths src --icon ..\installer\strawberry.ico --version-file ..\installer\version_info.txt --clean src\strawberry_cli\main.py
if errorlevel 1 (
    popd
    echo [ERROR] PyInstaller build failed.
    if not defined STRAWBERRY_BATCH_NOPAUSE pause
    exit /b 1
)
popd

echo.
echo [3/5] Staging public client config ^(URL + Publishable Key only^)...
set "PUB_URL="
set "PUB_KEY="
set "AZ_EP=!AZURE_SIGNING_ENDPOINT!"
set "AZ_ACC=!AZURE_SIGNING_ACCOUNT!"
set "AZ_PROF=!AZURE_SIGNING_PROFILE!"
if exist "%~dp0.env" (
    for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0.env") do (
        set "K=%%A"
        set "V=%%B"
        if /i "!K!"=="STRAWBERRY_SUPABASE_URL" set "PUB_URL=!V!"
        if /i "!K!"=="VITE_SUPABASE_URL" if not defined PUB_URL set "PUB_URL=!V!"
        if /i "!K!"=="STRAWBERRY_SUPABASE_PUBLISHABLE_KEY" set "PUB_KEY=!V!"
        if /i "!K!"=="VITE_SUPABASE_PUBLISHABLE_KEY" if not defined PUB_KEY set "PUB_KEY=!V!"
        if /i "!K!"=="AZURE_SIGNING_ENDPOINT" if not defined AZ_EP set "AZ_EP=!V!"
        if /i "!K!"=="AZURE_SIGNING_ACCOUNT" if not defined AZ_ACC set "AZ_ACC=!V!"
        if /i "!K!"=="AZURE_SIGNING_PROFILE" if not defined AZ_PROF set "AZ_PROF=!V!"
    )
)

if not defined PUB_URL (
    echo [ERROR] Missing STRAWBERRY_SUPABASE_URL in root .env
    if not defined STRAWBERRY_BATCH_NOPAUSE pause
    exit /b 1
)
if not defined PUB_KEY (
    echo [ERROR] Missing STRAWBERRY_SUPABASE_PUBLISHABLE_KEY in root .env
    if not defined STRAWBERRY_BATCH_NOPAUSE pause
    exit /b 1
)

set "CAN_SIGN=0"
set "SIGNTOOL_CMD="
set "AZ_DLIB=%LOCALAPPDATA%\Microsoft\MicrosoftTrustedSigningClientTools\x64\Azure.CodeSigning.Dlib.dll"
if defined AZURE_SIGNING_DLIB set "AZ_DLIB=%AZURE_SIGNING_DLIB%"
for /f "delims=" %%S in ('where signtool 2^>nul') do if not defined SIGNTOOL_CMD set "SIGNTOOL_CMD=%%S"
if not defined SIGNTOOL_CMD (
    for /d %%D in ("%ProgramFiles(x86)%\Windows Kits\10\bin\*") do (
        if exist "%%~D\x64\signtool.exe" set "SIGNTOOL_CMD=%%~D\x64\signtool.exe"
    )
)
if defined AZ_EP if defined AZ_ACC if defined AZ_PROF if exist "!AZ_DLIB!" if defined SIGNTOOL_CMD set "CAN_SIGN=1"

set "SIGN_META=%~dp0installer\.signing-metadata.json"
if "!CAN_SIGN!"=="1" (
    echo Signing standalone strawberry.exe via Azure Trusted Signing...
    (
        echo {
        echo   "Endpoint": "!AZ_EP!",
        echo   "CodeSigningAccountName": "!AZ_ACC!",
        echo   "CertificateProfileName": "!AZ_PROF!"
        echo }
    ) > "!SIGN_META!"
    call "!SIGNTOOL_CMD!" sign /v /fd SHA256 /tr "http://timestamp.acs.microsoft.com" /td SHA256 /dlib "!AZ_DLIB!" /dmdf "!SIGN_META!" "%~dp0strawberry-cli\dist\strawberry.exe"
    if errorlevel 1 (
        del /f /q "!SIGN_META!" >nul 2>nul
        echo [ERROR] Signing strawberry.exe failed.
        if not defined STRAWBERRY_BATCH_NOPAUSE pause
        exit /b 1
    )
)

set "STAGED_ENV=%~dp0installer\.env.student"
(
    echo STRAWBERRY_SUPABASE_URL=!PUB_URL!
    echo STRAWBERRY_SUPABASE_PUBLISHABLE_KEY=!PUB_KEY!
) > "!STAGED_ENV!"

echo.
echo [4/5] Compiling Strawberry_Setup.exe via Inno Setup...
call "!ISCC_CMD!" "%~dp0installer\strawberry.iss"
set "ISCC_ERR=%errorlevel%"

if exist "!STAGED_ENV!" del /f /q "!STAGED_ENV!" >nul 2>nul

if not "!ISCC_ERR!"=="0" (
    if exist "!SIGN_META!" del /f /q "!SIGN_META!" >nul 2>nul
    echo [ERROR] Inno Setup compilation failed.
    if not defined STRAWBERRY_BATCH_NOPAUSE pause
    exit /b 1
)

echo.
echo [5/5] Finalizing code signature...
if "!CAN_SIGN!"=="1" (
    call "!SIGNTOOL_CMD!" sign /v /fd SHA256 /tr "http://timestamp.acs.microsoft.com" /td SHA256 /dlib "!AZ_DLIB!" /dmdf "!SIGN_META!" "%~dp0dist\Strawberry_Setup.exe"
    set "SIGN_ERR=!errorlevel!"
    if exist "!SIGN_META!" del /f /q "!SIGN_META!" >nul 2>nul
    if not "!SIGN_ERR!"=="0" (
        echo [ERROR] Signing Strawberry_Setup.exe failed.
        if not defined STRAWBERRY_BATCH_NOPAUSE pause
        exit /b 1
    )
) else (
    echo [INFO] Azure Trusted Signing not configured locally; binaries left unsigned.
    echo        See docs\code-signing.md to configure local or CI signing.
)

echo.
echo ============================================================
echo   Release Build Complete:
echo   - Executable: strawberry-cli\dist\strawberry.exe
echo   - Installer:  dist\Strawberry_Setup.exe
echo ============================================================
if not defined STRAWBERRY_BATCH_NOPAUSE pause
exit /b 0
