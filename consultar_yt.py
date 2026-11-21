import urllib.request
import re

url = "https://www.youtube.com/shorts/gAmDxYVvwLM"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="ignore")
        title_match = re.search(r"<title>(.*?)</title>", html)
        desc_match = re.search(r'"description":\{"simpleText":"(.*?)"\}', html)
        video_id = re.search(r'"videoId":"(.*?)"', html)
        print("TITLE:", title_match.group(1) if title_match else "Não encontrado")
        print("DESC:", desc_match.group(1) if desc_match else "Não encontrada")
        
        # Procurar por trechos de legenda ou palavras-chave
        keywords = re.findall(r'"keywords":\[(.*?)\]', html)
        print("KEYWORDS:", keywords[:3] if keywords else "Nenhuma")
except Exception as e:
    print("ERRO:", e)
