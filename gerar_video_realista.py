import subprocess
import os

img1 = r"C:\Users\jonas\Desktop\JONAS_FEIRA_COCO.jpg"
img2 = r"C:\Users\jonas\Desktop\JONAS_MESA_PASTEL.webp"
audio = r"C:\Users\jonas\Desktop\AUDIO_JONAS_OFICIAL.wav"
out_video = r"C:\Users\jonas\Desktop\VIDEO_CINEPRO_JONAS_REALISTA.mp4"

font_bold = "C\\\\:/Windows/Fonts/arialbd.ttf"
font_regular = "C\\\\:/Windows/Fonts/arial.ttf"

# Take 1: Duração 4.2s (126 frames a 30fps) - Feira com Coco
# Take 2: Duração 4.33s (130 frames a 30fps) - Mesa de Boteco com Pastel
filter_complex = (
    # --- ÁUDIO (3 Camadas Simultâneas) ---
    "[2:a]volume=1.25,asplit=2[voz_mix][voz_waves];"
    "sine=f=587.33:d=1.2,afade=t=out:st=0.4:d=0.8,volume=0.18[tone1];"
    "sine=f=880:d=1.5,afade=t=out:st=0.5:d=1.0,volume=0.12[tone2];"
    "[tone1][tone2]amix=inputs=2[chime];"
    "sine=f=130.81:d=8.53,volume=0.035,lowpass=f=220[bed];"
    "[chime][bed]amix=inputs=2:duration=longest[trilha];"
    "[voz_mix][trilha]amix=inputs=2:duration=first:weights=1.0 0.28[a_out];"
    
    # --- VÍDEO TAKE 1 (Feira) ---
    "[0:v]zoompan=z='min(zoom+0.0005,1.05)':d=126:s=1280x720:fps=30[take1];"
    
    # --- VÍDEO TAKE 2 (Mesa com Pastel) ---
    "[1:v]zoompan=z='min(zoom+0.0005,1.05)':d=130:s=1280x720:fps=30[take2];"
    
    # --- CONCATENAÇÃO DOS TAKES (Corte dinâmico aos 4.2s) ---
    "[take1][take2]concat=n=2:v=1:a=0[v_base];"
    
    # --- ONDAS SONORAS REATIVAS ---
    "[voz_waves]showwaves=s=1200x80:mode=line:colors=0x10b981|0x38bdf8:rate=30,format=rgba[waves];"
    
    # --- TARJA SUPERIOR (AO VIVO) ---
    "[v_base]drawbox=y=25:x=35:width=230:height=48:color=black@0.75:t=fill[v_top];"
    f"[v_top]drawtext=fontfile={font_bold}:text='AO VIVO':fontcolor=0xef4444:fontsize=22:x=50:y=38,"
    f"drawtext=fontfile={font_bold}:text='CINEPRO TV':fontcolor=white:fontsize=22:x=145:y=38[v_top_branded];"
    
    # --- TARJA INFERIOR DE TELEJORNAL ---
    "[v_top_branded]drawbox=y=ih-170:color=black@0.80:width=iw:height=170:t=fill[v_box];"
    "[v_box][waves]overlay=40:H-90[v_waves_box];"
    f"[v_waves_box]drawtext=fontfile={font_bold}:text='JONAS - APRESENTADOR E DIRETOR':fontcolor=white:fontsize=28:x=45:y=h-145,"
    f"drawtext=fontfile={font_regular}:text='CENTRAL DE RADIO E TELEVISAO CINEPRO':fontcolor=0x34d399:fontsize=20:x=45:y=h-110[v_final]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", img1,
    "-i", img2,
    "-i", audio,
    "-filter_complex", filter_complex,
    "-map", "[v_final]",
    "-map", "[a_out]",
    "-c:v", "libx264",
    "-preset", "medium",
    "-c:a", "aac",
    "-b:a", "192k",
    "-pix_fmt", "yuv420p",
    "-t", "8.53",
    out_video
]

print("Renderizando vídeo de alta fidelidade...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res.returncode == 0 and os.path.exists(out_video):
    size = os.path.getsize(out_video)
    print(f"SUCESSO ABSOLUTO! Vídeo HD gerado: {size} bytes em {out_video}")
else:
    print("ERRO:", res.stderr[-600:])
