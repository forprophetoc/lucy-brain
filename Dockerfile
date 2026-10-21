# EstiClose brain (hc_compose_service) on Fly.io — Muse backend.
# Slim runtime: deps are pytz + anthropic only (render-build.sh's Claude CLI is a Render
# artifact, not needed here). The service binds HC_HOST/HC_PORT and serves GET /health.
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV HC_HOST=0.0.0.0 \
    HC_PORT=8080

EXPOSE 8080

CMD ["python", "hc_compose_service.py"]
