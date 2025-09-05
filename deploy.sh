#!/usr/bin/env bash
set -e

# ========= CONFIG =========
REPO_SSH="git@github.com:sognon/cyberpivot.git"
BRANCH="main"
APP_MODULE="app_cyberpivot"     # ton fichier principal est 'app_cyberpivot.py' à la racine
BOOTSTRAP_SH="bootstrap.sh"     # renomme si nécessaire (ex: bootstrap2.sh)

echo "➡️  Déploiement CyberPivot™ → $REPO_SSH ($BRANCH)"

# 0) Aller à la racine du repo (même depuis un sous-dossier)
cd "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# 1) Vérifier/installer la clé SSH (si pas déjà faite)
if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
  echo "🔑 Génération d'une clé SSH (ed25519)"
  ssh-keygen -t ed25519 -C "ton_email_github" -N "" -f "$HOME/.ssh/id_ed25519"
  eval "$(ssh-agent -s)"
  ssh-add "$HOME/.ssh/id_ed25519"
  echo "👉 Copie la clé publique suivante dans GitHub (Settings → SSH and GPG keys → New SSH key) :"
  echo "--------------------------------------------------------------------------"
  cat "$HOME/.ssh/id_ed25519.pub"
  echo "--------------------------------------------------------------------------"
  read -p "Appuie sur Entrée après avoir ajouté la clé sur GitHub… " _
else
  eval "$(ssh-agent -s)" >/dev/null
  ssh-add "$HOME/.ssh/id_ed25519" >/dev/null 2>&1 || true
fi

# 2) Config remote en SSH
if git remote | grep -q "^origin$"; then
  git remote set-url origin "$REPO_SSH"
else
  git remote add origin "$REPO_SSH"
fi

# 3) Créer/écraser main.py (entrypoint Streamlit)
cat > main.py <<PY
# main.py — Entrée Streamlit : lance $BOOTSTRAP_SH puis l'app $APP_MODULE.py
import os, subprocess
from pathlib import Path
import importlib
import streamlit as st

st.set_page_config(page_title="CyberPivot™", page_icon="🛡️", layout="wide")

# 1) Bootstrap (optionnel) — exécuter le script shell et afficher les logs
script = Path(__file__).parent / "$BOOTSTRAP_SH"
if script.exists():
    try:
        os.chmod(script, 0o755)
    except Exception:
        pass
    res = subprocess.run(["/bin/bash", str(script)], capture_output=True, text=True)
    with st.expander("Logs $BOOTSTRAP_SH", expanded=False):
        st.code(res.stdout or "(no stdout)")
        if res.stderr:
            st.code("STDERR:\\n" + res.stderr)
    if res.returncode != 0:
        st.error("$BOOTSTRAP_SH a échoué — mets les 'pip' dans requirements.txt, les 'apt' dans packages.txt, et les secrets dans Settings → Secrets.")
        st.stop()
else:
    st.caption("$BOOTSTRAP_SH introuvable (ok si tout est déjà prêt).")

# 2) Importer et lancer l'app principale
mod = importlib.import_module("$APP_MODULE")
if hasattr(mod, "main") and callable(mod.main):
    mod.main()
PY

# 4) S'assurer des dépendances minimales
touch requirements.txt
grep -q "^streamlit" requirements.txt || echo "streamlit" >> requirements.txt
grep -q "^requests"  requirements.txt || echo "requests"  >> requirements.txt

# 5) (Optionnel) Paquets système apt à installer côté Cloud
# Si ton bootstrap faisait 'apt-get install ...', liste-les (1 par ligne) dans packages.txt :
# touch packages.txt
# echo "graphviz" >> packages.txt

# 6) Commit & push
git checkout -B "$BRANCH"
git add -A
git commit -m "Deploy: entrypoint main.py (bootstrap + $APP_MODULE) & deps" || echo "ℹ️ Rien à committer."
git push --force --set-upstream origin "$BRANCH"

echo
echo "✅ Code poussé sur $REPO_SSH ($BRANCH)."
echo "➡️  Étapes Streamlit Cloud (après suppression de l'ancienne app) :"
echo "    1) Ouvre https://share.streamlit.io/"
echo "    2) Clique 'New app'"
echo "    3) Repo : sognon/cyberpivot  •  Branch : $BRANCH"
echo "    4) Main file path : main.py"
echo "    5) Deploy"
echo
echo "🌐 URL publique attendue : https://cyberpivot.streamlit.app/"
echo "💡 Dans l'app, menu ≡ → 'Clear cache' puis 'Rerun' si tu vois encore un ancien rendu."



