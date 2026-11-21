import subprocess
import os

img = r"C:\Users\jonas\Desktop\MEU_AVATAR_JONAS.jpg"
audio = r"C:\Users\jonas\Desktop\AUDIO_JONAS_OFICIAL.wav"
out_video = r"C:\Users\jonas\Desktop\VIDEO_OFICIAL_JONAS.mp4"
font_bold = "C\\\\:/Windows/Fonts/arialbd.ttf"
font_regular = "C\\\\:/Windows/Fonts/arial.ttf"

# Filtro Completo de Padrão Broadcast Comercial:
# 1. Vídeo: Zoompan suave (1.0 -> 1.045) em 768x1024 a 30fps
# 2. Tag superior: [🔴 AO VIVO] • CINEPRO TV
# 3. Tag inferior: Gradiente preto translúcido com ondas de áudio reagindo em verde esmeralda e ciano
# 4. Textos: Identificação oficial do Jonas e boas-vindas
# 5. Áudio (3 Camadas):
#    - Camada 1: Voz oficial do Jonas (+15% de ganho e equalizada)
#    - Camada 2: Chime / Vinheta harmônica de entrada de transmissão nos primeiros 1.5s
#    - Camada 3: Cama sonora sutil de estúdio ao fundo (-22dB)

filter_complex = (
    # --- ÁUDIO (3 Camadas) ---
    "[1:a]volume=1.2,asplit=2[voz_mix][voz_waves];"
    "sine=f=587.33:d=1.2,afade=t=out:st=0.4:d=0.8,volume=0.18[tone1];"
    "sine=f=880:d=1.5,afade=t=out:st=0.5:d=1.0,volume=0.12[tone2];"
    "[tone1][tone2]amix=inputs=2[chime];"
    "sine=f=130.81:d=8.53,volume=0.04,lowpass=f=220[bed];"
    "[chime][bed]amix=inputs=2:duration=longest[trilha];"
    "[voz_mix][trilha]amix=inputs=2:duration=first:weights=1.0 0.28[a_out];"
    # --- VÍDEO & ANIMAÇÃO GRÁFICA ---
    "[0:v]scale=768:1024,zoompan=z='min(zoom+0.00035,1.045)':d=260:s=768x1024:fps=30[bg];"
    "[voz_waves]showwaves=s=700x90:mode=line:colors=0x10b981|0x38bdf8:rate=30,format=rgba[waves];"
    # Tarja superior AO VIVO
    "[bg]drawbox=y=20:x=20:width=190:height=44:color=black@0.75:t=fill[bg_top];"
    f"[bg_top]drawtext=fontfile={font_bold}:text='AO VIVO':fontcolor=0xef4444:fontsize=20:x=35:y=32,"
    f"drawtext=fontfile={font_bold}:text='CINEPRO':fontcolor=white:fontsize=20:x=115:y=32[v_top];"
    # Tarja inferior de identificação
    "[v_top]drawbox=y=ih-210:color=black@0.80:width=iw:height=210:t=fill[v_box];"
    "[v_box][waves]overlay=34:H-105[v_waves_box];"
    f"[v_waves_box]drawtext=fontfile={font_bold}:text='JONAS - APRESENTADOR E DIRETOR':fontcolor=white:fontsize=26:x=(w-text_w)/2:y=h-180,"
    f"drawtext=fontfile={font_regular}:text='Seja bem-vindo a Central de Radio e TV!':fontcolor=0x34d399:fontsize=21:x=(w-text_w)/2:y=h-140[v_final]"
)

cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-i", img,
    "-i", audio,
    "-filter_complex", filter_complex,
    "-map", "[v_final]",
    "-map", "[a_out]",
    "-c:v", "libx264",
    "-preset", "medium",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    out_video
]

print("Renderizando vídeo de padrão oficial broadcast...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res.returncode == 0 and os.path.exists(out_video):
    size = os.path.getsize(out_video)
    print(f"SUCESSO ABSOLUTO! Vídeo finalizado: {size} bytes")
else:
    print("ERRO:", res.stderr[-500:])
