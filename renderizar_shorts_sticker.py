import subprocess
import os

sticker_png = r"C:\Users\jonas\Desktop\JONAS_AVATAR_STICKER.png"
audio_wav = r"C:\Users\jonas\Desktop\AUDIO_JONAS_OFICIAL.wav"
out_video = r"C:\Users\jonas\Desktop\VIDEO_SHORTS_JONAS_STICKER.mp4"

font_impact = "C\\\\:/Windows/Fonts/impact.ttf"
font_bold = "C\\\\:/Windows/Fonts/arialbd.ttf"

# Duração exata: 8.53 segundos
# Formato: 1080x1920 (9:16 Vertical para YouTube Shorts e TikTok)

filter_complex = (
    # --- 1. ÁUDIO (3 Camadas) ---
    "[1:a]volume=1.25,asplit=2[voz_mix][voz_waves];"
    # SFX Pop de entrada aos 0.1s
    "sine=f=520:d=0.22,afade=t=out:st=0.05:d=0.17,volume=0.22[sfx_pop];"
    # Trilha sonora sutil de fundo (batida lo-fi / tech suave)
    "sine=f=110:d=8.53,volume=0.04,lowpass=f=200[bed];"
    "[sfx_pop][bed]amix=inputs=2:duration=longest[trilha];"
    "[voz_mix][trilha]amix=inputs=2:duration=first:weights=1.0 0.25[a_out];"

    # --- 2. VÍDEO E ANIMAÇÕES ---
    # Fundo moderno em gradiente escuro profissional (1080x1920)
    "color=c=0x0b0f19:s=1080x1920:d=8.53[bg];"
    
    # Efeito de brilho radial sutil no centro
    "[bg]drawbox=x=0:y=0:width=1080:height=1920:color=0x1e293b@0.45:t=fill[bg_dark];"
    
    # Ondas de áudio dinâmicas na parte inferior atrás do avatar
    "[voz_waves]showwaves=s=1000x120:mode=line:colors=0x10b981|0x38bdf8:rate=30,format=rgba[waves];"
    "[bg_dark][waves]overlay=40:H-260[bg_waves];"

    # Selo de canal no topo: [🔴 CINEPRO TV • APRESENTADOR JONAS]
    "[bg_waves]drawbox=x=140:y=120:width=800:height=72:color=black@0.75:t=fill[v_header];"
    f"[v_header]drawtext=fontfile={font_bold}:text='AO VIVO':fontcolor=0xef4444:fontsize=28:x=180:y=138,"
    f"drawtext=fontfile={font_bold}:text='CINEPRO TV - CANAL OFICIAL':fontcolor=white:fontsize=28:x=340:y=138[v_head_branded];"

    # --- LEGENDAS DINÂMICAS VIRAIS (Amarelo Shorts com borda preta) ---
    f"[v_head_branded]drawtext=fontfile={font_impact}:text='OLA!':fontcolor=0xfacc15:fontsize=95:borderw=8:bordercolor=black:x=(w-text_w)/2:y=380:enable='between(t,0.05,1.7)',"
    f"drawtext=fontfile={font_impact}:text='MEU NOME E JONAS':fontcolor=0xfacc15:fontsize=75:borderw=8:bordercolor=black:x=(w-text_w)/2:y=380:enable='between(t,1.7,4.1)',"
    f"drawtext=fontfile={font_impact}:text='SEJA BEM-VINDO!':fontcolor=0x38bdf8:fontsize=75:borderw=8:bordercolor=black:x=(w-text_w)/2:y=380:enable='between(t,4.1,6.1)',"
    f"drawtext=fontfile={font_impact}:text='A CENTRAL CINEPRO TV!':fontcolor=0x34d399:fontsize=65:borderw=8:bordercolor=black:x=(w-text_w)/2:y=380:enable='between(t,6.1,8.53)'[v_textos];"

    # --- AVATAR STICKER COM ENTRADA EM PULO (BOUNCE POP-IN) ---
    # Redimensionar o sticker para 760x760 mantendo proporção
    "[0:v]scale=780:780[sticker];"
    # Animação de subida suave aos 0.1s - 0.45s:
    # y entra subindo de baixo da tela (y=H) até y=H-820 com leve amortecimento
    "[v_textos][sticker]overlay=x=(W-w)/2:y='if(lt(t,0.1), H+100, if(lt(t,0.45), H - ((t-0.1)/0.35)*(w+120), H-820))'[v_final]"
)

cmd = [
    "ffmpeg", "-y",
    "-i", sticker_png,
    "-i", audio_wav,
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

print("Renderizando vídeo vertical para YouTube Shorts / TikTok...")
res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
if res.returncode == 0 and os.path.exists(out_video):
    size = os.path.getsize(out_video)
    print(f"SUCESSO TOTAL! Vídeo Shorts gerado: {size} bytes em {out_video}")
else:
    print("ERRO:", res.stderr[-600:])
