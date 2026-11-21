import urllib.request
import ssl

print("Testando canais no relay 200.77.176.130...")
for i in range(1, 20):
    u = f"http://200.77.176.130:8000/udp/224.0.0.{i}:49152"
    try:
        with urllib.request.urlopen(u, timeout=1.5) as resp:
            if resp.status == 200:
                chunk = resp.read(256)
                if len(chunk) > 0 and chunk[0] == 0x47:
                    print(f"  [CANAL MPEG-TS VIVO] 224.0.0.{i} ({len(chunk)} bytes)")
    except Exception:
        pass
