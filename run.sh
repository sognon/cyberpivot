#!/usr/bin/env bash
set -euo pipefail

export CYBERPIVOT_DB="${CYBERPIVOT_DB:-$(pwd)/cyberpivot.db}"
echo "[RUN] DB: $CYBERPIVOT_DB"

# Si un autre streamlit tourne déjà sur 8501, utilise 8502
PORT="${PORT:-8501}"
if lsof -i :"$PORT" >/dev/null 2>&1; then
  PORT=8502
fi
echo "[RUN] Port: $PORT"

streamlit run app_cyberpivot.py --server.port "$PORT" --server.runOnSave true

