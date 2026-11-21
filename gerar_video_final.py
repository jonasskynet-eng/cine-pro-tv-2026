import subprocess
import os

img = r"C:\Users\jonas\Desktop\MEU_AVATAR_JONAS.jpg"
audio = r"C:\Users\jonas\Desktop\AUDIO_JONAS_OFICIAL.wav"
out_video = r"C:\Users\jonas\Desktop\VIDEO_OFICIAL_JONAS.mp4"
font_bold = "C\\\\:/Windows/Fonts/arialbd.ttf"
font_regular = "C\\\\:/Windows/Fonts/arial.ttf"

# Filtro completo:
# 1. Redimensiona imagem base para 768x1024
# 2. Zoompan sutil cinematográfico
# 3. Ondas sonoras animadas reagindo ao áudio em tempo real
# 4. Caixa inferior translúcida de apresentação
# 5. Textos profissionais de identificação do Jonas e CinePro TV
filter_complex = (
    "[0:v]scale=768:1024,zoompan=z='min(zoom+0.0003,1.04)':d=260:s=768x1024:fps=30[bg];"
    "[1:a]asplit[a_out][a_waves];"
    "[a_waves]showwaves=s=720x100:mode=line:colors=0x10b981|0x38bdf8:rate=30,format=rgba[waves];"
    "[bg]drawbox=y=ih-200:color=black@0.75:width=iw:height=200:t=fill[bg_box];"
    "[bg_box][waves]overlay=24:H-105[v1];"
    f"[v1]drawtext=fontfile={font_bold}:text='CINEPRO TV - APRESENTADOR JONAS':fontcolor=white:fontsize=26:x=(w-text_w)/2:y=h-175,"
    f"drawtext=fontfile={font_regular}:text='Seja bem-vindo a Central de Radio e TV!':fontcolor=0x34d399:fontsize=20:x=(w-text_w)/2:y=h-135[v_final]"
)

cmd = [
    "ffmpeg", "-y",
    "-loop", "1", "-i", img,
    "-i", audio,
    "-filter_complex", filter_complex,
    "-map", "[v_final]",
    "-map", "[a_out]",
    "-c:v", "libx264",
    "-tune", "stillimage",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-shortest",
    out_video
]

print("Iniciando renderização do vídeo oficial...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res.returncode == 0 and os.path.exists(out_video):
    size = os.path.getsize(out_video)
    print(f"SUCESSO! Vídeo gerado com perfeição: {size} bytes em {out_video}")
else:
    print("ERRO:", res.stderr[-500:])
