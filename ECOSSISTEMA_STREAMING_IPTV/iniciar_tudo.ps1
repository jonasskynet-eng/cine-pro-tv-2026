# Script de Inicialização Rápida do Ecossistema IPTV
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🚀 ECOSSISTEMA IPTV: VALIDAÇÃO TURBO & SERVIDOR LOCAL" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

$DiretorioAtual = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Coleta remota e validação massiva em lote
Write-Host "`n[1/2] Baixando fontes e filtrando canais ativos em alta velocidade..." -ForegroundColor Yellow
python "$DiretorioAtual\coletor_automatico.py"

# 2. Inicia o Servidor Local
Write-Host "`n[2/2] Subindo servidor de streaming local (Porta 8080)..." -ForegroundColor Yellow
Write-Host "-> Lista Brasil Turbo: http://localhost:8080/lista_brasil_turbo.m3u" -ForegroundColor Green
python "$DiretorioAtual\servidor_local.py"
