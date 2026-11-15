@echo off
chcp 65001 > nul
title Enviar Ecossistema Versao 03 (v3.0) para o GitHub
cd /d "c:\Users\jonas\Downloads\projeto de estudo"

echo =====================================================================
echo    🚀 SINCRONIZADOR OFICIAL — VERSAO 03 (v3.0) NO GITHUB
echo =====================================================================
echo.
echo [1/4] Verificando repositório local, tags e último commit...
git status --short
echo.
git tag -n
echo.
git log -n 1 --oneline
echo.

echo [2/4] Verificando login no GitHub CLI...
gh auth status > nul 2>&1
if %errorlevel% equ 0 goto :JA_LOGADO
echo.
echo ⚠️ Você ainda não fez login no GitHub CLI nesta máquina.
echo Vamos abrir o navegador para você autorizar em 1 clique:
echo.
gh auth login --web -h github.com -p https

:JA_LOGADO
echo.
echo [3/4] Publicando repositório e versões (v1.0, v2.0, v3.0)...
git branch -M main > nul 2>&1
gh repo view jonasskynet-eng/central-tv-iptv-pro > nul 2>&1
if %errorlevel% equ 0 goto :REPO_EXISTE

git remote remove origin > nul 2>&1
gh repo create jonasskynet-eng/central-tv-iptv-pro --public --source=. --remote=origin --push
if %errorlevel% equ 0 goto :ENVIAR_TAGS

:REPO_EXISTE
git remote remove origin > nul 2>&1
git remote add origin https://github.com/jonasskynet-eng/central-tv-iptv-pro.git > nul 2>&1
git push -u origin main --tags
goto :CRIAR_RELEASE

:ENVIAR_TAGS
git push origin --tags

:CRIAR_RELEASE
echo.
echo [4/4] Publicando Release Oficial v3.0 com pacote ZIP da nuvem...
gh release view v3.0 -R jonasskynet-eng/central-tv-iptv-pro > nul 2>&1
if %errorlevel% equ 0 goto :RELEASE_EXISTE
gh release create v3.0 "C:\Users\jonas\Desktop\iptv\CINEPRO_TV_NUVEM_PRONTO.zip" -R jonasskynet-eng/central-tv-iptv-pro --title "Versão 03 (v3.0) — CinePro TV 2026 Híbrida (Nuvem + Local)" --notes "Versão 03 Oficial: 920 canais auditados, 20 rádios brasileiras ao vivo, roteamento híbrido Nuvem HTTPS + Local e QR Code funcional."
goto :FIM

:RELEASE_EXISTE
echo ℹ️ Release v3.0 já existe no repositório remoto.

:FIM
echo.
echo =====================================================================
echo ✅ PROJETO E VERSAO 03 PUBLICADOS NO GITHUB COM SUCESSO!
echo Acesse em: https://github.com/jonasskynet-eng/central-tv-iptv-pro
echo =====================================================================
pause
