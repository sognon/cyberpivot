#!/usr/bin/env bash
set -e

# === CONFIG ===
REMOTE_URL="https://github.com/sognon/cyberpivot.git"
DEFAULT_BRANCH="main"     # change en "master" si ton Streamlit déploie sur master
COMMIT_MSG="${1:-Deploy: mise à jour CyberPivot locale}"

echo "➡️  Déploiement CyberPivot : écrasement du dépôt distant avec la version locale"
echo "   Remote: $REMOTE_URL"

# 1) Aller à la racine du repo (même si on part d'un sous-dossier)
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# 2) Initialiser Git si besoin
if [ ! -d .git ]; then
  echo "🔧 Repo non initialisé -> git init"
  git init
fi

# 3) Déterminer/normaliser la branche locale
LOCAL_BRANCH="$(git symbolic-ref --short HEAD 2>/dev/null || true)"
if [ -z "$LOCAL_BRANCH" ]; then
  echo "🔧 Pas de branche active -> création $DEFAULT_BRANCH"
  git checkout -B "$DEFAULT_BRANCH"
  LOCAL_BRANCH="$DEFAULT_BRANCH"
fi

# 4) Configurer origin
if git remote | grep -q "^origin$"; then
  git remote set-url origin "$REMOTE_URL"
else
  git remote add origin "$REMOTE_URL"
fi

# 5) S’assurer d’être sur la bonne branche (DEFAULT_BRANCH)
if [ "$LOCAL_BRANCH" != "$DEFAULT_BRANCH" ]; then
  echo "🔁 Bascule vers la branche $DEFAULT_BRANCH"
  git checkout -B "$DEFAULT_BRANCH"
fi

# 6) Commit local (même si rien n’a chang

