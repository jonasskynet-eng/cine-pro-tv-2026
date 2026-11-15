# ==============================================================================
# subir_para_github.ps1 - Sincronização oficial da Versão 03 (v3.0) no GitHub
# ==============================================================================
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location "c:\Users\jonas\Downloads\projeto de estudo"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "   🚀 SINCRONIZADOR OFICIAL — VERSAO 03 (v3.0) NO GITHUB" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Verificando status, tags e último commit local..." -ForegroundColor Yellow
git status --short
git tag -n
git log -n 1 --oneline

Write-Host ""
Write-Host "[2/4] Verificando login no GitHub..." -ForegroundColor Yellow
gh auth status *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Realize o login rápido de 1 clique no GitHub CLI:" -ForegroundColor Magenta
    gh auth login --web -h github.com -p https
}

Write-Host ""
Write-Host "[3/4] Criando repositório (se necessário) e enviando Versão 03 + tags..." -ForegroundColor Yellow
git branch -M main *> $null
gh repo view jonasskynet-eng/central-tv-iptv-pro *> $null
if ($LASTEXITCODE -ne 0) {
    git remote remove origin *> $null
    gh repo create jonasskynet-eng/central-tv-iptv-pro --public --source=. --remote=origin --push
    if ($LASTEXITCODE -eq 0) {
        git push origin --tags
    } else {
        git remote add origin https://github.com/jonasskynet-eng/central-tv-iptv-pro.git *> $null
        git push -u origin main --tags
    }
} else {
    git remote remove origin *> $null
    git remote add origin https://github.com/jonasskynet-eng/central-tv-iptv-pro.git *> $null
    git push -u origin main --tags
}

Write-Host ""
Write-Host "[4/4] Publicando Release Oficial v3.0 com pacote da nuvem..." -ForegroundColor Yellow
gh release view v3.0 -R jonasskynet-eng/central-tv-iptv-pro *> $null
if ($LASTEXITCODE -ne 0) {
    gh release create v3.0 "C:\Users\jonas\Desktop\iptv\CINEPRO_TV_NUVEM_PRONTO.zip" -R jonasskynet-eng/central-tv-iptv-pro --title "Versão 03 (v3.0) — CinePro TV 2026 Híbrida (Nuvem + Local)" --notes "Versão 03 Oficial: 920 canais auditados, 20 rádios brasileiras ao vivo, roteamento híbrido Nuvem HTTPS + Local e QR Code funcional."
} else {
    Write-Host "ℹ️ Release v3.0 já publicada no GitHub." -ForegroundColor Gray
}

Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Green
Write-Host "✅ PROJETO E VERSAO 03 SALVOS NO GITHUB COM SUCESSO!" -ForegroundColor Green
Write-Host "Acesse em: https://github.com/jonasskynet-eng/central-tv-iptv-pro" -ForegroundColor Green
Write-Host "=====================================================================" -ForegroundColor Green
