import json
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
DESKTOP_DIR = Path(r"C:\Users\jonas\Desktop")

html_path = BASE_DIR / "saida" / "index.html"
txt = html_path.read_text(encoding="utf-8")

# 1. Ajustar resolverUrl para SEMPRE apontar para http://localhost:8080/proxy?url=
velho_resolver = """        function resolverUrl(url) {
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                return '/proxy?url=' + encodeURIComponent(url);
            }
            return url;
        }"""

novo_resolver = """        function resolverUrl(url) {
            // Roteia SEMPRE pelo proxy local na porta 8080, mesmo se aberto via file:///
            return 'http://localhost:8080/proxy?url=' + encodeURIComponent(url);
        }"""

if velho_resolver in txt:
    txt = txt.replace(velho_resolver, novo_resolver)
    print("resolverUrl atualizado com sucesso!")
else:
    import re
    txt = re.sub(r'function resolverUrl\(url\) \{[\s\S]*?return url;\s*\}', novo_resolver, txt)
    print("resolverUrl substituido por regex!")

# 2. Adicionar video.onplaying para remover o toast de carregando assim que os primeiros quadros chegarem
hook_playing = """
            video.onplaying = function () {
                toast.classList.remove('active');
                liveDot.style.background = 'var(--emerald)';
                console.log('Transmissão ao vivo iniciada com sucesso!');
            };
            video.onwaiting = function () {
                toastMsg.textContent = 'Carregando transmissão...';
                toast.classList.add('active');
            };
"""

if "video.onplaying" not in txt:
    txt = txt.replace("destruirPlayers();", "destruirPlayers();\n" + hook_playing)
    print("Hooks de reprodução adicionados!")

# 3. Mudar o canal inicial para um canal ultra-rápido comprovado (Amazon Sat HD ou RecordTV)
# para que a tela nunca fique preta ao abrir
txt = txt.replace(
    "const inicial = CANAIS.find(c => c.nome.toLowerCase().includes('discovery kids') && c.qualidade === 'Digital') || CANAIS[0];",
    "const inicial = CANAIS.find(c => c.cors_star === 1 && c.latencia < 100) || CANAIS[0];"
)

# Gravar nos dois arquivos
(BASE_DIR / "saida" / "index.html").write_text(txt, encoding="utf-8")
(DESKTOP_DIR / "ASSISTIR_TV.html").write_text(txt, encoding="utf-8")
print("index.html e ASSISTIR_TV.html gravados com sucesso!")
