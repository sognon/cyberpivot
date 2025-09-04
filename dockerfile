FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_PORT=8501 \
    CYBERPIVOT_DEV_MODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
      libfreetype6 \
      libjpeg62-turbo \
      curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN useradd -ms /bin/bash appuser
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app
RUN mkdir -p /app/data && chown -R appuser:appuser /app
USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app_cyberpivot.py", "--server.address=0.0.0.0", "--server.port=8501"]

