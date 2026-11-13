import os
import subprocess
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
PYTHONW_EXE = r"C:\Program Files (x86)\Python315-32\pythonw.exe"
SERVIDOR_PY = BASE_DIR / "servidor_streaming_local.py"
VBS_PATH = BASE_DIR / "iniciar_servidor_silencioso.vbs"
STARTUP_DIR = Path(os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"))
LNK_PATH = STARTUP_DIR / "Servidor_Streaming_IPTV.lnk"

# 1. Criar o VBScript de inicialização totalmente invisível
conteudo_vbs = f'''Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """{PYTHONW_EXE}"" ""{SERVIDOR_PY}""", 0, False
'''
VBS_PATH.write_text(conteudo_vbs, encoding="utf-8")
print(f"✅ VBScript silencioso criado em: {VBS_PATH}")

# 2. Criar o atalho (.lnk) na pasta Inicializar (Startup) do Windows via PowerShell
cmd_shortcut = f'''$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{LNK_PATH}")
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = """{VBS_PATH}"""
$Shortcut.WorkingDirectory = "{BASE_DIR}"
$Shortcut.Description = "Inicializador Silencioso do Servidor de Streaming IPTV Local"
$Shortcut.Save()
'''
res_shortcut = subprocess.run(["powershell", "-Command", cmd_shortcut], capture_output=True, text=True)
if res_shortcut.returncode == 0 and LNK_PATH.exists():
    print(f"✅ Atalho na pasta Inicializar criado com sucesso em: {LNK_PATH}")
else:
    print(f"⚠️ Erro ao criar atalho: {res_shortcut.stderr}")

# 3. Registrar no Agendador de Tarefas do Windows (schtasks) para iniciar no Logon
nome_tarefa = "ServidorStreamingIPTV"
cmd_schtask = [
    "schtasks", "/create",
    "/tn", nome_tarefa,
    "/tr", f'wscript.exe "{VBS_PATH}"',
    "/sc", "onlogon",
    "/f"
]
res_sch = subprocess.run(cmd_schtask, capture_output=True, text=True)
if res_sch.returncode == 0:
    print(f"✅ Tarefa agendada '{nome_tarefa}' registrada com sucesso no Agendador do Windows (ONLOGON)!")
else:
    print(f"ℹ️ schtasks retorno: {res_sch.stdout or res_sch.stderr}")

# 4. Verificar se o servidor na porta 8080 está respondendo
import urllib.request
try:
    with urllib.request.urlopen("http://localhost:8080/index.html", timeout=4) as resp:
        print(f"✅ Servidor de streaming local respondendo com Status {resp.status} em http://localhost:8080/index.html")
except Exception as e:
    print(f"⚠️ Servidor não respondeu imediatamente: {e}")

print("\n🚀 CONFIGURAÇÃO DE INICIALIZAÇÃO AUTOMÁTICA FINALIZADA COM SUCESSO!")
