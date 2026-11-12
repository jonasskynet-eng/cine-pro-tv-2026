import json
from pathlib import Path

BASE_DIR = Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV")
DESKTOP_DIR = Path(r"C:\Users\jonas\Desktop")

# Carregar index.html atual para atualizar a parte do JavaScript
html_path = BASE_DIR / "saida" / "index.html"
html_content = html_path.read_text(encoding="utf-8")

# Substituir type: 'mse' por type: 'mpegts'
velho_bloco = """                    mpegtsPlayer = mpegts.createPlayer({
                        type: 'mse',
                        isLive: true,
                        url: targetUrl
                    }, {"""

novo_bloco = """                    mpegtsPlayer = mpegts.createPlayer({
                        type: 'mpegts',
                        isLive: true,
                        url: targetUrl
                    }, {"""

if velho_bloco in html_content:
    html_content = html_content.replace(velho_bloco, novo_bloco)
    print("Corrigido type: 'mse' para type: 'mpegts'!")
else:
    print("Aviso: Bloco com type: 'mse' nao encontrado diretamente, fazendo busca por regex...")
    import re
    html_content = re.sub(r"type:\s*['\"]mse['\"]", "type: 'mpegts'", html_content)
    print("Regex de correcao aplicada!")

# Garantir video com initial muted para destravar a politica de autoplay do Chrome
html_content = html_content.replace("<video id=\"mainVideo\" controls autoplay playsinline></video>", "<video id=\"mainVideo\" controls autoplay playsinline muted></video>")

# Adicionar desmutar automatico no primeiro clique
desmutar_script = """
        // Desmutar o video no primeiro clique do usuario em qualquer lugar da tela
        document.body.addEventListener('click', function () {
            if (video.muted) {
                video.muted = false;
                console.log('Audio ativado com sucesso pelo clique do usuario!');
            }
        }, { once: true });
"""
if "document.body.addEventListener('click'" not in html_content:
    html_content = html_content.replace("renderizar();", desmutar_script + "\n        renderizar();")

# Gravar nos arquivos
(DESKTOP_DIR / "ASSISTIR_TV.html").write_text(html_content, encoding="utf-8")
(BASE_DIR / "saida" / "index.html").write_text(html_content, encoding="utf-8")
print("ASSISTIR_TV.html e saida/index.html atualizados com correcao de reproducao definitiva!")
