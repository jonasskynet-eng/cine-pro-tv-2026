@echo off
chcp 65001 >nul
title Gerenciador do Docker VIP Completo - CinePro TV
color 0B
cd /d "%~dp0"

:MENU
cls
echo ==============================================================
echo   🐳 GERENCIADOR DOCKER VIP COMPLETO - CINEPRO TV 2026
echo ==============================================================
echo.
echo [1] Ver status do container Docker VIP (Porta 8090)
echo [2] Iniciar ou atualizar Docker VIP Completo
echo [3] Abrir pasta secreta das listas VIP (.m3u / .m3u8)
echo [4] Abrir CinePro TV VIP no Navegador (http://localhost:8090)
echo [5] Parar container Docker VIP
echo [6] Sair
echo.
set /p opcao="Escolha uma opcao [1-6]: "

if "%opcao%"=="1" goto STATUS
if "%opcao%"=="2" goto SUBIR
if "%opcao%"=="3" goto PASTA_VIP
if "%opcao%"=="4" goto ABRIR
if "%opcao%"=="5" goto PARAR
if "%opcao%"=="6" goto SAIR
goto MENU

:STATUS
cls
echo [Verificando container cinepro_tv_vip...]
docker ps --filter "name=cinepro_tv_vip" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
pause
goto MENU

:SUBIR
cls
echo [Construindo e iniciando o servidor Docker VIP na porta 8090...]
docker compose up -d --build
echo.
echo Acesse no navegador: http://localhost:8090
echo.
pause
goto MENU

:PASTA_VIP
start "" "%~dp0ECOSSISTEMA_STREAMING_IPTV\vip_privado"
goto MENU

:ABRIR
start http://localhost:8090
goto MENU

:PARAR
cls
echo [Parando container Docker VIP...]
docker compose down
echo.
pause
goto MENU

:SAIR
exit
