@echo off
chcp 65001 >nul
title Gerenciador do Servidor de Streaming IPTV Local
color 0A

:MENU
cls
echo ========================================================
echo   📺 GERENCIADOR DO SERVIDOR DE STREAMING IPTV PRO
echo ========================================================
echo.
echo [1] Checar se o Servidor esta ATIVO
echo [2] Iniciar Servidor Silenciosamente (Segundo Plano)
echo [3] Parar / Fechar Servidor
echo [4] Abrir a Central de TV no Navegador
echo [5] Sair
echo.
set /p opcao="Escolha uma opção [1-5]: "

if "%opcao%"=="1" goto STATUS
if "%opcao%"=="2" goto INICIAR
if "%opcao%"=="3" goto PARAR
if "%opcao%"=="4" goto ABRIR
if "%opcao%"=="5" goto SAIR

:STATUS
cls
echo [Verificando porta 8080...]
netstat -ano | findstr :8080 >nul
if %errorlevel% equ 0 (
    echo.
    echo ✅ O SERVIDOR ESTA ONLINE E RODANDO NA PORTA 8080!
    echo Acesse: http://localhost:8080/index.html
) else (
    echo.
    echo ⚠️ O Servidor esta OFFLINE no momento.
)
echo.
pause
goto MENU

:INICIAR
cls
echo [Iniciando servidor de streaming em segundo plano...]
wscript.exe "C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\iniciar_servidor_silencioso.vbs"
timeout /t 2 >nul
echo.
echo ✅ Comando enviado! Verificando status...
netstat -ano | findstr :8080 >nul
if %errorlevel% equ 0 (
    echo ✅ Servidor iniciado com sucesso!
) else (
    echo ℹ️ Aguardando inicialização completa...
)
echo.
pause
goto MENU

:PARAR
cls
echo [Encerrando processos do servidor de streaming...]
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8080') do taskkill /f /pid %%a >nul 2>&1
echo.
echo ✅ Servidor parado com sucesso.
echo.
pause
goto MENU

:ABRIR
start http://localhost:8080/index.html
goto MENU

:SAIR
exit
