FROM python:3.12.4-slim-bookworm

WORKDIR /app

COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY clip_extractor/* /usr/local/bin/
RUN chmod +x /usr/local/bin/clip_extract*

COPY clip_studio_webhook.py .

CMD ["python", "clip_studio_webhook.py"]