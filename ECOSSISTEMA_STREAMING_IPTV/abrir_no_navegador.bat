@echo off
REM Garante que o servidor local na porta 8080 esteja ativo antes de abrir no navegador
powershell -NoProfile -Command "try { (New-Object Net.Sockets.TcpClient('127.0.0.1', 8080)).Close(); exit 0 } catch { exit 1 }"
if %errorlevel% neq 0 (
    wscript //nologo "%~dp0iniciar_servidor_silencioso.vbs"
    timeout /t 2 /nobreak > nul
)
start http://localhost:8080/index.html
