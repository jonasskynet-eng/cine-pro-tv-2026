from pathlib import Path

for path in [
    Path(r"c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\saida\index.html"),
    Path(r"C:\Users\jonas\Desktop\ASSISTIR_TV.html")
]:
    txt = path.read_text(encoding="utf-8")
    # Canal inicial rápido instantâneo
    txt = txt.replace(
        "const inicial = CANAIS.find(c => c.cors_star === 1 && c.latencia < 100) || CANAIS[0];",
        "const inicial = CANAIS.find(c => c.nome.toLowerCase().includes('amazon sat')) || CANAIS[0];"
    )
    # Mensagem personalizada de carregamento do Discovery
    txt = txt.replace(
        "toastMsg.textContent = 'Carregando transmissão...';",
        "toastMsg.textContent = c && c.nome.toLowerCase().includes('discovery') ? 'Conectando ao sinal Discovery (aguarde cerca de 3s)...' : 'Carregando transmissão...';"
    )
    path.write_text(txt, encoding="utf-8")

print("Canal inicial definido para Amazon Sat HD (0.09s) com aviso de buffer para o Discovery!")
