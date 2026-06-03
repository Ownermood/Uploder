# ════════════════════════════════════════════════════════════════════════
#  🦅 GOLDEN EAGLE BOT — ULTIMATE EDITION
#  Works on: Render (web service) + Heroku (container worker)
# ════════════════════════════════════════════════════════════════════════
FROM python:3.12-slim-bookworm

# No .pyc files, unbuffered logs, sensible defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

WORKDIR /app

# ── System packages ──────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        aria2 \
        wget \
        curl \
        unzip \
        gcc \
        g++ \
        cmake \
        make \
        libssl-dev \
        ca-certificates \
        supervisor \
    && rm -rf /var/lib/apt/lists/*

# ── Bento4 (mp4decrypt — required for DRM) ──────────────────────────────
RUN wget -q https://github.com/axiomatic-systems/Bento4/archive/v1.6.0-639.zip \
    && unzip -q v1.6.0-639.zip \
    && cd Bento4-1.6.0-639 \
    && mkdir build && cd build \
    && cmake .. -DCMAKE_BUILD_TYPE=Release \
    && make -j$(nproc) \
    && cp mp4decrypt /usr/local/bin/ \
    && cd ../.. \
    && rm -rf Bento4-1.6.0-639 v1.6.0-639.zip

# ── Python dependencies ──────────────────────────────────────────────────
COPY sainibots.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r sainibots.txt \
    && pip install -U yt-dlp psutil

# ── Application files ────────────────────────────────────────────────────
COPY . .
RUN mkdir -p downloads /var/log/supervisor

# ── Supervisor config ────────────────────────────────────────────────────
# On RENDER  → CMD below runs supervisord (Flask health page + bot together)
# On HEROKU  → heroku.yml overrides CMD to just: python3 modules/main.py
#              (worker dyno — no web server needed)
RUN cat > /etc/supervisor/conf.d/golden_eagle.conf << 'EOF'
[supervisord]
nodaemon=true
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid

[program:flask]
command=gunicorn app:app --bind 0.0.0.0:%(ENV_PORT)s --workers 1 --timeout 120
directory=/app
autostart=true
autorestart=true
startretries=5
stderr_logfile=/var/log/supervisor/flask.err.log
stdout_logfile=/var/log/supervisor/flask.out.log
environment=PORT="%(ENV_PORT)s"

[program:bot]
command=python3 modules/main.py
directory=/app
autostart=true
autorestart=true
startsecs=5
startretries=999
stderr_logfile=/var/log/supervisor/bot.err.log
stdout_logfile=/var/log/supervisor/bot.out.log
EOF

# Supervisor needs PORT from environment at runtime — wrap CMD in shell
# so %(ENV_PORT)s picks up the Render-injected PORT at container start
EXPOSE 8080

CMD ["supervisord", "-c", "/etc/supervisor/supervisord.conf"]
