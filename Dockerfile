FROM python:3.12-slim

WORKDIR /app

COPY docs/ /app/docs/
COPY ECOSSISTEMA_STREAMING_IPTV/servidor_streaming_local.py /app/servidor_streaming_local.py

RUN mkdir -p /app/vip_privado && chmod -R 777 /app/vip_privado

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860 \
    CINEPRO_MODO=VIP_DOCKER \
    CINEPRO_STATIC_DIR=/app/docs \
    CINEPRO_VIP_DIR=/app/vip_privado

EXPOSE 7860 8090

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT','7860') + '/healthz', timeout=3)"

CMD ["python", "/app/servidor_streaming_local.py"]
