#!/usr/bin/env bash
set -euo pipefail

# ---- Dépendances système minimales (si venv indisponible) ----
# Sur Kali/Debian/Ubuntu il faut le module venv :
if ! python3 -c "import venv" >/dev/null 2>&1; then
  echo "[BOOTSTRAP] Le module venv n'est pas installé. Installation (sudo requise)…"
  if command -v apt >/dev/null 2>&1; then
    # Essaie d'installer le paquet venv (nom générique)
    sudo apt update
    sudo apt install -y python3-venv
  else
    echo "[BOOTSTRAP] Installe manuellement le module venv pour Python (ex: apt install python3-venv)."
    exit 1
  fi
fi

echo "[BOOTSTRAP] Création des dossiers…"
mkdir -p standards evidences reports uploads

# ---- Création/activation du virtualenv local .venv ----
if [ ! -d ".venv" ]; then
  echo "[BOOTSTRAP] Création du virtualenv local (.venv)…"
  python3 -m venv .venv
fi

# Utilise le pip du venv
VENV_PY=".venv/bin/python"
VENV_PIP=".venv/bin/pip"

echo "[BOOTSTRAP] Mise à jour de pip dans le venv…"
$VENV_PY -m pip install --upgrade pip

echo "[BOOTSTRAP] Installation des dépendances dans le venv…"
$VENV_PIP install -r requirements.txt

echo "[BOOTSTRAP] Initialisation DB & comptes…"
$VENV_PY - <<'PY'
import auth
from app_cyberpivot import init_app_db
init_app_db()
auth.init_auth_db()
print("[BOOTSTRAP] DB initialisée. Admin par défaut : admin@cyberpivot.local / admin123")
PY

echo "[BOOTSTRAP] Terminé ✅"

