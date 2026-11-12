# Script de Registro da Tarefa Agendada no Windows
$NomeTarefa = "AtualizadorDiarioIPTV"
$ScriptBat = "C:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\executar_rotina_diaria.bat"

Write-Host "Configurando tarefa agendada no Agendador do Windows para as 03:00 diariamente..." -ForegroundColor Cyan

# Executa schtasks para criar a rotina diária apontando para o arquivo em lote (.bat)
schtasks /create /tn $NomeTarefa /tr "`"$ScriptBat`"" /sc daily /st 03:00 /f

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n[SUCESSO] Tarefa agendada com exito!" -ForegroundColor Green
    Write-Host "A lista de canais sera atualizada automaticamente todos os dias as 03:00." -ForegroundColor Yellow
    Write-Host "Registro de execucao: saida\log_atualizacao.log" -ForegroundColor Gray
} else {
    Write-Host "`n[AVISO] Nao foi possivel registrar a tarefa. Verifique as permissoes." -ForegroundColor Red
}
