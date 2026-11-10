@echo off
chcp 65001 >nul
echo =====================================================================
echo   🚀 COMPILADOR DE APK ANDROID - DEFENSOR ESTELAR (DOCKER + BUILDOZER)
echo =====================================================================
echo.

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] O Docker Desktop nao esta em execucao no momento.
    echo     1. Abra o aplicativo "Docker Desktop" no Windows e aguarde iniciar.
    echo     2. Execute este arquivo (gerar_apk_local.bat) novamente!
    echo.
    pause
    exit /b 1
)

echo [1/2] Iniciando container oficial kivy/buildozer...
echo       (A primeira execucao baixa o Android SDK/NDK e pode levar 15-20 min)
echo.

docker run --rm ^
    -v "%~dp0mobile_python_kivy:/home/user/hostcwd" ^
    -v buildozer_cache:/home/user/.buildozer ^
    kivy/buildozer android debug

if %errorlevel% equ 0 (
    echo.
    echo =====================================================================
    echo   ✅ APK GERADO COM SUCESSO!
    echo   Arquivo disponivel na pasta: mobile_python_kivy\bin\
    echo =====================================================================
    explorer "%~dp0mobile_python_kivy\bin"
) else (
    echo.
    echo [X] Ocorreu um erro durante a compilacao do APK.
)
pause

