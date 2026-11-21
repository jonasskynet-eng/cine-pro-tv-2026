import subprocess
import os

video_path = r"C:\Users\jonas\.gemini\antigravity\brain\d405b632-b181-41d9-92e9-360e6672e46d\.user_uploaded\media_1795051919804_a444b6ca.mp4"
out_img = r"C:\Users\jonas\.gemini\antigravity\brain\d405b632-b181-41d9-92e9-360e6672e46d\rosto_real_jonas.jpg"

cmd = [
    "ffmpeg", "-y",
    "-i", video_path,
    "-ss", "00:00:01",
    "-vframes", "1",
    "-q:v", "2",
    out_img
]

try:
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    if os.path.exists(out_img):
        print(f"SUCESSO: {os.path.getsize(out_img)} bytes")
    else:
        print("ERRO: Nao criou o arquivo")
except Exception as e:
    print("EXCECAO:", e)
