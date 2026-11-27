@echo off
setlocal EnableExtensions EnableDelayedExpansion
chcp 65001 >nul

cd /d "%~dp0"

echo ============================================================
echo   Strawberry Admin - Vercel Production Deployment
echo ============================================================
echo.

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    pause
    exit /b 1
)

where npm >nul 2>nul
if errorlevel 1 (
    echo [ERROR] npm is not installed or not in PATH.
    pause
    exit /b 1
)

set "VERCEL_CMD=npx --yes vercel@latest"
where vercel >nul 2>nul
if not errorlevel 1 (
    set "VERCEL_CMD=vercel"
)

echo [1/4] Verifying TypeScript & Vite build in strawberry-admin...
pushd "%~dp0strawberry-admin"
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm ci
    if errorlevel 1 (
        popd
        echo [ERROR] npm ci failed.
        pause
        exit /b 1
    )
)
call npm run build
if errorlevel 1 (
    popd
    echo [ERROR] strawberry-admin build failed. Fix errors before deploying.
    pause
    exit /b 1
)
popd
echo [OK] Build passed.
echo.

echo [2/4] Checking Vercel CLI authentication...
call %VERCEL_CMD% whoami >nul 2>nul
if errorlevel 1 (
    echo Not logged into Vercel. Launching login...
    call %VERCEL_CMD% login
    if errorlevel 1 (
        echo [ERROR] Vercel login failed.
        pause
        exit /b 1
    )
)
for /f "delims=" %%U in ('call %VERCEL_CMD% whoami 2^>nul') do set "VC_USER=%%U"
echo [OK] Logged in as: !VC_USER!
echo.

echo [3/4] Checking Vercel project link & public Supabase environment...
if not exist "%~dp0.vercel\project.json" (
    echo Project not linked yet. Running vercel link...
    call %VERCEL_CMD% link
    if errorlevel 1 (
        echo [ERROR] Vercel project link failed.
        pause
        exit /b 1
    )
)

REM Read public Supabase keys from .env (strictly ignores STRAWBERRY_SUPABASE_SECRET_KEY)
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

if defined PUB_URL if defined PUB_KEY (
    echo Note: Ensure VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY are set in Vercel Project Settings.
    set /p "SYNC_ENV=Push public VITE_SUPABASE_URL & VITE_SUPABASE_PUBLISHABLE_KEY to Vercel production env? (y/N): "
    if /i "!SYNC_ENV!"=="y" (
        <nul set /p ="!PUB_URL!"| call %VERCEL_CMD% env add VITE_SUPABASE_URL production --force
        <nul set /p ="!PUB_KEY!"| call %VERCEL_CMD% env add VITE_SUPABASE_PUBLISHABLE_KEY production --force
    )
) else (
    echo [WARN] No local .env Supabase keys found. Configure VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY in Vercel Dashboard.
)
echo.

echo [4/4] Deploying Strawberry Admin to Vercel Production...
call %VERCEL_CMD% deploy --prod
if errorlevel 1 (
    echo.
    echo [ERROR] Vercel deployment failed.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Deployment Complete!
echo ============================================================
pause
exit /b 0
