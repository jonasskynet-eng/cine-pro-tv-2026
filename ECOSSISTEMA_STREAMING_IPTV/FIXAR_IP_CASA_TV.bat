@echo off
chcp 65001 >nul
title Fixar IP da Casa para TV Samsung - CinePro TV
color 0E

:MENU
cls
echo ==================================================================
echo   📺 FIXAR IP DA SUA CASA PARA TV SAMSUNG (192.168.100.210)
echo ==================================================================
echo.
echo   Isso evita que o endereco da sua TV mude se faltar luz.
echo   (Execute clicando com o botao direito ^> "Executar como administrador")
echo.
echo [1] Travar IP Fixo 192.168.100.210 no Windows (Recomendado)
echo [2] Voltar para IP Automatico (DHCP do roteador)
echo [3] Ver IP atual do computador
echo [4] Sair
echo.
set /p op="Escolha uma opcao [1-4]: "

if "%op%"=="1" goto FIXAR
if "%op%"=="2" goto DHCP
if "%op%"=="3" goto VERIP
if "%op%"=="4" exit
goto MENU

:FIXAR
cls
echo [Aplicando IP fixo 192.168.100.210 na placa de rede ativa...]
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { Write-Host 'ERRO: Abra este arquivo como ADMINISTRADOR!' -ForegroundColor Red; exit 1 }; $rota = Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object RouteMetric | Select-Object -First 1; if (-not $rota) { Write-Host 'Placa de rede ativa nao encontrada.' -ForegroundColor Red; exit 1 }; $alias = $rota.InterfaceAlias; $gw = $rota.NextHop; Remove-NetIPAddress -InterfaceAlias $alias -AddressFamily IPv4 -Confirm:$false -ErrorAction SilentlyContinue; New-NetIPAddress -InterfaceAlias $alias -IPAddress '192.168.100.210' -PrefixLength 24 -DefaultGateway $gw | Out-Null; Set-DnsClientServerAddress -InterfaceAlias $alias -ServerAddresses @($gw,'1.1.1.1','8.8.8.8'); Write-Host ('Sucesso! IP travado em 192.168.100.210 na placa ' + $alias + ' (Gateway ' + $gw + ')') -ForegroundColor Green"
echo.
pause
goto MENU

:DHCP
cls
echo [Voltando para IP automatico (DHCP)...]
powershell -NoProfile -ExecutionPolicy Bypass -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { Write-Host 'ERRO: Abra este arquivo como ADMINISTRADOR!' -ForegroundColor Red; exit 1 }; $rota = Get-NetRoute -DestinationPrefix '0.0.0.0/0' | Sort-Object RouteMetric | Select-Object -First 1; $alias = $rota.InterfaceAlias; Set-NetIPInterface -InterfaceAlias $alias -Dhcp Enabled; Set-DnsClientServerAddress -InterfaceAlias $alias -ResetServerAddresses; Write-Host ('IP automatico reativado na placa ' + $alias) -ForegroundColor Green"
echo.
pause
goto MENU

:VERIP
cls
ipconfig | findstr /R "IPv4 Gateway"
echo.
pause
goto MENU
