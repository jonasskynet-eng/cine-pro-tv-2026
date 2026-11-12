@echo off
chcp 65001 > nul
title Central de TV Digital Pro 2026 - Inicializador
echo =====================================================================
echo    🚀 CENTRAL DE TV DIGITAL PRO 2026 - INICIANDO ECOSSISTEMA
echo =====================================================================
echo.
echo [1/2] Iniciando servidor de streaming local na porta 8080...
start /B python "ECOSSISTEMA_STREAMING_IPTV\servidor_streaming_local.py"
timeout /t 2 /nobreak > nul
echo.
echo [2/2] Abrindo Central de TV no navegador...
start http://localhost:8080/index.html
echo.
echo ✅ Central iniciada com sucesso!
echo Pressione qualquer tecla para fechar esta janela (o servidor continuará ativo).
pause > nul
