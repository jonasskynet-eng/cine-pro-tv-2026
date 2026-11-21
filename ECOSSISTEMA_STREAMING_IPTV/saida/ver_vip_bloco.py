with open(r'c:\Users\jonas\Downloads\projeto de estudo\ECOSSISTEMA_STREAMING_IPTV\atualizar_central_pro.py', 'r', encoding='utf-8') as f:
    c = f.read()

idx = c.find('canais_vip_fibra = [')
print(c[idx:idx+800])
