import os
import sys

def test_lipsync():
    try:
        from gradio_client import Client, handle_file
    except ImportError:
        print("gradio_client ainda não está disponível.")
        return

    print("Conectando ao espaço de sincronização labial (Wav2Lip)...")
    client = Client("manavisrani07/gradio-lipsync-wav2lip")
    
    img_path = r"C:\Users\jonas\Desktop\JONAS_FEIRA_COCO.jpg"
    audio_path = r"C:\Users\jonas\Desktop\AUDIO_JONAS_OFICIAL.wav"
    
    print(f"Enviando imagem ({img_path}) e áudio ({audio_path})...")
    result = client.predict(
        video=handle_file(img_path),
        audio=handle_file(audio_path),
        checkpoint="wav2lip_gan",
        no_smooth=0,
        resize_factor=10,
        pad_top=0,
        pad_bottom=0,
        pad_left=1,
        api_name="/generate"
    )
    print("Resultado recebido:", result)

if __name__ == "__main__":
    test_lipsync()
