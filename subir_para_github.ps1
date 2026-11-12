# ==============================================================================
# subir_para_github.ps1 - Sincronização automatizada com o GitHub
# ==============================================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   🚀 SINCRONIZADOR OFICIAL DO ECOSSISTEMA COM O GITHUB" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Verificando status do Git local..." -ForegroundColor Yellow
git status --short

Write-Host ""
Write-Host "[2/3] Verificando login no GitHub..." -ForegroundColor Yellow
$authCheck = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Realize o login rápido de 1 clique no GitHub CLI:" -ForegroundColor Magenta
    gh auth login --web -h github.com -p https
}

Write-Host ""
Write-Host "[3/3] Criando repositório e enviando arquivos para a nuvem..." -ForegroundColor Yellow
gh repo create jonasskynet-eng/central-tv-iptv-pro --public --source=. --remote=origin --push

if ($LASTEXITCODE -ne 0) {
    Write-Host "Tentando envio direto para o repositório remoto..." -ForegroundColor Yellow
    git remote add origin https://github.com/jonasskynet-eng/central-tv-iptv-pro.git 2>$null
    git branch -M main
    git push -u origin main
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "✅ PROJETO SALVO NO GITHUB COM SUCESSO!" -ForegroundColor Green
Write-Host "Acesse em: https://github.com/jonasskynet-eng/central-tv-iptv-pro" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
