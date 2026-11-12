import urllib.request

u = "http://rtv30t.com:80/Wintvx/Wtv1020/71874.ts"
req = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0"})
data = b""
with urllib.request.urlopen(req, timeout=5) as resp:
    data = resp.read(188 * 500) # Ler 500 pacotes TS

print("Total de dados lidos:", len(data))
# Cada pacote TS tem 188 bytes e comeca com 0x47
packets = [data[i:i+188] for i in range(0, len(data), 188) if len(data[i:i+188]) == 188 and data[i] == 0x47]
print("Total de pacotes TS validos:", len(packets))

pids = set()
for p in packets:
    pid = ((p[1] & 0x1F) << 8) | p[2]
    pids.add(pid)
print("PIDs encontrados:", pids)

# Procurar PAT (PID 0)
pat_packet = next((p for p in packets if (((p[1] & 0x1F) << 8) | p[2]) == 0), None)
if pat_packet:
    print("PAT encontrado!")
    # O ponteiro de payload está no byte 4
    pointer = pat_packet[4]
    pat_data = pat_packet[5 + pointer:]
    pmt_pid = ((pat_data[10] & 0x1F) << 8) | pat_data[11]
    print("PMT PID:", pmt_pid)
    
    # Procurar PMT
    pmt_packet = next((p for p in packets if (((p[1] & 0x1F) << 8) | p[2]) == pmt_pid), None)
    if pmt_packet:
        print("PMT encontrado!")
        pointer_pmt = pmt_packet[4]
        pmt_data = pmt_packet[5 + pointer_pmt:]
        section_length = ((pmt_data[1] & 0x0F) << 8) | pmt_data[2]
        program_info_length = ((pmt_data[10] & 0x0F) << 8) | pmt_data[11]
        
        streams_data = pmt_data[12 + program_info_length : 3 + section_length - 4]
        idx = 0
        while idx < len(streams_data):
            st_type = streams_data[idx]
            elem_pid = ((streams_data[idx+1] & 0x1F) << 8) | streams_data[idx+2]
            es_info_len = ((streams_data[idx+3] & 0x0F) << 8) | streams_data[idx+4]
            
            tipo_nome = "Desconhecido"
            if st_type == 0x1B: tipo_nome = "H.264 / AVC (Compatível 100% com Chrome)"
            elif st_type == 0x24: tipo_nome = "H.265 / HEVC"
            elif st_type == 0x02: tipo_nome = "MPEG-2 Video"
            elif st_type == 0x0F: tipo_nome = "AAC Audio (Compatível 100% com Chrome)"
            elif st_type == 0x03 or st_type == 0x04: tipo_nome = "MP3 Audio"
            elif st_type == 0x81: tipo_nome = "AC-3 / Dolby Audio"
            
            print(f"-> Stream Type: 0x{st_type:02X} ({tipo_nome}), PID: {elem_pid}")
            idx += 5 + es_info_len
