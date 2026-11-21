import subprocess
import os

def check_video():
    url = "https://www.youtube.com/shorts/gAmDxYVvwLM"
    out_dir = r"C:\Users\jonas\Downloads\projeto de estudo\yt_check"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, "short_info.json")
    
    cmd = [
        "yt-dlp",
        "--dump-json",
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if res.returncode == 0:
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(res.stdout)
            print("INFO DUMPED SUCCESSFULLY")
        else:
            print("ERRO:", res.stderr[:300])
    except Exception as e:
        print("EXC:", e)

if __name__ == "__main__":
    check_video()
