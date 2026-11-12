@echo off
chcp 65001 > nul
title Enviar Ecossistema para o GitHub
echo =====================================================================
echo    🚀 SINCRONIZADOR OFICIAL DO ECOSSISTEMA COM O GITHUB
echo =====================================================================
echo.
echo [1/3] Verificando status do Git local...
git status --short
echo.
echo [2/3] Verificando login no GitHub...
gh auth status > nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Você ainda não fez login no GitHub CLI nesta máquina.
    echo Vamos abrir o navegador para você autorizar em 1 clique:
    echo.
    gh auth login --web -h github.com -p https
)

echo.
echo [3/3] Criando repositório remoto e enviando arquivos...
gh repo create jonasskynet-eng/central-tv-iptv-pro --public --source=. --remote=origin --push

if %errorlevel% neq 0 (
    echo.
    echo Tentando push direto caso o repositório já exista...
    git remote add origin https://github.com/jonasskynet-eng/central-tv-iptv-pro.git > nul 2>&1
    git branch -M main
    git push -u origin main
)

echo.
echo =====================================================================
echo ✅ PROJETO SALVO NO GITHUB COM SUCESSO!
echo Acesse em: https://github.com/jonasskynet-eng/central-tv-iptv-pro
echo =====================================================================
pause
